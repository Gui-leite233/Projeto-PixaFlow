import React, { useState } from 'react';
import QueryInput from './components/QueryInput';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="App">
      <header>
        <h1>Sistema RAG - Pixaflow</h1>
        <p>Consulta Inteligente com IA</p>
      </header>
      <main>
        <QueryInput setResult={setResult} setLoading={setLoading} />
        {loading && <div className="loading">Processando sua consulta...</div>}
        {result && <ResultDisplay result={result} />}
      </main>
    </div>
  );
}

export default App;
