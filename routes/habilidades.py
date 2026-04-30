from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db_connection
from routes.admin import login_required

habilidades_bp = Blueprint('habilidades_admin', __name__, url_prefix='/admin/habilidades')

@habilidades_bp.route('/')
@login_required
def lista():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca categorias e habilidades para listar no painel
    cursor.execute("""
        SELECT C.NomeCategoria, H.Descricao, H.HabilidadeId, C.HabilidadeCategoriaId
        FROM Habilidade H
        JOIN HabilidadeCategoria C ON H.HabilidadeCategoriaId = C.HabilidadeCategoriaId
        ORDER BY C.NomeCategoria, H.Descricao
    """)
    habilidades = cursor.fetchall()
    
    # Busca categorias para o formulário de cadastro rápido
    cursor.execute("SELECT * FROM HabilidadeCategoria ORDER BY NomeCategoria")
    categorias = cursor.fetchall()
    
    conn.close()
    return render_template('admin/habilidades_lista.html', 
                           habilidades=habilidades, 
                           categorias=categorias)

@habilidades_bp.route('/add', methods=['POST'])
@login_required
def adicionar():
    categoria_id = request.form.get('categoria_id')
    descricao = request.form.get('descricao')
    
    if not descricao:
        flash('A descrição da habilidade é obrigatória.', 'danger')
        return redirect(url_for('habilidades_admin.lista'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Habilidade (HabilidadeCategoriaId, Descricao) VALUES (?, ?)", 
                   (categoria_id, descricao))
    conn.commit()
    conn.close()
    
    flash('Habilidade adicionada!', 'success')
    return redirect(url_for('habilidades_admin.lista'))

@habilidades_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Habilidade WHERE HabilidadeId = ?", (id,))
    conn.commit()
    conn.close()
    flash('Habilidade removida.', 'warning')
    return redirect(url_for('habilidades_admin.lista'))