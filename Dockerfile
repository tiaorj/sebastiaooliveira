# 1. Imagem base estável
FROM python:3.10-slim

# 2. Instala dependências básicas do sistema e certificados
# O erro 127 ocorre muitas vezes porque 'curl' ou 'gnupg2' não estão presentes no shell
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg2 \
    && apt-get clean

# 3. Adiciona a chave oficial da Microsoft para o repositório de pacotes
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# 4. Adiciona o repositório do Microsoft ODBC Driver 17 para Debian 11 (Bullseye)
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 5. Instala o Driver ODBC e ferramentas de desenvolvimento para o pyodbc
# ACCEPT_EULA=Y é obrigatório para aceitar os termos da Microsoft automaticamente
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17 \
    unixodbc-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 6. Define o diretório de trabalho no container
WORKDIR /app

# 7. Copia apenas o requirements primeiro para aproveitar o cache do Docker
# Isso acelera os próximos deploys se as bibliotecas não mudarem
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 8. Copia todo o restante do código do projeto para o container
COPY . .

# 9. Comando de execução usando Gunicorn (Padrão para Render/Produção)
# O bind na porta 10000 é o padrão do Render para Web Services
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]