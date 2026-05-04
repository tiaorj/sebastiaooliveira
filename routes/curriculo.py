from flask import Blueprint, render_template, make_response
from database import get_db_cursor
from xhtml2pdf import pisa
from io import BytesIO

curriculo_bp = Blueprint('curriculo', __name__)

# FUNÇÃO AUXILIAR: Centraliza a inteligência de busca
def get_dados_completos_curriculo():
    with get_db_cursor() as cursor:
        # 1. BUSCAR EXPERIÊNCIAS
        cursor.execute("""
            SELECT E.ExperienciaId, Em.NomeEmpresa, E.Cargo, E.ResumoCurto,
                FORMAT(E.DataInicio, 'MM/yyyy') + ' - ' + ISNULL(FORMAT(E.DataFim, 'MM/yyyy'), 'Atual') as Periodo,
                DataInicio
            FROM ExperienciaProfissional E
            JOIN Empresa Em ON E.EmpresaId = Em.EmpresaId
            ORDER BY CASE WHEN E.DataFim IS NULL THEN 0 ELSE 1 END, E.DataFim DESC, E.DataInicio DESC
        """)
        exps_rows = cursor.fetchall()

        # 2. BUSCAR DETALHES
        cursor.execute("SELECT ExperienciaId, DescricaoConquista FROM ExperienciaDetalhe")
        detalhes_rows = cursor.fetchall()
        
        detalhes_map = {}
        for d in detalhes_rows:
            if d.ExperienciaId not in detalhes_map:
                detalhes_map[d.ExperienciaId] = []
            detalhes_map[d.ExperienciaId].append(d.DescricaoConquista)

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

        # 3. HABILIDADES
        cursor.execute("""
            SELECT C.NomeCategoria, STRING_AGG(H.Descricao, ', ') as Itens
            FROM Habilidade H
            JOIN HabilidadeCategoria C ON H.HabilidadeCategoriaId = C.HabilidadeCategoriaId
            GROUP BY C.NomeCategoria
        """)
        habilidades = cursor.fetchall()

        # 4. FORMAÇÃO
        cursor.execute("""
            SELECT NomeCurso, NomeInstituicao, Descricao, NomeCursoAbreviado, 
            CAST(AnoInicio AS VARCHAR) + ' - ' + ISNULL(CAST(AnoConclusao AS VARCHAR), 'Cursando') as PeriodoFormacao
            FROM FormacaoAcademica
            ORDER BY CASE WHEN AnoConclusao IS NULL THEN 0 ELSE 1 END, AnoConclusao DESC, AnoInicio DESC
        """)
        formacao_rows = cursor.fetchall()

        lista_formacao = [{
            'curso': f.NomeCurso,
            'instituicao': f.NomeInstituicao,
            'periodo': f.PeriodoFormacao,
            'Descricao': f.Descricao,
            'NomeCursoAbreviado': f.NomeCursoAbreviado
        } for f in formacao_rows]

        # 5. CERTIFICAÇÕES
        cursor.execute("SELECT Nome, Instituicao, IconeClass, LinkVerificacao FROM Certificacoes")
        certificados = cursor.fetchall()

    return {
        'experiencias': lista_experiencias,
        'habilidades': habilidades,
        'formacao': lista_formacao,
        'certificados': certificados
    }

# ROTA 1: Versão Web (Especialista)
@curriculo_bp.route('/especialista')
def especialista():
    dados = get_dados_completos_curriculo()
    return render_template('especialista.html', **dados)

@curriculo_bp.route('/gerar-pdf')
def gerar_pdf():
#@curriculo_bp.route('/debug-html')
#def debug_html():
    dados = get_dados_completos_curriculo()
        
    # 2. Renderizar o HTML específico para o PDF
    html = render_template('pdf_template.html', **dados)

    # 3. Converter HTML para PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding="UTF-8")

    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=curriculo_sebastiao.pdf'
        return response
    
    return "Erro ao gerar PDF", 500
    #return render_template('pdf_template.html', **dados)