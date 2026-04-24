from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    dados_curriculo = {
        'nome': 'Sebastiao G. Oliveira',
        'cargo': 'Desenvolvedor Full Stack',
        'habilidades': ['Python', 'Flask', 'PostgreSQL', 'HTML5']
    }
    return render_template('index.html', info=dados_curriculo)