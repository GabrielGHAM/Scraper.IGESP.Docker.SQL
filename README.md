# Projeto de Scraping de Planilhas de Pagamento do IGESP DF
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Python-blue.svg)](https://docker.com/)


## Descrição

- Erojeto de raspagem de dados (Scraping) das planilhas de pagamentos do IGESP DF, processo de Extreção e Carregamento (EL de ELT), sendo executado em containers Docker.

## Funcionalidades
- Extrair dados das planilhas de pagamento do IGESP DF
- Tratar os dados e padronizá-los como dataframes
- Salvar os dados em formato CSV
- Armazenar os dados em um banco de dados
- Gerar logs das operações e salvar no banco de dados
- 
## Requisitos
- Docker
- Docker Compose
- 
## Execução do Projeto
- O projeto é executado em um ambiente Docker utilizando o Docker Compose.
- Edite o arquivo .env com as variáveis necessárias
- Execute com o comando `docker compose up --build`

## .env
    (não alterar Server, Database e UID)
- SERVER=dbsqlserver
- DATABASE=master
- UID=sa
- pathCSV=/app/data/planilhas
- MSSQL_SA_PASSWORD=SenhA_SeGURA ( Senha segura SQL, Letra maiúscula, letra minúscula , números e não alpha-numérico
TB_NAME=TB_TABELA  ( Nome da tabela de dados)
DB_NAME=DB_IGESP   ( Nome da Database)
Certifique-se de ajustar os valores das variáveis conforme necessário.

Execute o comando docker-compose up --build para criar e executar os contêineres do projeto.
O scraping será iniciado e os dados serão extraídos, transformados e salvos no banco de dados.
Os logs das operações também serão salvos no banco de dados.

# Estrutura do Projeto
A estrutura do projeto é organizada da seguinte forma:

- main.py: Arquivo principal do projeto. Executa o scraping e salva os dados no banco de dados.
- dockerfile: Arquivo de configuração do Docker para a construção da imagem do projeto.
- docker-compose.yml: Arquivo de configuração do Docker Compose para a execução do projeto.
- modulos/
  - scraping.py: Contém a lógica do scraping das planilhas de pagamento.
  - logs.py: Contém a lógica de criação e salvamento dos logs.
  - tabela.py: Contém a a lógica relacionado aos dados das tabelas, tratamento de colunas..
  - database.py: Contém a lógica de gerenciamento do banco de dados.
- .env: Arquivo de configuração com as variáveis de ambiente do projeto.

Fique à vontade para ajustar as configurações e personalizar o projeto de acordo com suas necessidades.
