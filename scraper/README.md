# PJA-RAG scraper

This is a simple web scraper that uses selenium to scrape `https://pja.mykhi.org/` for the data. The data is then stored in a qdrant vector database.

## Installation

1. Install the required packages using pip (you need to be in root directory of the project):
```bash
pip install -r requirements.txt
```
2. Run the scraper:
```bash
make scrape_data
```

or 

insert scraped data into qdrant:
```bash
make insert_data
```

* You need to setup .env or `scraper/config.py` file with qdrant credentials and `DATA_DIRECTORY`.
* PDF parser won't work without tesseract installed on your machine. You can install it from [here](https://github.com/UB-Mannheim/tesseract/wiki).


# TODO

- Better way to scrape data (something like structures for sites)