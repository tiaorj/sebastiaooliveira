from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db_connection
from routes.admin import login_required

certificacoes_bp = Blueprint('certificacoes_admin', __name__, url_prefix='/admin/certificacoes')

@certificacoes_bp.route('/')
@login_required
def lista():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Certificacoes ORDER BY Nome")
    certificados = cursor.fetchall()
    conn.close()
    return render_template('admin/certificacoes_lista.html', certificados=certificados)

@certificacoes_bp.route('/form', defaults={'id': None}, methods=['GET', 'POST'])
@certificacoes_bp.route('/form/<int:id>', methods=['GET', 'POST'])
@login_required
def form(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        instituicao = request.form.get('instituicao')
        icone = request.form.get('icone')
        link = request.form.get('link')

        if id:
            cursor.execute("""
                UPDATE Certificacoes SET Nome=?, Instituicao=?, IconeClass=?, LinkVerificacao=?
                WHERE CertificacaoId=?
            """, (nome, instituicao, icone, link, id))
            flash('Certificação atualizada!', 'success')
        else:
            cursor.execute("""
                INSERT INTO Certificacoes (Nome, Instituicao, IconeClass, LinkVerificacao)
                VALUES (?, ?, ?, ?)
            """, (nome, instituicao, icone, link))
            flash('Certificação cadastrada com sucesso!', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('certificacoes_admin.lista'))

    certificado = None
    if id:
        cursor.execute("SELECT * FROM Certificacoes WHERE CertificacaoId = ?", (id,))
        certificado = cursor.fetchone()
    
    conn.close()
    return render_template('admin/form_certificacao.html', certificado=certificado)

@certificacoes_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Certificacoes WHERE CertificacaoId = ?", (id,))
    conn.commit()
    conn.close()
    flash('Certificação removida.', 'danger')
    return redirect(url_for('certificacoes_admin.lista'))