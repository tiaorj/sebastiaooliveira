# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    dados_curriculo = {
        'nome': 'Sebastião G. Oliveira',
        'cargo': 'Analista de Sistemas Sr',
        'habilidades': ['Python', 'Flask', 'PostgreSQL', 'HTML5']
    }
    return render_template('index.html', info=dados_curriculo)

if __name__ == '__main__':
    app.run(debug=True)