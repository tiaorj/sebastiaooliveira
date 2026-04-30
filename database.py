import os
import pyodbc
import platform
from dotenv import load_dotenv


def get_db_connection():
    load_dotenv()

    # Detecta se está no Render (Linux) ou Local (Windows)
    if platform.system() != 'Windows':
        driver = '{ODBC Driver 17 for SQL Server}'
    else:
        driver = '{SQL Server}'


    
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    
    if not server or not database:
        raise ValueError("ERRO: As variáveis de ambiente não foram carregadas do arquivo .env")

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"Connection Timeout=30;" # Dá mais tempo para o SQL responder
    )
    return pyodbc.connect(conn_str)