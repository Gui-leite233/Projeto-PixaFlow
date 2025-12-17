import React from 'react';

function ResultDisplay({ result }) {
  if (!result) return null;

  return (
    <div className="result">
      <h2>Resposta:</h2>
      <p>{result.answer}</p>
      
      {result.sources && result.sources.length > 0 && (
        <>
          <h3>Fontes Consultadas:</h3>
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
