import React, { useEffect } from "react";
import ChatContainer from "./components/ChatContainer";

function App(): JSX.Element {
  useEffect(() => {
    document.title = "PJA-RAG"
  }, [])
  return (
    <div className="App">
      <ChatContainer />
    </div>
  );
}

export default App;
