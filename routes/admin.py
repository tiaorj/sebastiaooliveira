from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from functools import wraps
from werkzeug.security import check_password_hash # Importante para verificar a senha
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__)

# --- DEFINIÇÃO DO DECORADOR DE SEGURANÇA ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logado' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function
# -------------------------------------------

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('usuario')
        senha_digitada = request.form.get('senha')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Busca o usuário pelo username
        cursor.execute("SELECT UsuarioId, Nome, SenhaHash FROM Usuarios WHERE Username = ?", (username,))
        usuario = cursor.fetchone()
        
        if usuario and check_password_hash(usuario.SenhaHash, senha_digitada):
            # Verifica se a senha digitada bate com o Hash do banco
            if check_password_hash(usuario.SenhaHash, senha_digitada):
                session['admin_logado'] = True
                session['usuario_id'] = usuario.UsuarioId
                session['usuario_nome'] = usuario.Nome
                
                # Opcional: Atualizar último acesso
                cursor.execute("UPDATE Usuarios SET UltimoAcesso = ? WHERE UsuarioId = ?", (datetime.now(), usuario.UsuarioId))
                conn.commit()
                conn.close()
                
                flash(f'Bem-vindo, {usuario.Nome}!', 'success')
                return redirect(url_for('dashboard.index'))
        
        conn.close()
        flash('Usuário ou senha inválidos.', 'danger')
        
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear() # Limpa toda a sessão por segurança
    return redirect(url_for('empresa.home'))

@admin_bp.route('/experiencia/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_experiencia(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        cargo = request.form.get('cargo')
        resumo = request.form.get('resumo_curto')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim') or None

        cursor.execute("""
            UPDATE ExperienciaProfissional 
            SET EmpresaId = ?, Cargo = ?, ResumoCurto = ?, DataInicio = ?, DataFim = ?
            WHERE ExperienciaId = ?
        """, (empresa_id, cargo, resumo, data_inicio, data_fim, id))
        
        conn.commit()
        conn.close()
        flash('Experiência e empresa atualizadas!', 'success')
        return redirect(url_for('curriculo.especialista'))

    # BUSCA DADOS DA EXPERIÊNCIA
    cursor.execute("SELECT * FROM ExperienciaProfissional WHERE ExperienciaId = ?", (id,))
    exp = cursor.fetchone()

    # BUSCA LISTA DE EMPRESAS PARA O SELECT
    cursor.execute("SELECT EmpresaId, NomeEmpresa FROM Empresa ORDER BY NomeEmpresa")
    empresas = cursor.fetchall()

    # BUSCA OS DETALHES (CONQUISTAS) DESTA EXPERIÊNCIA
    cursor.execute("SELECT * FROM ExperienciaDetalhe WHERE ExperienciaId = ?", (id,))
    detalhes = cursor.fetchall()

    conn.close()
    return render_template('admin/form_experiencia.html', exp=exp, empresas=empresas, detalhes=detalhes)

# Rota para Adicionar Detalhe
@admin_bp.route('/experiencia/detalhe/adicionar/<int:exp_id>', methods=['POST'])
@login_required
def adicionar_conquista(exp_id):
    descricao = request.form.get('descricao_conquista')
    if descricao:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ExperienciaDetalhe (ExperienciaId, DescricaoConquista) 
            VALUES (?, ?)
        """, (exp_id, descricao))
        conn.commit()
        conn.close()
        flash('Conquista adicionada com sucesso!', 'success')
    
    return redirect(url_for('admin.editar_experiencia', id=exp_id))

# Rota para Excluir Detalhe
@admin_bp.route('/experiencia/detalhe/excluir/<int:detalhe_id>/<int:exp_id>')
@login_required
def excluir_conquista(detalhe_id, exp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ExperienciaDetalhe WHERE ExperienciaDetalheId = ?", (detalhe_id,))
    conn.commit()
    conn.close()
    flash('Conquista removida.', 'info')
    
    return redirect(url_for('admin.editar_experiencia', id=exp_id))