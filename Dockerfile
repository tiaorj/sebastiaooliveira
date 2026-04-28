# Usando a versão estável do Python
FROM python:3.11-bullseye

# Instala dependências básicas e o Driver da Microsoft
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get clean

WORKDIR /app

# Copia e instala as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta do Render
EXPOSE 10000

# Executa com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]