from flask import Blueprint, render_template
from database import get_db_connection

curriculo_bp = Blueprint('curriculo', __name__)

@curriculo_bp.route('/sobre')
def sobre():
    # Esta rota agora foca no resumo e nas experiências
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca Experiências e Detalhes (mesma lógica que criamos antes)
    cursor.execute("""
        SELECT E.ExperienciaId, Em.NomeEmpresa, E.Cargo, E.ResumoCurto,
               FORMAT(E.DataInicio, 'MM/yyyy') + ' - ' + ISNULL(FORMAT(E.DataFim, 'MM/yyyy'), 'Atual') as Periodo
        FROM ExperienciaProfissional E
        JOIN Empresa Em ON E.EmpresaId = Em.EmpresaId
        ORDER BY 
            CASE WHEN E.DataFim IS NULL THEN 0 ELSE 1 END, -- NULL ganha peso 0 (vem primeiro)
            E.DataFim DESC,                               -- Depois, as datas mais recentes
    E.DataInicio DESC;
    """)
    exps_raw = cursor.fetchall()

    cursor.execute("SELECT ExperienciaId, DescricaoConquista FROM ExperienciaDetalhe")
    detalhes_raw = cursor.fetchall()
    
    detalhes_map = {}
    for d in detalhes_raw:
        if d.ExperienciaId not in detalhes_map:
            detalhes_map[d.ExperienciaId] = []
        detalhes_map[d.ExperienciaId].append(d.DescricaoConquista)

    experiencias = []
    for exp in exps_raw:
        experiencias.append({
            'id': exp.ExperienciaId, 'empresa': exp.NomeEmpresa, 'cargo': exp.Cargo, 'periodo': exp.Periodo,
            'resumo_curto': exp.ResumoCurto, 'detalhes': detalhes_map.get(exp.ExperienciaId, [])
        })

    conn.close()
    return render_template('index.html', info={'experiencias': experiencias, 'resumo': 'Analista Sênior...'})

@curriculo_bp.route('/formacao')
def formacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT NomeCurso, NomeInstituicao, AnoInicio, AnoConclusao FROM FormacaoAcademica ORDER BY AnoInicio DESC")
    
    formacao_lista = []
    for row in cursor.fetchall():
        formacao_lista.append({
            'curso': row.NomeCurso,
            'instituicao': row.NomeInstituicao,
            'AnoInicio': row.AnoInicio,
            'ano': row.AnoConclusao
        })


    # Busca Certificações (A nova tabela!)
    cursor.execute("SELECT Nome, Instituicao, IconeClass, LinkVerificacao FROM Certificacoes")
    certificados_lista = []
    for row in cursor.fetchall():
        certificados_lista.append({
            'nome': row.Nome,
            'instituicao': row.Instituicao,
            'icone': row.IconeClass,
            'link': row.LinkVerificacao
        })
    conn.close()
    return render_template('Formacao.html', formacao=formacao_lista, certificados=certificados_lista)

@curriculo_bp.route('/habilidades')
def habilidades():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.NomeCategoria, STRING_AGG(H.Descricao, ', ') as Itens
        FROM Habilidade H
        JOIN HabilidadeCategoria C ON H.HabilidadeCategoriaId = C.HabilidadeCategoriaId
        GROUP BY C.NomeCategoria
    """)
    
    habilidades_lista = []
    for row in cursor.fetchall():
        habilidades_lista.append({
            'categoria': row.NomeCategoria,
            'itens': row.Itens
        })
    conn.close()
    return render_template('Habilidades.html', habilidades=habilidades_lista)