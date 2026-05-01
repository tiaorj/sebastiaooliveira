import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Segurança
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'chave-padrao-super-secreta')
    
    # Configurações do Banco de Dados
    DB_SERVER = os.getenv('DB_SERVER')
    DB_DATABASE = os.getenv('DB_DATABASE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Driver automático: usa Driver 17 para Linux (Render) e Windows local
    DB_DRIVER = '{ODBC Driver 17 for SQL Server}'