# Use a imagem base do Ubuntu
FROM python:3.10

RUN apt-get update && \
    apt-get install -y curl openjdk-11-jdk

# Importar a chave GPG da Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Adicionar o repositório da Microsoft para o SQL Server
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update

# Aceitar o contrato de licença (EULA) e instalar o msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Adicionar o diretório de ferramentas ao PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Carregar as variáveis de ambiente
RUN echo 'source ~/.bashrc' >> ~/.bash_profile

WORKDIR /app
# Copiar o código para o diretório de trabalho
COPY . /app

# Copiar o arquivo .env para o contêiner
COPY .env /app/.env

# Instalar as dependências Python
RUN pip3 install -r requirements.txt

CMD ["python", "/app/main.py"]
