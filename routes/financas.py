from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db_cursor
from datetime import datetime

financas_bp = Blueprint('financas', __name__, url_prefix='/financas')

@financas_bp.route('/adicionar-gasto', methods=['GET', 'POST'])
def adicionar_gasto():
    # ID fixo por enquanto (até integrarmos o login)
    usuario_id = 1 

    if request.method == 'POST':
        descricao = request.form.get('descricao')
        categoria_id = request.form.get('categoria_id')
        valor_est = request.form.get('valor_estimado').replace(',', '.')
        data_venc = request.form.get('data_vencimento')
        
        # Extrair mês e ano da data de vencimento para facilitar filtros
        dt = datetime.strptime(data_venc, '%Y-%m-%d')
        mes = dt.month
        ano = dt.year

        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO FIN_Lancamentos 
                (UsuarioId, CategoriaId, Descricao, ValorEstimado, DataVencimento, MesReferencia, AnoReferencia, Pago)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (usuario_id, categoria_id, descricao, valor_est, data_venc, mes, ano))
        
        flash('Gasto adicionado com sucesso!', 'success')
        return redirect(url_for('financas.dashboard'))

    # GET: Busca categorias para preencher o Select do formulário
    with get_db_cursor() as cursor:
        cursor.execute("SELECT CategoriaId, Nome FROM FIN_Categorias WHERE UsuarioId = ?", (usuario_id,))
        categorias = cursor.fetchall()

    return render_template('financas/form_gasto.html', categorias=categorias)

@financas_bp.route('/')
@financas_bp.route('/dashboard')
def dashboard():
    usuario_id = 1
    hoje = datetime.now()
    
    # Captura mês e ano da URL ou usa o atual como padrão
    mes_sel = request.args.get('mes', hoje.month, type=int)
    ano_sel = request.args.get('ano', hoje.year, type=int)

    # Lista para o <select> do HTML
    meses_lista = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    # Lista de anos (ano atual, 1 anterior e 1 próximo)
    anos_lista = [hoje.year - 1, hoje.year]

    with get_db_cursor() as cursor:
        # 1. Busca Resumo de Rendas
        cursor.execute("""
            SELECT SUM(ValorReal) as TotalReal, SUM(ValorPrevisto) as TotalPrevisto 
            FROM FIN_Rendas WHERE UsuarioId = ? AND MesReferencia = ? AND AnoReferencia = ?
        """, (usuario_id, mes_sel, ano_sel))
        res_renda = cursor.fetchone()
        total_renda = float(res_renda[0]) if res_renda and res_renda[0] else 0.0

        # 2. Busca Resumo de Despesas (Pagos vs Pendentes)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Pago = 1 THEN ValorReal ELSE 0 END) as Pagas,
                SUM(CASE WHEN Pago = 0 THEN ValorEstimado ELSE 0 END) as Pendentes
            FROM FIN_Lancamentos WHERE UsuarioId = ? AND MesReferencia = ? AND AnoReferencia = ?
        """, (usuario_id, mes_sel, ano_sel))
        res_despesas = cursor.fetchone()
        contas_pagas = float(res_despesas[0]) if res_despesas and res_despesas[0] else 0.0
        contas_pendentes = float(res_despesas[1]) if res_despesas and res_despesas[1] else 0.0

        # 3. Busca Lançamentos Detalhados (Para a tabela abaixo do resumo)
        cursor.execute("""
            SELECT L.*, C.Nome as CategoriaNome, C.CorHex 
            FROM FIN_Lancamentos L
            JOIN FIN_Categorias C ON L.CategoriaId = C.CategoriaId
            WHERE L.UsuarioId = ? AND L.MesReferencia = ? AND L.AnoReferencia = ?
            ORDER BY L.DataVencimento ASC
        """, (usuario_id, mes_sel, ano_sel))
        lancamentos = cursor.fetchall()

    # Cálculos Automáticos (Lógica da Planilha)
    saldo_total = total_renda - contas_pagas
    sobra_prevista = total_renda - contas_pagas - contas_pendentes

    return render_template('financas/dashboard.html', 
                           meses=meses_lista,
                           anos=anos_lista,
                           mes=mes_sel, ano=ano_sel,
                           renda=total_renda,                            
                           pagas=contas_pagas, 
                           pendentes=contas_pendentes,
                           saldo_total=saldo_total,
                           sobra=sobra_prevista,
                           lancamentos=lancamentos)

@financas_bp.route('/baixar-gasto/<int:id>', methods=['POST'])
def baixar_gasto(id):
    usuario_id = 1 #
    
    with get_db_cursor() as cursor:
        # Primeiro, pegamos o valor estimado para preencher o real na hora da baixa
        cursor.execute("SELECT ValorEstimado FROM FIN_Lancamentos WHERE LancamentoId = ? AND UsuarioId = ?", (id, usuario_id))
        gasto = cursor.fetchone()
        
        if gasto:
            cursor.execute("""
                UPDATE FIN_Lancamentos 
                SET Pago = 1, ValorReal = ValorEstimado 
                WHERE LancamentoId = ? AND UsuarioId = ?
            """, (id, usuario_id))
            return {"success": True}, 200 # Retorno JSON para o JavaScript
            
    return {"success": False}, 400

@financas_bp.route('/atualizar-valor-real/<int:id>', methods=['POST'])
def atualizar_valor_real(id):
    usuario_id = 1
    # Captura o valor enviado pelo JSON
    dados = request.get_json()
    novo_valor = dados.get('valor').replace(',', '.') # Sanitização básica
    
    try:
        valor_float = float(novo_valor)
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE FIN_Lancamentos 
                SET ValorReal = ?, Pago = CASE WHEN ? > 0 THEN 1 ELSE Pago END
                WHERE LancamentoId = ? AND UsuarioId = ?
            """, (valor_float, valor_float, id, usuario_id))
            
        return {"success": True}, 200
    except ValueError:
        return {"success": False, "message": "Valor inválido"}, 400
    
@financas_bp.route('/rendas', methods=['GET', 'POST'])
def gerenciar_rendas():
    usuario_id = 1
    hoje = datetime.now()

    # Captura mes/ano da URL ou usa o atual como padrão
    mes = request.args.get('mes', hoje.month, type=int)
    ano = request.args.get('ano', hoje.year, type=int)

    if request.method == 'POST':
        descricao = request.form.get('descricao')
        v_previsto = request.form.get('valor_previsto', '0').replace(',', '.')
        v_real = request.form.get('valor_real', '0').replace(',', '.')
        data_receb = request.form.get('data_recebimento')
        
        # 2. CONVERSÃO CRUCIAL: Se a string for vazia ou inválida, vira 0.0
        # Isso impede o erro de 'nvarchar to numeric' no SQL Server
        try:
            valor_previsto = float(v_previsto) if v_previsto else 0.0
            valor_real = float(v_real) if v_real else 0.0
        except ValueError:
            valor_previsto = 0.0
            valor_real = 0.0

        data_receb = request.form.get('data_recebimento')
        dt = datetime.strptime(data_receb, '%Y-%m-%d')
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO FIN_Rendas 
                (UsuarioId, Descricao, ValorPrevisto, ValorReal, DataRecebimento, MesReferencia, AnoReferencia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (usuario_id, descricao, valor_previsto, valor_real, data_receb, dt.month, dt.year))
        
        flash('Renda registrada com sucesso!', 'success')
        return redirect(url_for('financas.dashboard'))

    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM FIN_Rendas 
            WHERE UsuarioId = ? AND MesReferencia = ? AND AnoReferencia = ?
        """, (usuario_id, mes, ano))
        rendas = cursor.fetchall()

    return render_template('financas/rendas.html', rendas=rendas, mes=mes, ano=ano)

@financas_bp.route('/deletar-renda/<int:id>', methods=['POST'])
def deletar_renda(id):
    usuario_id = 1
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM FIN_Rendas WHERE RendaId = ? AND UsuarioId = ?", (id, usuario_id))
    return {"success": True}, 200

@financas_bp.route('/editar-renda/<int:id>', methods=['POST'])
def editar_renda(id):
    usuario_id = 1
    dados = request.get_json()
    
    # Tratamento para garantir que o SQL receba o tipo correto
    try:
        desc = dados.get('descricao')
        v_prev = float(dados.get('valor_previsto').replace(',', '.'))
        v_real = float(dados.get('valor_real').replace(',', '.'))
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE FIN_Rendas 
                SET Descricao = ?, ValorPrevisto = ?, ValorReal = ?
                WHERE RendaId = ? AND UsuarioId = ?
            """, (desc, v_prev, v_real, id, usuario_id))
        return {"success": True}, 200
    except Exception as e:
        return {"success": False, "message": str(e)}, 400
    
@financas_bp.route('/deletar-gasto/<int:id>', methods=['POST'])
def deletar_gasto(id):
    usuario_id = 1
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM FIN_Lancamentos WHERE LancamentoId = ? AND UsuarioId = ?", (id, usuario_id))
    return {"success": True}, 200