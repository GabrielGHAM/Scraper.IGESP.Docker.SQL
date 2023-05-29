import pyodbc
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None

    def _db_connect(self):
        load_dotenv()
        server = os.getenv('SERVER')
        database = os.getenv('DATABASE')
        username = os.getenv('UID')
        password = os.getenv('MSSQL_SA_PASSWORD')
        connection_data = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
        try:
            return pyodbc.connect(connection_data)
        except pyodbc.Error as e:
            print(f"Error connecting to SQL Server: {e}")
            return None

    def _get_connection(self):
        if self.connection is None:
            self.connection = self._db_connect()
            self.cursor = self.connection.cursor()  # Criar o cursor após estabelecer a conexão
        return self.connection    

    def create_table(self, table_name, table_columns):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            connection.autocommit = True
            database_name = os.getenv('DB_NAME')
            cursor.execute(f"USE {database_name}")
            cursor.execute(f"IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}') SELECT 1 ELSE SELECT 0")
            table_exists = cursor.fetchone()[0] == 1

            if not table_exists:
                column_definitions = ", ".join(table_columns)
                create_table_query = f"CREATE TABLE {table_name} ({column_definitions})"
                cursor.execute(create_table_query)
                print(f"Tabela {table_name} criada com sucesso!")

            connection.commit()
        except Exception as e:
            print(f"Erro ao criar tabela: {str(e)}")

    def create_database(self):
        try:
            connection = self._get_connection()
            database_name = os.getenv('DB_NAME')
            cursor = connection.cursor()
            connection.autocommit = True
            cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{database_name}'")
            database_exists = cursor.fetchone()[0] == 1

            if not database_exists:
                connection.autocommit = True
                cursor.execute(f"CREATE DATABASE {database_name}")
                print(f"Banco de dados {database_name} criado com sucesso!")
                connection.autocommit = False

            cursor.execute(f"USE {database_name}")
            connection.commit()
        except Exception as e:
            print(f"Erro ao criar banco de dados: {str(e)}")

    def truncate_table(self, table_name):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(f"IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}') SELECT 1 ELSE SELECT 0")
            table_exists = cursor.fetchone()[0] == 1

            if table_exists:
                cursor.execute(f"TRUNCATE TABLE {table_name}")
                print(f"Tabela {table_name} truncada com sucesso!")
            connection.commit()
        except Exception as e:
            print(f"Erro ao truncar tabela: {str(e)}")

    def insert_data(self, table_name, values, columns):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Verificar se a tabela existe
            cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0")
            table_exists = cursor.fetchone()[0] == 1

            if not table_exists:
                print(f"Tabela {table_name} não existe!")
                # Criar tabela caso não exista
                # self.create_table(table_name, create_columns_log_file)

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            if isinstance(values, list) and isinstance(values[0], tuple):
                cursor.executemany(insert_query, values)
            elif isinstance(values, tuple):
                cursor.execute(insert_query, values)
            else:
                raise ValueError("Invalid values format")

        except Exception as e:
            print(f"Erro ao inserir dados: {str(e)}")


    def close_connection(self):
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
            print("Conexão com o banco de dados fechada com sucesso!")
            self.connection = None
        else:
            print("Não há conexão ativa com o banco de dados.")
