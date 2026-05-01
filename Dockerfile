FROM python:3.10-slim

# Instala dependências do sistema e o Driver ODBC da Microsoft para SQL Server
RUN apt-get update && apt-get install -y \
    curl gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Comando de inicialização para produção
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]