import React, { useState } from 'react';
import { sendQuery } from '../services/api';

function QueryInput({ setResult, setLoading }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const data = await sendQuery(question);
      setResult(data);
    } catch (error) {
      console.error('Erro ao consultar:', error);
      setResult({
        answer: 'Erro ao processar sua consulta. Tente novamente.',
        sources: []
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Faça sua pergunta aqui..."
        required
      />
      <button type="submit">Consultar</button>
    </form>
  );
}

export default QueryInput;
