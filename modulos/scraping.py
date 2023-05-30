from bs4 import BeautifulSoup
import requests
import concurrent.futures
import tabula
import pandas as pd
from modulos.tabela import Tabela
from modulos.config import generate_name_table, generate_filename, formatar_tempo
from modulos.database import DatabaseManager
from modulos.logs import  DataLogger, columns_dataLogger, dataLogger_table_name, create_columns_dataLogger
import os
import time
from dotenv import load_dotenv
load_dotenv()



class Scraper:
    def __init__(self, logger_instance):
        self.logger_instance = logger_instance
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        }

    def make_request(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f'Erro ao fazer a requisição: {e}')
            raise

    def extract_table_data(self, link):
        name_table = generate_name_table(link)
        filename = generate_filename(name_table)
        try:
            href = link.get('href')
            if href.endswith('.pdf'):
                df = self.read_pdf_table(href, name_table)
            else:
                df = self.read_html_table(href, name_table)

            if df.empty:
                print(
                    f'Erro ao extrair a {name_table}: DataFrame nulo. Pulando o processamento.')
                return name_table, None, href

            tabela = Tabela()
            df = tabela.clean_rows_columns(df, name_table)
            self.logger_instance.info(f'{filename} - {len(df)} lines saved')
            return name_table, df, href

        except Exception as e:
            pass

    def read_pdf_table(self, href, name_table):
        filename = generate_filename(name_table)
        try:
            df = tabula.read_pdf(href, pages='all')
            df = pd.concat(df)
            df.columns = df.columns.str.replace('\r', ' ')
            self.logger_instance.info(f'{filename} - {len(df)} lines read')
            return df
        except Exception as e:
            print(f'Erro ao ler dados de {name_table}', e)

    def read_html_table(self, href, name_table):
        filename = generate_filename(name_table)
        try:
            df = pd.read_html(href)
            df = pd.concat(df)
            self.logger_instance.info(f'{filename} - {len(df)} lines read')
            return df
        except Exception as e:
            print(f'Erro ao ler dados de {name_table}', e)

    def find_table_links(self, soup):
        try:
            divs = soup.find_all(lambda tag: tag.name == 'div' and 'elementor-tab-content' in tag.get(
                'id', '') and any('Pagamentos' in a.text for a in tag.find_all('a')))
            links = [link for div in divs for link in div.find_all(
                'a', href=True)]
            return links
        except Exception as e:
            print(f'Erro ao encontrar links das tabelas: {e}')
            raise

    def get_tables_data(self):
        page = self.make_request("https://igesdf.org.br/transparencia/pagamentos/")
        soup = BeautifulSoup(page.content, 'html.parser')
        links = self.find_table_links(soup)
        data = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_extract = {executor.submit(self.extract_table_data, link): link for link in links}
            concurrent.futures.wait(future_to_extract)
            for future in concurrent.futures.as_completed(future_to_extract):
                link = future_to_extract[future]
                try:
                    name_table, df, href = future.result()
                    if df is not None:
                        data[name_table] = df, href
                except Exception as e:
                    pass
        return data

    def run_scraping(self):
        start_time = time.time()
        table_name = os.getenv('TB_NAME')
        self.database_manager = DatabaseManager()  # Adicione esta linha
        self.database_manager.create_database()
        tabela = Tabela()
        self.database_manager.truncate_table(table_name)
        self.database_manager.create_table(table_name, tabela.create_table_columns)
        self.database_manager.create_table(dataLogger_table_name, create_columns_dataLogger)


        path = os.getenv('pathCSV')
        if not os.path.exists(path):
            os.makedirs(path)

        try:
            data_values = []
            log_values_list = []

            data = self.get_tables_data()
            for name_table, (df, href) in data.items():
                filename = generate_filename(name_table)
                filepath = os.path.join(path, filename)
                df.to_csv(filepath, index=False, encoding='utf-8')
                end_time = time.time()
                total_time = end_time - start_time
                tempo_formatado = formatar_tempo(total_time)

                combined_df_values = tabela.create_values_list(df)
                data_values.extend(combined_df_values)

                data_logger = DataLogger(
                    href=href, filename=filename, qtd_linhas=len(df), tempo_busca=tempo_formatado, status='Salvo no Banco de dados')
                log_data = data_logger.file_log_data()
                log_values_list.append(tuple(log_data.values()))

            # Iniciar transação
            self.database_manager.begin_transaction()

            try:
                print('Inserindo dados no banco de dados')
                self.database_manager.insert_data_bulk(dataLogger_table_name, log_values_list, columns_dataLogger)
                self.database_manager.insert_data_bulk(table_name, data_values, tabela.table_columns)
                self.logger_instance.info(f'{table_name} {len(data_values)} lines saved in the database')
            except Exception as e:
                print(f'Erro ao inserir {table_name} {len(data_values)} linhas no banco de dados:', e)
                self.database_manager.rollback_transaction()
            else:
                # Commit da transação se tudo ocorrer sem erros
                self.database_manager.commit_transaction()
                self.logger_instance.info('Data and logs saved in the database')
        finally:
            end_time_program = time.time()
            total_time_program = end_time_program - start_time
            total_time_program_formatted = formatar_tempo(total_time_program)
            self.database_manager.close_connection()
            self.logger_instance.info(f'Connection closed: {total_time_program_formatted}')
