# -*- coding: utf-8 -*-
import pyodbc
import platform
from flask import Flask, render_template

app = Flask(__name__)

# --- CONFIGURAÇÃO DE CONEXÃO ---
if platform.system() == 'Windows':
    DRIVER = '{SQL Server}'
else:
    DRIVER = '{ODBC Driver 17 for SQL Server}'

CONN_STR = (
    f"Driver={DRIVER};"
    "Server=DIRECTTI.mssql.somee.com;"
    "Database=DIRECTTI;"
    "UID=tiaorj_SQLLogin_1;"
    "PWD=8z3h6dedem;"
    "TrustServerCertificate=yes;"
)

# Informações base da DIRECTI / Sebastião
INFO_BASE = {
    'nome': 'DIRECTI Solutions',
    'especialista': 'SEBASTIÃO OLIVEIRA',
    'cargo': 'Analista de Sistemas Sênior & Arquiteto de Software',
    'contato': {
        'local': 'Rio de Janeiro – RJ',
        'telefone': '(41) 99911-3960',
        'email': 'tiaorj@gmail.com',
        'linkedin': 'linkedin.com/in/sebastião-oliveira-53346833'
    }
}

def get_db_connection():
    try:
        # Definimos um timeout curto para não travar o site se a Somee demorar
        return pyodbc.connect(CONN_STR, timeout=10)
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

# --- ROTAS ---

@app.route('/')
def home():
    """Página Inicial: Portfólio da Empresa DIRECTI"""
    conn = get_db_connection()
    cases = []
    if conn:
        cursor = conn.cursor()
        # Busca os cases da nova tabela da empresa
        try:
            cursor.execute("SELECT servico, cliente, descricao_case, resultado FROM PortfoliioEmpresa")
            for row in cursor.fetchall():
                cases.append({
                    'servico': row.servico,
                    'cliente': row.cliente,
                    'descricao': row.descricao_case,
                    'resultado': row.resultado
                })
        except:
            # Caso a tabela ainda não exista, enviamos uma lista vazia
            pass
        conn.close()
    
    return render_template('empresa.html', info=INFO_BASE, cases=cases)

@app.route('/sobre')
def sobre():
    """Página Sobre o Especialista: Currículo Detalhado"""
    conn = get_db_connection()
    experiencias = []
    habilidades = []
    formacao = []
    
    if conn:
        cursor = conn.cursor()
        
        # Buscar Experiências
        cursor.execute("SELECT slug, empresa, periodo, cargo, resumo_curto, detalhes_pipe FROM Experiencias")
        for row in cursor.fetchall():
            experiencias.append({
                'id': row.slug,
                'empresa': row.empresa,
                'periodo': row.periodo,
                'cargo': row.cargo,
                'resumo_curto': row.resumo_curto,
                'detalhes': row.detalhes_pipe.split('|') if row.detalhes_pipe else []
            })

        # Buscar Habilidades
        cursor.execute("SELECT categoria, itens FROM Habilidades")
        for row in cursor.fetchall():
            habilidades.append({'categoria': row.categoria, 'itens': row.itens})

        # Buscar Formação
        cursor.execute("SELECT descricao FROM Formacao")
        for row in cursor.fetchall():
            formacao.append(row.descricao)
            
        conn.close()

    dados_completos = {
        **INFO_BASE,
        'resumo': "Analista Sênior com sólida trajetória em modernização de ecossistemas corporativos.",
        'habilidades': habilidades,
        'experiencias': experiencias,
        'formacao': formacao
    }
    return render_template('index.html', info=dados_completos)

@app.route('/projetos')
def projetos():
    """Página de Projetos Técnicos"""
    conn = get_db_connection()
    meus_projetos = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, tecnologias, descricao, icone FROM Projetos")
        for row in cursor.fetchall():
            meus_projetos.append({
                'titulo': row.titulo,
                'tecnologias': row.tecnologias,
                'descricao': row.descricao,
                'icone': row.icone
            })
        conn.close()
    return render_template('projetos.html', info=INFO_BASE, projetos=meus_projetos)

@app.route('/contato')
def contato():
    """Página de Contato"""
    return render_template('contato.html', info=INFO_BASE)

if __name__ == '__main__':
    app.run(debug=True)