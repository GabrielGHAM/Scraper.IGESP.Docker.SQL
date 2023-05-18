from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import concurrent.futures
import os
import tabula
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def db_connect():
    # Carregar as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Obter as informações do banco de dados do arquivo .env
    server = os.getenv('SERVER')
    database = os.getenv('DATABASE')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    # Montar a string de conexão
    connection_data = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f"Server={server};"
        f"Database={database};"
        f"UID={username};"
        f"PWD={password};"
    )

    # Tentar estabelecer a conexão com o banco de dados
    try:
        connection = pyodbc.connect(connection_data)
        print("Conexão bem-sucedida")
        return connection
    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao conectar ao banco de dados: {e}")
        return None

def make_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    return requests.get(url, headers=headers)

def tratamento_dados(df,name_table):
    new_cols = {
        'NU_PROCESSO_SEI': ['Nº Processo SEI', 'N° Processo SEI'],
        'NM_RAZAO_SOCIAL': ['Razão Social', 'Razo Social', 'Raz?o Social', 'FORNECEDOR','RAZ?O SOCIAL'],
        'NU_CPF_CNPJ': ['CNPJ/CPF', 'CNPJ'],
        'DOC_FISCAL': ['NF-e', 'DOCTO FISCAL', 'Docto Fiscal', 'DOCTO. FISCAL', 'NFE', 'NFe',' DOC. FISCAL'],
        'TX_LINK_SEI_DOC_FISCAL': ['Link', 'Link SEI do Docto. Fiscal','Link SEI do Docto. Fiscal'],
        'DT_EMISSAO': ['Dt. Emisso', 'Emissão', 'Dt. Emiss?o', 'DATA EMISÃO OU ATESTE', 'Dt. Emissão','DT. EMISS?O'],
        'DT_ATESTO': ['Atesto', 'Dt Atesto'],
        'DT_VENCIMENTO': ['Vencimento', 'Data de Vecto', 'DT de Vencimento'],
        'VL_TOTAL': ['Valor', 'Valor Total', 'VALOR'],
        'VALOR_ORIGINAL': ['Valor Original'],
        'JUROS_MULTA': ['Juros e Multa'],
        'DT_PGTO': ['Pagamento', 'Dt. Pagto', 'DATA PGTO', 'DT Pagamento'],
        'DT_RECBTO': ['Data Recbto'],
        'LOTE': ['Lote','LOTE','FORMA DE PAGTO','FORMA DE PAGAMENTO'],
        'TX_LINK_SEI_COMPROVANTE': ['Link SEI do Comprovante', 'Comprovante'],
        'NM_MODALIDADE_CONTRATUAL': ['Modalidade Contratual', 'Modalidade'],
        'NU_INSTRUMENTO_CONTRATUAL': ['Nº Instrumento', 'N? Instrumento Contratual', 'N¼ Instrumento Contratual', 'NM Instrumento', 'Nº INSTRUMENTO CONTRATUAL'],
        'TX_HISTORICO_DESPESA': ['Histórico da Despesa', 'Hist?rico da Despesa', 'HISTÓRICO DA DESPESA', 'Historico da Despesa'],
        'NM_GRUPO': ['Grupo'],
        'NM_PLANO_CONTAS': ['Plano de Contas'],
        'NM_UNIDADE': ['Unidade','Un. Saúde'],
        'DS_OBSERVACAO_PENDENCIA': ['Observa??o / Pend?ncia', 'Observação / Pendência', 'OBSERVAÇÕES', 'Observacao e Pendencia','OBSERVA??O / PEND?NCIA'],
        'COVID-19': ['COVID-19'],
        
    }

    # Criar dicionário de novos nomes para as colunas do dataframe
    new_names = {}
    try:
        for col in df.columns:
            for new_col, variations in new_cols.items():
                pattern = r'\b(?:' + '|'.join(map(re.escape, variations)) + r')\b'
                if re.fullmatch(pattern, col, re.IGNORECASE):
                    new_names[col] = new_col.upper()
                    break
            else:
                new_names[col] = col.upper()
        df = df.rename(columns=new_names)
        df = df.replace(';', ' ', regex=True)
        cols_to_keep = [col for col in df.columns if col in new_cols]
        df = df[cols_to_keep]
        # Verificar se as novas colunas existem no dataframe
        for new_col in new_cols.keys():
            if new_col.upper() not in df.columns:
                # Criar a nova coluna com o valor None
                df = df.assign(**{new_col.upper(): None})            
        df = df.dropna(how='all')
    # Substituir valores nulos restantes por "NULL"
        df = df.fillna('')
    except Exception as e:
        print(f'Erro ao tratar dados da {name_table}')
    return df


def extract_table_data(link):
    year_table = re.findall(r'\d{4}', link.get('href'))[0]
    name_table = f'{link.text} de {year_table}'

    try:
        href = link.get('href')

        if href.endswith('.pdf'):
            df = tabula.read_pdf(href, pages='all')
            df = pd.concat(df)
            df.columns = df.columns.str.replace('\r', ' ')

        else:
            df = pd.read_html(href)
            df = pd.concat(df)
            
        if df.empty:
            print(f'O dataframe {name_table} está vazio. Pulando o processamento.')
            return name_table, None

        df = tratamento_dados(df,name_table)
        return name_table, df

    except Exception as e:
        print(f'Erro ao extrair a {name_table}',e)

# Função para inserir os dados no banco de dados
def insert_data_to_database(df, connection):
    cursor = connection.cursor()

    # Verificar se a tabela já existe
    table_name = os.getenv('TB_NAME')
    cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
    table_exists = cursor.fetchone()[0] > 0

    # Se a tabela não existe, criar a tabela com as colunas especificadas
    if not table_exists:
        create_table_query = f"""
        CREATE TABLE {table_name} (
            NU_PROCESSO_SEI VARCHAR(MAX),
            NM_RAZAO_SOCIAL VARCHAR(MAX),
            NU_CPF_CNPJ VARCHAR(MAX),
            DOC_FISCAL VARCHAR(MAX),
            TX_LINK_SEI_DOC_FISCAL VARCHAR(MAX),
            DT_EMISSAO VARCHAR(MAX),
            DT_ATESTO VARCHAR(MAX),
            DT_VENCIMENTO VARCHAR(MAX),
            VL_TOTAL VARCHAR(MAX),
            VALOR_ORIGINAL VARCHAR(MAX),
            JUROS_MULTA VARCHAR(MAX),
            DT_PGTO VARCHAR(MAX),
            DT_RECBTO VARCHAR(MAX),
            LOTE VARCHAR(MAX),
            TX_LINK_SEI_COMPROVANTE VARCHAR(MAX),
            NM_MODALIDADE_CONTRATUAL VARCHAR(MAX),
            NU_INSTRUMENTO_CONTRATUAL VARCHAR(MAX),
            TX_HISTORICO_DESPESA VARCHAR(MAX),
            NM_GRUPO VARCHAR(MAX),
            NM_PLANO_CONTAS VARCHAR(MAX),
            NM_UNIDADE VARCHAR(MAX),
            DS_OBSERVACAO_PENDENCIA VARCHAR(MAX),
            [COVID-19] VARCHAR(MAX)
        )
        """
        cursor.execute(create_table_query)
        print(f"Tabela {table_name} criada com sucesso!")

    # Especifique a ordem das colunas na tabela do banco de dados
    columns_order = [
        'NU_PROCESSO_SEI',
        'NM_RAZAO_SOCIAL',
        'NU_CPF_CNPJ',
        'DOC_FISCAL',
        'TX_LINK_SEI_DOC_FISCAL',
        'DT_EMISSAO',
        'DT_ATESTO',
        'DT_VENCIMENTO',
        'VL_TOTAL',
        'VALOR_ORIGINAL',
        'JUROS_MULTA',
        'DT_PGTO',
        'DT_RECBTO',
        'LOTE',
        'TX_LINK_SEI_COMPROVANTE',
        'NM_MODALIDADE_CONTRATUAL',
        'NU_INSTRUMENTO_CONTRATUAL',
        'TX_HISTORICO_DESPESA',
        'NM_GRUPO',
        'NM_PLANO_CONTAS',
        'NM_UNIDADE',
        'DS_OBSERVACAO_PENDENCIA',
        'COVID-19'
    ]

    # Reordene as colunas do DataFrame de acordo com a ordem especificada
    df = df[columns_order]
    
    # Crie uma lista de tuplas contendo os valores de cada linha do DataFrame
    values = [tuple(row) for _, row in df.iterrows()]

    # Execute a query de inserção de dados para todas as linhas de uma vez
    insert_query = F"""
    INSERT INTO {table_name} (
        NU_PROCESSO_SEI,
        NM_RAZAO_SOCIAL,
        NU_CPF_CNPJ,
        DOC_FISCAL,
        TX_LINK_SEI_DOC_FISCAL,
        DT_EMISSAO,
        DT_ATESTO,
        DT_VENCIMENTO,
        VL_TOTAL,
        VALOR_ORIGINAL,
        JUROS_MULTA,
        DT_PGTO,
        DT_RECBTO,
        LOTE,
        TX_LINK_SEI_COMPROVANTE,
        NM_MODALIDADE_CONTRATUAL,
        NU_INSTRUMENTO_CONTRATUAL,
        TX_HISTORICO_DESPESA,
        NM_GRUPO,
        NM_PLANO_CONTAS,
        NM_UNIDADE,
        DS_OBSERVACAO_PENDENCIA,
        [COVID-19]
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(insert_query, values)

    # Confirme a transação
    connection.commit()



def get_tables_data():
    page = make_request("https://igesdf.org.br/transparencia/pagamentos/")
    soup = BeautifulSoup(page.content, 'html.parser')
    
    divs = soup.find_all(lambda tag: tag.name == 'div' and 'elementor-tab-content' in tag.get('id', '') and any('Pagamentos' in a.text for a in tag.find_all('a')))
    data = {}


    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_extract = {executor.submit(
            extract_table_data, link): link for div in divs for link in div.find_all('a', href=True)}
        
        concurrent.futures.wait(future_to_extract)


        for future in concurrent.futures.as_completed(future_to_extract):
            link = future_to_extract[future]
            try:
                name_table, df = future.result()
                if df is not None:
                    data[name_table] = df
                    print(f'Dados da {name_table} armazenados!')
            except Exception as e:
               pass   
    return data

if __name__ == '__main__':
    path = '/app/planilhas'
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)

    # Estabelecer a conexão com o banco de dados
    connection = db_connect()
    if connection is not None:
        try:
            data = get_tables_data()
            for name, df in data.items():
                filename = name.replace(' ', '_').lower() + '.csv'
                # Caminho completo do arquivo CSV
                filepath = os.path.join(path, filename)
                df.to_csv(filepath, index=False, encoding='utf-8')
                print(f'O arquivo {filename} foi salvo localmente!')

                try:
                    # Inserir os dados no banco de dados
                    insert_data_to_database(df, connection)
                    print(f'Dados da {name} inseridos no banco de dados!')
                except Exception as e:
                    print(f'Ocorreu um erro ao inserir os dados da {name} no banco de dados:', e)
        finally:
            connection.close()
    else:
        print("Não foi possível estabelecer a conexão com o banco de dados.")
