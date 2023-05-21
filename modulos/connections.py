import pyodbc
import os
from dotenv import load_dotenv

def db_connect():
    # Obter as informações do banco de dados do arquivo .env
    server = os.getenv('SERVER')
    database = os.getenv('DATABASE')
    username = os.getenv('UID')
    password = os.getenv('SA_PASSWORD')
    # Montar a string de conexão
    connection_data = (
         "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"        
    )
    print (username)
    print(connection_data)

    # Tentar estabelecer a conexão com o banco de dados
    try:
        connection = pyodbc.connect(connection_data)
        print("Conexão bem-sucedida")
        return connection
    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao conectar ao banco de dados: {e}")
        return None
