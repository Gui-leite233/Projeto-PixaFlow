import React from "react";

function ResultDisplay({ result }) {
  if (!result) return null;

  return (
    <div className="result">
      <div
        style={{
          display: "inline-block",
          padding: "5px 15px",
          borderRadius: "20px",
          backgroundColor: "#2196F3",
          color: "white",
          fontSize: "12px",
          fontWeight: "bold",
          marginBottom: "15px",
        }}
      >
        🤖 RAG Knowledge Base
      </div>

      <h2>Resposta:</h2>
      <p style={{ whiteSpace: "pre-line" }}>{result.answer}</p>

      {result.sources && result.sources.length > 0 && (
        <>
          <h3>Fontes Consultadas ({result.sources.length}):</h3>
          <ul>
            {result.sources.map((source, index) => (
              <li key={index}>{source}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default ResultDisplay;
