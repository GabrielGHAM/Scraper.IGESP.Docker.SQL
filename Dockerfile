# Use a imagem base do Ubuntu
FROM python:3.10

RUN apt-get update && \
    apt-get install -y curl openjdk-11-jdk && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc && \
    echo 'source ~/.bashrc' >> ~/.bash_profile

WORKDIR /app

# Copiar o código para o diretório de trabalho
COPY . /app

USER root

# Copiar o arquivo .env para o contêiner
COPY .env /app/.env

# Instalar as dependências Python
RUN pip3 install -r requirements.txt

CMD ["python", "/app/main.py"]
