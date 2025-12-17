const API_URL = 'http://localhost:8000/api/v1';

export const sendQuery = async (question) => {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });
  
  if (!response.ok) {
    throw new Error('Erro ao consultar a API');
  }
  
  return response.json();
};

export const addDocument = async (title, content) => {
  const response = await fetch(`${API_URL}/documents`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, content }),
  });
  
  if (!response.ok) {
    throw new Error('Erro ao adicionar documento');
  }
  
  return response.json();
};

export const getQueries = async () => {
  const response = await fetch(`${API_URL}/queries`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar consultas');
  }
  
  return response.json();
};
