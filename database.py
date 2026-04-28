import pyodbc
import platform

def get_db_connection():
    # Detecta se está no Render (Linux) ou Local (Windows)
    if platform.system() != 'Windows':
        driver = '{ODBC Driver 17 for SQL Server}'
    else:
        driver = '{SQL Server}'
        
    # Adicionamos "Login Timeout" para dar mais tempo na conexão
    conn_str = (
        f"Driver={driver};"
        "Server=DIRECTTI.mssql.somee.com;"
        "Database=DIRECTTI;"
        "UID=tiaorj_SQLLogin_1;"
        "PWD=8z3h6dedem;"
        "Connection Timeout=30;" # Dá 30 segundos para o servidor responder
        "TrustServerCertificate=yes;"
    )

    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        # Se falhar aqui, ele vai imprimir o erro exato no console
        print(f"Erro de Conexão: {e}")
        raise e