from bs4 import BeautifulSoup
import requests
import concurrent.futures
import re
import tabula
import pandas as pd
from modulos.database import Tabela


def make_requests_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    return requests.get(url, headers=headers)


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
        
        tabela = Tabela()
        df = tabela.clean_rows_columns(df, name_table)
        return name_table, df

    except Exception as e:
        print(f'Erro ao extrair a {name_table}',e)

        
def get_tables_data():
    
    page = make_requests_url("https://igesdf.org.br/transparencia/pagamentos/")
    soup = BeautifulSoup(page.content, 'html.parser')    
    divs = soup.find_all(lambda tag: tag.name == 'div' and 'elementor-tab-content' in tag.get('id', '') and any('Pagamentos' in a.text for a in tag.find_all('a')))
    data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_extract = {executor.submit(extract_table_data, link): link for div in divs for link in div.find_all('a', href=True)}
        
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


