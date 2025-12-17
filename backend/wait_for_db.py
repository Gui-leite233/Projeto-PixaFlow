import time
import pymysql
import os
import sys

def wait_for_db():
    max_retries = 60
    retry_interval = 3
    
    print("🔄 Iniciando verificação do MySQL...")
    print(f"   Host: {os.getenv('MYSQL_HOST', 'mysql')}")
    print(f"   Port: {os.getenv('MYSQL_PORT', '3306')}")
    print(f"   User: {os.getenv('MYSQL_USER', 'user')}")
    print(f"   Database: {os.getenv('MYSQL_DATABASE', 'ragdb')}")
    
    for i in range(max_retries):
        try:
            connection = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'mysql'),
                user=os.getenv('MYSQL_USER', 'user'),
                password=os.getenv('MYSQL_PASSWORD', 'password'),
                database=os.getenv('MYSQL_DATABASE', 'ragdb'),
                port=int(os.getenv('MYSQL_PORT', '3306')),
                connect_timeout=10
            )
            connection.close()
            print("✅ MySQL conectado com sucesso!")
            return True
        except Exception as e:
            if i < 5 or i % 10 == 0:  # Mostra erro a cada 10 tentativas
                print(f"⏳ Tentativa {i+1}/{max_retries} - Aguardando MySQL...")
                print(f"   Erro: {str(e)[:100]}")
            time.sleep(retry_interval)
    
    print("❌ ERRO: Não foi possível conectar ao MySQL!")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
