# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Instala as dependências do sistema e o driver Microsoft ODBC 17
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get clean

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Flask usa
EXPOSE 10000

# Comando para rodar a aplicação usando Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]