import re
import unicodedata

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db_connection
from routes.admin import login_required

experiencias_bp = Blueprint('experiencias_admin', __name__, url_prefix='/admin/experiencias')

def slugify(text):
    # Remove acentos
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Remove caracteres especiais e transforma em minúsculo
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    # Substitui espaços e hifens por underscores (conforme o padrão que vi no seu print)
    return re.sub(r'[-\s]+', '_', text)

@experiencias_bp.route('/')
@login_required
def lista():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT E.ExperienciaId, Em.NomeEmpresa, E.Cargo, 
               FORMAT(E.DataInicio, 'MM/yyyy') as Inicio, 
               ISNULL(FORMAT(E.DataFim, 'MM/yyyy'), 'Atual') as Fim
        FROM ExperienciaProfissional E
        JOIN Empresa Em ON E.EmpresaId = Em.EmpresaId
        ORDER BY E.DataInicio DESC
    """)
    experiencias = cursor.fetchall()
    conn.close()
    return render_template('admin/experiencias_lista.html', experiencias=experiencias)

@experiencias_bp.route('/form', defaults={'id': None}, methods=['GET', 'POST'])
@experiencias_bp.route('/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # 1. Captura de dados (Usando o nome correto 'resumo_curto')
        nome_empresa = request.form.get('nome_empresa').strip()
        cargo = request.form.get('cargo')
        resumo = request.form.get('resumo_curto') # Sincronizado com o HTML
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim') or None
        
        # Pega a lista de conquistas vindas do form dinâmico
        conquistas_enviadas = request.form.getlist('conquistas[]')

        # 2. Lógica de Empresa (com Slug automático)
        cursor.execute("SELECT EmpresaId FROM Empresa WHERE NomeEmpresa = ?", (nome_empresa,))
        row_empresa = cursor.fetchone()

        if row_empresa:
            empresa_id = row_empresa[0]
        else:
            novo_slug = slugify(nome_empresa)
            cursor.execute("INSERT INTO Empresa (NomeEmpresa, Slug) OUTPUT INSERTED.EmpresaId VALUES (?, ?)", 
                           (nome_empresa, novo_slug))
            empresa_id = cursor.fetchone()[0]

        # 3. Salvar Experiência
        if id:
            cursor.execute("""
                UPDATE ExperienciaProfissional 
                SET EmpresaId=?, Cargo=?, ResumoCurto=?, DataInicio=?, DataFim=?
                WHERE ExperienciaId=?
            """, (empresa_id, cargo, resumo, data_inicio, data_fim, id))
            exp_id = id
            # Limpa conquistas antigas para sobrescrever com a nova lista
            cursor.execute("DELETE FROM ExperienciaDetalhe WHERE ExperienciaId = ?", (id,))
        else:
            cursor.execute("""
                INSERT INTO ExperienciaProfissional (EmpresaId, Cargo, ResumoCurto, DataInicio, DataFim)
                OUTPUT INSERTED.ExperienciaId
                VALUES (?, ?, ?, ?, ?)
            """, (empresa_id, cargo, resumo, data_inicio, data_fim))
            exp_id = cursor.fetchone()[0]

        # 4. Salvar as Conquistas
        for desc in conquistas_enviadas:
            if desc.strip():
                cursor.execute("INSERT INTO ExperienciaDetalhe (ExperienciaId, DescricaoConquista) VALUES (?, ?)", 
                               (exp_id, desc.strip()))

        conn.commit()
        conn.close()
        flash('Experiência e detalhes salvos!', 'success')
        return redirect(url_for('experiencias_admin.lista'))

    # GET: Preparar dados para a tela
    cursor.execute("SELECT NomeEmpresa FROM Empresa ORDER BY NomeEmpresa")
    # Pegamos apenas o nome (index 0) para não vir como tupla (id, nome) no HTML
    empresas = [row[0] for row in cursor.fetchall()]
    
    exp = None
    detalhes = []
    nome_empresa_atual = ""
    
    if id:
        cursor.execute("""
            SELECT E.*, Em.NomeEmpresa 
            FROM ExperienciaProfissional E 
            JOIN Empresa Em ON E.EmpresaId = Em.EmpresaId 
            WHERE E.ExperienciaId = ?
        """, (id,))
        exp = cursor.fetchone()
        if exp:
            nome_empresa_atual = exp.NomeEmpresa
            cursor.execute("SELECT DescricaoConquista FROM ExperienciaDetalhe WHERE ExperienciaId = ?", (id,))
            detalhes = [d[0] for d in cursor.fetchall()]

    conn.close()
    return render_template('admin/form_experiencia.html', 
                           exp=exp, empresas=empresas, detalhes=detalhes, nome_empresa_atual=nome_empresa_atual)