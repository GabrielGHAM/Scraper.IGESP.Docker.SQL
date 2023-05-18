# Use a imagem base do Ubuntu
FROM python:3.10

RUN apt-get update && \
    apt-get install -y gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev unixodbc libstdc++6 zlib1g curl gnupg openjdk-11-jdk

RUN apt-get install -y bash icu-devtools krb5-locales libgcc-s1 libgssapi-krb5-2 libkrb5-3 libssl1.1

# Verificar a versão do Ubuntu
RUN if ! [[ "16.04 18.04 20.04 22.04" == *"$(lsb_release -rs)"* ]]; then \
        echo "Ubuntu $(lsb_release -rs) is not currently supported."; \
        exit; \
    fi

# Importar a chave GPG da Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Adicionar o repositório da Microsoft para o SQL Server
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update

# Aceitar o contrato de licença (EULA) e instalar o msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Instalar o mssql-tools
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools

# Adicionar o diretório de ferramentas ao PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Carregar as variáveis de ambiente
RUN echo 'source ~/.bashrc' >> ~/.bash_profile

WORKDIR /app

# Criar o arquivo .env com as configurações de conexão
RUN echo "SERVER=************" > /app/.env \
    && echo "DATABASE=*********" >> /app/.env \
    && echo "USERNAME=**********" >> /app/.env \
    && echo "PASSWORD=*********" >> /app/.env \
    && echo "DATA_PATH=************" >> /app/.env\
    && echo "TB_NAME=*********" >> /app/.env 


# Copiar o código para o diretório de trabalho
COPY . /app

# Criar o diretório "planilhas"
RUN mkdir /app/planilhas

# Copia os arquivos do docker para o Path local
VOLUME ${DATA_PATH}:/app/planilhas

# Instalar as dependências Python
RUN pip3 install -r requirements.txt

# Executar o script Python
EXPOSE 8000

# Mostrar o conteúdo do arquivo .env para fins de depuração
RUN cat /app/.env

CMD ["python", "/app/main.py", "runserver", "0.0.0.0:8000"]



