# Tworzenie systemów RAG

## Wprowadzenie

RAG (Retrieval Augmented Generation) to rodzaj systemu, który łączy generację tekstu z wyszukiwaniem informacji. W tym repozytorium znajdziesz dokładny opis tego, jak stworzyć taki system, bez użycia LangChaina/StreamLita.

Należy rozpocząć od scrapowania i czyszczenia danych, nie będę się rozwodził nad scrapowaniem, bo to zbyt indywidualny proces. W tym repozytorium znajdziesz kod, który scrapuje pliki z [serwera PJA](https://pja.mykhi.org/).

### Parsowanie danych

Następnie należy przetworzyć dane, skupmy się nad plikami PDF.
Do przetworzenia osobiście korzystałem z `pdfplumber`, ale `PyMuPDF` lub jakakolwiek inna biblioteka do obsługi PDFów wystarczy.
Warto wykorzystać [Factory](https://refactoring.guru/design-patterns/factory-method), aby móc zaimplementować wiele różnych sposobów przetwarzania różnych typów plików.

```py
class PdfParser(BaseParser):
    def parse(self, filepath: str):
        with pdfplumber.open(filepath) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages])
            return content
```
Jedyne zadanie parsera to wyciągnięcie tekstu z pliku, warto także zapisac sciezke do pliku, jego nazwę i metadane.

```py
@dataclass
class ParsedData:
    content: str
    filename: str
    path: str
    metadata: dict

class PdfParser(BaseParser):
    def parse(self, filepath: str):
        with pdfplumber.open(filepath) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages])
            metadata = pdf.metadata
        return ParsedData(content, filepath.split("/")[-1], filepath, metadata)
```

### Qdrant

Gdy mamy zaimplementowaną logikę scrapowania i parsowania plików, należy je umieścić w wektorowej bazie danych. Wektorowe bazy danych pozwalają na szybkie wyszukiwanie podobnych wektorów, co jest kluczowe w systemach RAG.
Da nam to łatwy dostęp do dokumentów, bazując na query, które wprowadzi użytkownik, tzw. "semantic search".

Qdrant ma wersje Cloud, która jest darmowa do pewnego momentu, można też postawić własną instancję z użyciem Dockera.

```sh
docker run -d -p 6333:6333 -v /path/to/index:/qdrant/index qdrant/qdrant:latest
```

Następnie, należy zaimplementować logikę dodawania dokumentów do bazy danych. Pliki PDF sa parsowane, a następnie przy użyciu SentenceTransformers zamieniane na wektory.
Warto także zmienić długie teksty na kilka krótszych (chunkowanie), aby móc łatwiej wyszukiwać konkretne informacje.

Implementacja funkcji do zamiany tekstu na wektory oraz chunkowania:

```py
from sentence_transformers import SentenceTransformer
import torch


model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cuda" if torch.cuda.is_available() else "cpu",
)

def convert_to_vector(text: str) -> List[float]:
    vectors = model.encode(text, show_progress_bar=False)
    return vectors

def chunk_text(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks = [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return chunks
```

Wstępna funkcja do dodawania dokumentów do bazy danych polega na przeiterowaniu przez zapisane pliki, przetworzeniu ich przez wcześniej utworzony parser, zamienieniu kontentu na wektory i dodaniu ich do bazy danych.

```py
def process_file(root, file):
    filepath = os.path.join(root, file)
    try:
        # Factory parsujace pliki bazujac na ich rozszerzeniu
        parser = FileParser(filepath)
        data = parser.parse()
    except Exception as e:
        print(f"Failed to parse file: {file}, error: {e}")
        return

    chunks = chunk_text(data.content)
    for chunk in chunks:
        id_ = uuid.uuid4().hex

        yield {
            "id": id_,
            "content": chunk,
            "metadata": {
                "filename": data.filename,
                "path": data.path,
                "metadata": data.metadata,
            },
        }


def process_files(qdrant_client: QdrantClient):
    directory = os.walk(config.DATA_DIRECTORY)
    points = []

    for root, _, files in directory:
        for file in files:
            payload = process_file(root, file)
            for payload in payload:
                points.append(payload)

    # Add samo w sobie zamienia dokumenty na wektory i dodaje je do bazy danych
    # Performance nie jest najlepszy, ale nie ma za bardzo znaczenia ze wzgledu na dodawanie 
    # dokumentow PRZED implementacja API
    qdrant_client.add(
        collection_name=config.QDRANT_COLLECTION_NAME,
        ids=[point["id"] for point in points],
        documents=[point["content"] for point in points],
        metadata=[point["metadata"] for point in points],
    )
```

### API

Skoro parsowanie tekstu mamy już ogarnięte, należy zaimplementować API, które będzie działać jako proxy do Ollamy i Qdranta.

Najważniejszą częścią - sercem RAG - jest generowanie query, reszta implementacji nie ma znaczenia i może być dostosowana pod konkretne potrzeby.
Do generowania query należy:
1. Dostać konkretny prompt od użytkownika
2. Wysłać go do Qdranta, dostać w odpowiedzi listę dokumentów/chunków, które pasują do query
3. Utworzyć "finalny" prompt, który będzie zawierał prompt użytkownika oraz znalezione dokumenty jako kontekst
4. Wysłać finalny prompt do Ollamy, dostać w odpowiedzi wygenerowany tekst

Warto pamiętać, że jest to element logiki biznesowej. W zależności od potrzeb, można dodać różne warunki, które będą decydować, jakie dokumenty będą brane pod uwagę, jakie będą brane pod uwagę fragmenty dokumentów, jakie będą brane pod uwagę metadane dokumentów itp.

```py
client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY)


def process_retrieval(query: str) -> str:
    search_result = search(query=query)
    resulting_query: str = (
        f"Answer based only on the context, nothing else. \n"
        f"QUERY:\n{query}\n"
        f"CONTEXT:\n{search_result}"
    )
    logger.info(f"Resulting Query: {resulting_query}")
    return resulting_query


def search(query: str) -> str:
    # Query samo w sobie zamienia test na wektor, a następnie wyszukuje podobne wektory w bazie danych
    search_result = client.query(
        collection_name=settings.QDRANT_COLLECTION_NAME, limit=3, query_text=query
    )
    if not search_result:
        raise RetrievalNoDocumentsFoundException  # Własny wyjątek, który obsługuje brak dokumentów
    return "\n".join(result.document for result in search_result)
```