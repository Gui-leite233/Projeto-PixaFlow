from sqlalchemy import text
from app.database import SessionLocal

class SQLAIService:
    def __init__(self):
        print("✅ SQL AI Service inicializado!")
    
    def process_query(self, question: str):
        """Processa pergunta em linguagem natural e consulta o banco"""
        db = SessionLocal()
        
        try:
            print(f"🔍 Processando: {question}")
            
            # Converte pergunta em SQL
            sql_query = self._question_to_sql(question)
            
            if not sql_query:
                return {
                    "answer": "Desculpe, não entendi sua pergunta. Tente perguntas como: 'Quantos alfaces tem no estoque?' ou 'Qual o total de vendas?'",
                    "sql": None,
                    "data": []
                }
            
            # Executa query
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Gera resposta em linguagem natural
            answer = self._generate_answer(question, rows, sql_query)
            
            return {
                "answer": answer,
                "sql": sql_query,
                "data": [dict(row._mapping) for row in rows] if rows else []
            }
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {
                "answer": f"Erro ao processar consulta: {str(e)}",
                "sql": None,
                "data": []
            }
        finally:
            db.close()
    
    def _question_to_sql(self, question: str):
        """Converte pergunta em SQL (versão simplificada)"""
        question_lower = question.lower()
        
        # Padrões de perguntas sobre ESTOQUE
        if any(word in question_lower for word in ["quanto", "quantos", "quantidade", "tem no estoque", "estoque"]):
            # Extrai o produto
            produtos = ["alface", "tomate", "cenoura", "batata", "cebola", "arroz", "feijão"]
            produto_encontrado = None
            
            for produto in produtos:
                if produto in question_lower:
                    produto_encontrado = produto.capitalize()
                    break
            
            if produto_encontrado:
                return f"SELECT produto, quantidade, unidade, preco FROM estoque WHERE produto = '{produto_encontrado}'"
            else:
                return "SELECT produto, quantidade, unidade FROM estoque"
        
        # Padrões de perguntas sobre VENDAS
        elif any(word in question_lower for word in ["vendas", "vendeu", "vendi", "faturamento"]):
            if "total" in question_lower:
                return "SELECT SUM(valor_total) as total_vendas, COUNT(*) as numero_vendas FROM vendas"
            elif "hoje" in question_lower:
                return "SELECT produto, quantidade, valor_total, cliente FROM vendas WHERE DATE(data_venda) = CURDATE()"
            else:
                return "SELECT produto, quantidade, valor_total, cliente, data_venda FROM vendas ORDER BY data_venda DESC LIMIT 10"
        
        # Lista todos os produtos
        elif "listar" in question_lower or "mostrar" in question_lower or "todos" in question_lower:
            if "produto" in question_lower or "estoque" in question_lower:
                return "SELECT produto, quantidade, unidade, preco, categoria FROM estoque ORDER BY produto"
        
        # Produtos em falta
        elif "falta" in question_lower or "acabando" in question_lower or "pouco" in question_lower:
            return "SELECT produto, quantidade, unidade FROM estoque WHERE quantidade < 50 ORDER BY quantidade"
        
        # Produtos mais caros
        elif "caro" in question_lower or "preço" in question_lower:
            return "SELECT produto, preco, quantidade FROM estoque ORDER BY preco DESC LIMIT 5"
        
        return None
    
    def _generate_answer(self, question: str, rows, sql_query: str):
        """Gera resposta em linguagem natural"""
        
        if not rows:
            return "Não encontrei resultados para sua consulta."
        
        question_lower = question.lower()
        
        # Respostas específicas por tipo de pergunta
        if "quanto" in question_lower or "quantos" in question_lower:
            row = rows[0]
            produto = row.produto if hasattr(row, 'produto') else row[0]
            quantidade = row.quantidade if hasattr(row, 'quantidade') else row[1]
            unidade = row.unidade if hasattr(row, 'unidade') else row[2]
            
            return f"Há {quantidade} {unidade}(s) de {produto} no estoque."
        
        elif "total" in question_lower and "vendas" in question_lower:
            row = rows[0]
            total = row.total_vendas if hasattr(row, 'total_vendas') else row[0]
            numero = row.numero_vendas if hasattr(row, 'numero_vendas') else row[1]
            
            return f"O total de vendas é R$ {total:.2f} em {numero} venda(s)."
        
        elif "listar" in question_lower or "todos" in question_lower:
            produtos_list = []
            for row in rows:
                produto = row.produto if hasattr(row, 'produto') else row[0]
                quantidade = row.quantidade if hasattr(row, 'quantidade') else row[1]
                produtos_list.append(f"• {produto}: {quantidade}")
            
            return "Produtos no estoque:\n" + "\n".join(produtos_list[:10])
        
        # Resposta genérica
        else:
            result_text = f"Encontrei {len(rows)} resultado(s):\n\n"
            for i, row in enumerate(rows[:5], 1):
                row_dict = dict(row._mapping)
                result_text += f"{i}. "
                result_text += ", ".join([f"{k}: {v}" for k, v in row_dict.items()])
                result_text += "\n"
            
            return result_text

sql_ai_service = SQLAIService()
