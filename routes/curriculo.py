from flask import Blueprint, render_template
from database import get_db_connection

curriculo_bp = Blueprint('curriculo', __name__)

@curriculo_bp.route('/especialista')
def especialista():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. BUSCAR EXPERIÊNCIAS (Ordenadas: Atual primeiro)
    cursor.execute("""
        SELECT E.ExperienciaId, Em.NomeEmpresa, E.Cargo, E.ResumoCurto,
               FORMAT(E.DataInicio, 'MM/yyyy') + ' - ' + ISNULL(FORMAT(E.DataFim, 'MM/yyyy'), 'Atual') as Periodo
        FROM ExperienciaProfissional E
        JOIN Empresa Em ON E.EmpresaId = Em.EmpresaId
        ORDER BY CASE WHEN E.DataFim IS NULL THEN 0 ELSE 1 END, E.DataFim DESC, E.DataInicio DESC
    """)
    exps_rows = cursor.fetchall()

    # 2. BUSCAR DETALHES/CONQUISTAS
    cursor.execute("SELECT ExperienciaId, DescricaoConquista FROM ExperienciaDetalhe")
    detalhes_rows = cursor.fetchall()
    
    # Mapear detalhes para suas respectivas experiências
    detalhes_map = {}
    for d in detalhes_rows:
        if d.ExperienciaId not in detalhes_map:
            detalhes_map[d.ExperienciaId] = []
        detalhes_map[d.ExperienciaId].append(d.DescricaoConquista)

    # Montar lista final de experiências com seus detalhes acoplados
    lista_experiencias = []
    for row in exps_rows:
        lista_experiencias.append({
            'id': row.ExperienciaId,
            'empresa': row.NomeEmpresa,
            'cargo': row.Cargo,
            'resumo': row.ResumoCurto,
            'periodo': row.Periodo,
            'conquistas': detalhes_map.get(row.ExperienciaId, [])
        })

    # 3. BUSCAR HABILIDADES (Usando sua nova query com STRING_AGG)
    cursor.execute("""
        SELECT C.NomeCategoria, STRING_AGG(H.Descricao, ', ') as Itens
        FROM Habilidade H
        JOIN HabilidadeCategoria C ON H.HabilidadeCategoriaId = C.HabilidadeCategoriaId
        GROUP BY C.NomeCategoria
    """)
    habilidades = cursor.fetchall()

    # 4. BUSCAR FORMAÇÃO ACADÊMICA
    cursor.execute("""
        SELECT NomeCurso, NomeInstituicao, 
           CAST(AnoInicio AS VARCHAR) + ' - ' + ISNULL(CAST(AnoConclusao AS VARCHAR), 'Cursando') as PeriodoFormacao
        FROM FormacaoAcademica
        ORDER BY CASE WHEN AnoConclusao IS NULL THEN 0 ELSE 1 END, AnoConclusao DESC, AnoInicio DESC
    """)
    formacao_rows = cursor.fetchall()

    lista_formacao = []
    for f in formacao_rows:
        lista_formacao.append({
            'curso': f.NomeCurso,
            'instituicao': f.NomeInstituicao,
            'periodo': f.PeriodoFormacao
        })

    # 5. BUSCAR CERTIFICAÇÕES (Badges)
    cursor.execute("SELECT Nome, Instituicao, IconeClass, LinkVerificacao FROM Certificacoes")
    certificados = cursor.fetchall()

    conn.close()

    return render_template('especialista.html', 
                        experiencias=lista_experiencias, 
                        habilidades=habilidades,
                        formacao=lista_formacao,
                        certificados=certificados)