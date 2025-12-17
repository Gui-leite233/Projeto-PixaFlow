import React, { useState } from "react";
import "./App.css";
import { sendQuery } from "./services/api";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { type: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendQuery(input);
      const botMessage = {
        type: "bot",
        text: data.answer,
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: "bot",
        text: "Desculpe, ocorreu um erro ao processar sua mensagem.",
        error: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <header className="chat-header">
          <div className="header-content">
            <div className="logo">🤖</div>
            <div>
              <h1>Pixaflow AI Assistant</h1>
              <p>Sistema RAG com ChromaDB</p>
            </div>
          </div>
        </header>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>👋 Bem-vindo!</h2>
              <p>
                Pergunte sobre o estoque, vendas ou qualquer informação do
                sistema.
              </p>
              <div className="suggestion-chips">
                <button onClick={() => setInput("Quanto custa o tomate?")}>
                  💰 Preços
                </button>
                <button
                  onClick={() => setInput("Quantos produtos tem no estoque?")}
                >
                  📦 Estoque
                </button>
                <button onClick={() => setInput("Mostre as vendas recentes")}>
                  📊 Vendas
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.type}`}>
              <div className="message-avatar">
                {msg.type === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content">
                <div className={`message-bubble ${msg.error ? "error" : ""}`}>
                  {msg.text}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <details>
                      <summary>📚 {msg.sources.length} fonte(s)</summary>
                      <ul>
                        {msg.sources.map((source, i) => (
                          <li key={i}>{source}</li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message bot">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-bubble loading-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? "⏳" : "➤"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
