# Projeto de Scraper do IGESP DF
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Python-blue.svg)](https://docker.com/)
### Gabriel Almada
#### Maio de 2023

Processo de extração e Carregamento (EL de ELT) das planilhas de pagamentos do IGESP DF, sendo executado em contêineres Docker.

![arch](https://i.imgur.com/1Mm8EOh.png)



## Funcionalidades
- Extrair dados das planilhas de pagamento do IGESP DF
- Tratar os dados e padronizá-los como dataframes
- Salvar os dados em formato CSV
- Armazenar os dados em um banco de dados
- Gerar logs das operações e salvar no banco de dados


## Estrutura do Projeto
A estrutura do projeto é organizada da seguinte forma:

- main.py: Arquivo principal do projeto. Executa o Scraper e salva os dados no banco de dados.
- dockerfile: Arquivo de configuração do Docker para a construção da imagem do projeto.
- docker-compose.yml: Arquivo de configuração do Docker Compose para a execução do projeto.
- modulos/
  - scraping.py: Contém a lógica do Scraper das planilhas de pagamento.
  - logs.py: Contém a lógica de criação e salvamento dos logs.
  - tabela.py: Contém a a lógica relacionado aos dados das tabelas, tratamento de colunas..
  - database.py: Contém a lógica de gerenciamento do banco de dados.
- .env: Arquivo de configuração com as variáveis de ambiente do projeto.
# Passo a passo para execução

## 1 - Pré-requisitos

- Docker
- docker-compose

## 2 - Configurar o arquivo .env

Você deve criar um arquivo `.env` e atribuir os valores das credenciais do SQL. O arquivo deve ser conforme o modelo:
(não alterar Server, Database e UID)
```
SERVER=dbsqlserver
DATABASE=master
UID=sa
pathCSV=/app/data/planilhas

MSSQL_SA_PASSWORD=SenhA_SeGURA (Letra maiúscula, letra minúscula , números e não alpha-numérico)
TB_NAME=TB_EXEMPLO  ( Nome da tabela de dados)
DB_NAME=DB_EXEMPLO  ( Nome da Database)
```
## 3 - Buildar e executar os containêres 
Clone o repositório e execute o projeto com o seguinte comando:

```bash
git clone https://github.com/GabrielGHAM/Scraper.IGESP.Docker.SQL.git
cd Scraper.IGESP.Docker.SQL
docker compose up --build
```

O Scraper será iniciado e os dados serão extraídos, as colunas serão padronizadas e salvas locamente na pasta ./data/planilhas e no banco de dados.
Os logs das operações também serão salvos no banco.

**Parabéns**!! Você acabou de concluir a Extração e carregamento de dados.

#### Fique à vontade para ajustar as configurações e personalizar o projeto de acordo com suas necessidades.
