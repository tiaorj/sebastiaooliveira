import pyodbc
from contextlib import contextmanager
from config import Config

def get_db_connection():
    conn_str = (
        f"DRIVER={Config.DB_DRIVER};"
        f"SERVER={Config.DB_SERVER};"
        f"DATABASE={Config.DB_DATABASE};"
        f"UID={Config.DB_USERNAME};"
        f"PWD={Config.DB_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

@contextmanager
def get_db_cursor():
    """Gerencia a abertura e fechamento automático da conexão e do cursor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()