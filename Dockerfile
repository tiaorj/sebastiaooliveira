# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Evita interrupções por prompts de configuração
ENV DEBIAN_FRONTEND=noninteractive

# 2. Instala apenas o necessário para baixar a chave e o driver
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    && apt-get clean

# 3. Baixa a chave da Microsoft e converte para o formato de keyring (substitui o apt-key)
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# 4. Adiciona o repositório usando a chave específica criada acima
RUN echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# 5. Instala o Driver ODBC 17 e dependências do pyodbc
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17 \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 6. Configuração do ambiente de trabalho
WORKDIR /app

# 7. Instalação das dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 8. Copia o código fonte[cite: 1]
COPY . .

# 9. Inicialização com Gunicorn para o Render
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]