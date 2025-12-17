const API_URL = "http://localhost:8000/api/v1";

export const sendQuery = async (question) => {
  const response = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Erro ao consultar a API");
  }

  return response.json();
};

export const syncDatabase = async () => {
  const response = await fetch(`${API_URL}/sync-database`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Erro ao sincronizar banco");
  }

  return response.json();
};

export const addDocument = async (texts) => {
  const response = await fetch(`${API_URL}/add-documents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      texts: Array.isArray(texts) ? texts : [texts],
      metadatas: null,
    }),
  });

  if (!response.ok) {
    throw new Error("Erro ao adicionar documento");
  }

  return response.json();
};

export const getQueries = async () => {
  const response = await fetch(`${API_URL}/queries`);

  if (!response.ok) {
    throw new Error("Erro ao buscar consultas");
  }

  return response.json();
};

export const getDocumentCount = async () => {
  const response = await fetch(`${API_URL}/documents/count`);

  if (!response.ok) {
    throw new Error("Erro ao buscar contagem");
  }

  return response.json();
};
