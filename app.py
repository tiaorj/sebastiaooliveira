# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    dados_curriculo = {
        'nome': 'SEBASTIÃO OLIVEIRA',
        'cargo': 'Analista de Sistemas Sênior & Arquiteto de Software',
        'contato': {
            'local': 'Rio de Janeiro – RJ',
            'telefone': '(41) 99911-3960',
            'email': 'tiaorj@gmail.com',
            'linkedin': 'linkedin.com/in/sebastião-oliveira-53346833'
        },
        'resumo': (
            "Analista de Sistemas Sênior & Arquiteto de Software com sólida trajetória e "
            "mais de 20 anos de experiência no desenvolvimento, manutenção e modernização "
            "de sistemas corporativos de grande porte. Especialista em ASP Classic, C# e SQL Server, "
            "com forte atuação em ecossistemas legados e Business Intelligence."
        ),
        'habilidades': [
            {'categoria': 'Desenvolvimento', 'itens': 'ASP Classic, C#, ASP.NET, VBScript, VB, Delphi, HTML5, CSS, Bootstrap, jQuery, Ajax.'},
            {'categoria': 'Banco de Dados', 'itens': 'SQL Server (Expert), Oracle, PostgreSQL, Performance Tuning, Modelagem de Dados.'},
            {'categoria': 'BI & Dados', 'itens': 'Power BI (Desktop/Service), Power Query, Linguagem M e DAX.'},
            {'categoria': 'Metodologias', 'itens': 'Git, Jira, Scrum, Kanban, APIs REST/SOAP.'}
        ],
        'experiencias': [
            {
                'id': 'bk_petrobras',
                'empresa': 'BK CONSULTORIA (PETROBRAS)',
                'periodo': '12/2022 – Presente',
                'cargo': 'Analista de Sistemas Sênior',
                'resumo_curto': 'Especialista em BI e Arquitetura de Dados Oracle.',
                'detalhes': [
                    'Desenvolvimento e manutenção de dashboards estratégicos no Power BI.',
                    'Modelagem e otimização de bancos de dados Oracle para grandes volumes.',
                    'Sustentação de sistemas em ASP Classic com integração via REST API.'
                ]
            },
            {
                'id': 'moot_lm',
                'empresa': 'MOOT (LM Mobilidade)',
                'periodo': '12/2024 – 04/2026',
                'cargo': 'Analista de Sistemas',
                'resumo_curto': 'Desenvolvimento Full-stack e Engenharia de Dados SQL Server.',
                'detalhes': [
                    'Criação de novos módulos e manutenção evolutiva em ASP Classic.',
                    'Utilização de Bootstrap, jQuery e AJAX para modernização de interface.',
                    'Design de banco de dados e desenvolvimento de Stored Procedures e Triggers complexas.',
                    'Trabalho em squads ágeis via JIRA e versionamento com GIT.'
                ]
            },
            {
                'id': 'easycarros_lead',
                'empresa': 'EASYCARROS (EURO IT)',
                'periodo': '01/2019 – 12/2024',
                'cargo': 'Tech Lead / Analista Sênior',
                'resumo_curto': 'Liderança técnica e modernização de ERP robusto.',
                'detalhes': [
                    'Coordenação técnica na modernização cross-browser eliminando dependência do IE.',
                    'Implementação de REDIS para gestão de sessões e refatoração de performance.',
                    'Redução de 20% no tempo de operação manual através de automação em SQL Server.',
                    'Arquitetura de integrações via REST API com sistemas de parceiros B2C.'
                ]
            },
            {
                'id': 'tim_celular',
                'empresa': 'TIM Celular S.A.',
                'periodo': '06/2018 – 01/2019',
                'cargo': 'Analista de Sistemas',
                'resumo_curto': 'Soluções de Intranet e automação comercial.',
                'detalhes': [
                    'Desenvolvimento de soluções de Intranet e Extranet.',
                    'Automação de processos comerciais utilizando C# e SQL Server.'
                ]
            },
            {
                'id': 'petrobras_juridico',
                'empresa': 'Petrobras',
                'periodo': '06/2012 – 01/2018',
                'cargo': 'Analista de Sistemas',
                'resumo_curto': 'Sustentação de sistemas jurídicos críticos.',
                'detalhes': [
                    'Sustentação de sistemas jurídicos críticos nível 3.',
                    'Modelagem de dados e relatórios complexos com Crystal Reports.',
                    'Uso de tecnologias legadas e modernas: VB6, VB.NET e C#.'
                ]
            }
        ],
        'formacao': [
            'Pós-Graduação – Análise, Projeto e Gerência de Sistemas - PUC-Rio (2009)',
            'Extensão: Especialização em Técnicas de Desenvolvimento - PUC-Rio (2007)',
            'Graduação: Tecnologia da Informação - Estácio de Sá (2007)'
        ]
    }
    return render_template('index.html', info=dados_curriculo)

if __name__ == '__main__':
    app.run(debug=True)