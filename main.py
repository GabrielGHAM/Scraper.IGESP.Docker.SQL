import os
from modulos.scraping import get_tables_data
from modulos.database import Tabela
from modulos.connections import db_connect
from dotenv import load_dotenv



if __name__ == '__main__':
    load_dotenv()
    path = '/app/planilhas'
    print('lido')
    if not os.path.exists(path):
        os.makedirs(path)
        
    connection = db_connect()
    try:
        data = get_tables_data()
        tabela = Tabela()
        tabela.create_or_truncate_table(connection)
        for name, df in data.items():
            filename = name.replace(' ', '_').lower() + '.csv'
            # Caminho completo do arquivo CSV
            filepath = os.path.join(path, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f'O arquivo {filename} foi salvo localmente!')

            try:
                # Inserir os dados no banco de dados
                tabela.insert_data_to_database(df, connection)
                print(f'Dados da {name} inseridos no banco de dados!')
            except Exception as e:
                print(f'Ocorreu um erro ao inserir os dados da {name} no banco de dados:', e)
    finally:
        connection.close()
