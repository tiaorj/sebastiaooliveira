from flask import Flask
from flask_mail import Mail
from routes.empresa import empresa_bp
from routes.curriculo import curriculo_bp
from routes.admin import admin_bp 
from datetime import datetime
from routes.dashboard import dashboard_bp
from routes.projetos import projetos_bp
from routes.habilidades import habilidades_bp
from routes.certificacoes import certificacoes_bp
from routes.experiencias import experiencias_bp
import os
from dotenv import load_dotenv
from flask import render_template
from routes.formacao import formacao_bp

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave-padrao-muito-fraca')

@app.template_filter('formatar_data')
def formatar_data(value, formato='%d/%m/%Y'):
    if not value:
        return ""
    # Se já for um objeto date/datetime do Python (o pyodbc costuma retornar assim)
    if hasattr(value, 'strftime'):
        return value.strftime(formato)
    return value

app.register_blueprint(admin_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(projetos_bp)
app.register_blueprint(habilidades_bp)
app.register_blueprint(certificacoes_bp)
app.register_blueprint(experiencias_bp)
app.register_blueprint(formacao_bp)

# CONFIGURAÇÃO DE E-MAIL (Exemplo Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'direct.ti.tec@gmail.com'
app.config['MAIL_PASSWORD'] = 'xbtx motn zyrk xibq' # Use senha de app, não a senha comum
app.config['MAIL_DEFAULT_SENDER'] = 'direct.ti.tec@gmail.com'

mail = Mail(app) # Inicializa o motor de e-mail

# Injetar o objeto mail nas rotas se necessário, ou importar direto
app.extensions['mail'] = mail

# Informações base da DIRECTI / Sebastião
INFO_BASE = {
    'nome': 'DIRECT TI SOLUÇÕES EM TECNOLOGIA LTDA',
    'especialista': 'SEBASTIÃO OLIVEIRA',
    'cargo': 'Analista de Sistemas Sênior & Arquiteto de Software',
    'resumo':'Analista de Sistemas com sólida trajetória e mais de 20 anos de experiência em desenvolvimento Full-stack e arquitetura de sistemas de grande escala. Especialista na sustentação e modernização de ecossistemas legados (ASP Classic) e liderança técnica em projetos críticos. Expertise em performance SQL e Business Intelligence.',
    'contato': {
        'local': 'Rio de Janeiro – RJ',
        'telefone': '(41) 99911-3960',
        'email': 'direct.ti.tec@gmail.com',
        'linkedin': 'linkedin.com/in/sebastião-oliveira-53346833'
    }
}

# Injetar INFO_BASE automaticamente em todos os templates
@app.context_processor
def inject_info():
    return dict(INFO_BASE=INFO_BASE)

# Registro dos módulos (Blueprints)
app.register_blueprint(empresa_bp)   # Cuida da Home (/)
app.register_blueprint(curriculo_bp)  # Cuida do Sobre (/sobre)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Aqui você pode enviar um log ou e-mail para si mesmo avisando do erro
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)