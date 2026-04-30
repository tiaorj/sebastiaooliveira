from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db_connection
from routes.admin import login_required

projetos_bp = Blueprint('projetos_admin', __name__, url_prefix='/admin/projetos')

# LISTAGEM DE PROJETOS
@projetos_bp.route('/')
@login_required
def lista():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Projeto ORDER BY ProjetoId DESC")
    projetos = cursor.fetchall()
    conn.close()
    return render_template('admin/projetos_lista.html', projetos=projetos)

# ADICIONAR / EDITAR PROJETO
@projetos_bp.route('/form', defaults={'id': None}, methods=['GET', 'POST'])
@projetos_bp.route('/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        tecnologias = request.form.get('tecnologias')
        descricao = request.form.get('descricao')
        icone = request.form.get('icone')
        ordem = request.form.get('ordem') or 0
        link_git = request.form.get('link_github') # NOVO
        link_live = request.form.get('link_live')   # NOVO

        if id:
            # No UPDATE, mantemos a ordem que já existe (ou permitimos editar)
            ordem = request.form.get('ordem')
            cursor.execute("""
                UPDATE Projeto SET Titulo=?, Tecnologias=?, Descricao=?, IconeClass=?, OrdemExibicao=?, LinkGitHub=?, LinkLive=?
                WHERE ProjetoId=?
            """, (titulo, tecnologias, descricao, icone, ordem, link_git, link_live, id))
        else:
            # No INSERT, a ordem é automática: MAX + 1
            cursor.execute("""
                INSERT INTO Projeto (Titulo, Tecnologias, Descricao, IconeClass, OrdemExibicao, LinkGitHub, LinkLive)
                VALUES (?, ?, ?, ?, (SELECT ISNULL(MAX(OrdemExibicao), 0) + 1 FROM Projeto), ?, ?)
            """, (titulo, tecnologias, descricao, icone, link_git, link_live))
            flash('Projeto cadastrado com sucesso!', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('projetos_admin.lista'))

    projeto = None
    if id:
        cursor.execute("SELECT * FROM Projeto WHERE ProjetoId = ?", (id,))
        projeto = cursor.fetchone()
    
    conn.close()
    return render_template('admin/form_projeto.html', projeto=projeto)

# EXCLUIR PROJETO
@projetos_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Projeto WHERE ProjetoId = ?", (id,))
    conn.commit()
    conn.close()
    flash('Projeto removido.', 'danger')
    return redirect(url_for('projetos_admin.lista'))