import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configurar banco de dados persistente
db_path = os.path.join(os.environ.get("RENDER_DISK_PATH", "/tmp"), 'controle_financeiro.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do Banco de Dados
class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(20), nullable=False)
    ano = db.Column(db.Integer, default=2025, nullable=False)
    status = db.Column(db.String(50), default='PENDENTE')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class Investimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Ação, Fundo, Cripto, etc
    valor_inicial = db.Column(db.Float, nullable=False)
    valor_atual = db.Column(db.Float, nullable=False)
    data_compra = db.Column(db.DateTime, default=datetime.utcnow)
    ano = db.Column(db.Integer, default=2025, nullable=False)

class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    valor_alvo = db.Column(db.Float, nullable=False)
    valor_atual = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_alvo = db.Column(db.DateTime)
    ano = db.Column(db.Integer, default=2025, nullable=False)
    status = db.Column(db.String(20), default='ATIVA')  # ATIVA, CONCLUIDA, CANCELADA

CATEGORIAS_DESPESAS = [
    "Tributos Igreja", "Aluguel", "Plano de Saúde",
    "Contas", "Cartão de Crédito", "Pagamento Amor",
    "Transporte", "Empréstimo", "Viagens", "Outros Gastos",
    "Alimentação", "Investimentos", "Carro"
]

CATEGORIAS_RECEITAS = ["Salário", "Bonificação"]

MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

# Endpoints de Transações
@app.route('/api/resumo/<int:ano>/<mes>', methods=['GET'])
def get_resumo(ano, mes):
    transacoes = Transacao.query.filter_by(mes=mes.upper(), ano=ano).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
    return jsonify({'receitas': receitas, 'despesas': despesas, 'saldo': receitas - despesas})

@app.route('/api/resumo/<mes>', methods=['GET'])
def get_resumo_ano_atual(mes):
    ano_atual = datetime.now().year
    return get_resumo(ano_atual, mes)

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    mes_param = request.args.get('mes', 'JANEIRO').upper()
    ano_param = request.args.get('ano', datetime.now().year, type=int)
    transacoes = Transacao.query.filter(
        Transacao.mes == mes_param,
        Transacao.ano == ano_param,
        Transacao.valor > 0
    ).order_by(Transacao.id.desc()).all()
    return jsonify([{
        'id': t.id,
        'categoria': t.categoria,
        'valor': t.valor,
        'tipo': t.tipo,
        'mes': t.mes,
        'ano': t.ano,
        'status': t.status
    } for t in transacoes])

@app.route('/api/transacoes', methods=['POST'])
def add_transacao():
    data = request.json
    ano = data.get('ano', datetime.now().year)
    mes = data.get('mes', 'JANEIRO').upper()
    
    nova = Transacao(
        categoria=data['categoria'],
        valor=data['valor'],
        tipo=data['tipo'],
        mes=mes,
        ano=ano,
        status='RECEBIDO' if data['tipo'] == 'RECEITA' else 'PAGO'
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({'message': 'Transação adicionada com sucesso', 'id': nova.id}), 201

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    t = Transacao.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Transação removida com sucesso'})

# Endpoints de Investimentos
@app.route('/api/investimentos', methods=['GET'])
def get_investimentos():
    ano_param = request.args.get('ano', datetime.now().year, type=int)
    investimentos = Investimento.query.filter_by(ano=ano_param).all()
    return jsonify([{
        'id': i.id,
        'nome': i.nome,
        'tipo': i.tipo,
        'valor_inicial': i.valor_inicial,
        'valor_atual': i.valor_atual,
        'ganho': i.valor_atual - i.valor_inicial,
        'rentabilidade': ((i.valor_atual - i.valor_inicial) / i.valor_inicial * 100) if i.valor_inicial > 0 else 0,
        'data_compra': i.data_compra.isoformat()
    } for i in investimentos])

@app.route('/api/investimentos', methods=['POST'])
def add_investimento():
    data = request.json
    ano = data.get('ano', datetime.now().year)
    
    novo = Investimento(
        nome=data['nome'],
        tipo=data['tipo'],
        valor_inicial=data['valor_inicial'],
        valor_atual=data['valor_inicial'],
        ano=ano
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({'message': 'Investimento adicionado com sucesso', 'id': novo.id}), 201

@app.route('/api/investimentos/<int:id>', methods=['PUT'])
def update_investimento(id):
    inv = Investimento.query.get_or_404(id)
    data = request.json
    inv.valor_atual = data.get('valor_atual', inv.valor_atual)
    db.session.commit()
    return jsonify({'message': 'Investimento atualizado com sucesso'})

@app.route('/api/investimentos/<int:id>', methods=['DELETE'])
def delete_investimento(id):
    inv = Investimento.query.get_or_404(id)
    db.session.delete(inv)
    db.session.commit()
    return jsonify({'message': 'Investimento removido com sucesso'})

# Endpoints de Metas
@app.route('/api/metas', methods=['GET'])
def get_metas():
    ano_param = request.args.get('ano', datetime.now().year, type=int)
    metas = Meta.query.filter_by(ano=ano_param).all()
    return jsonify([{
        'id': m.id,
        'nome': m.nome,
        'descricao': m.descricao,
        'valor_alvo': m.valor_alvo,
        'valor_atual': m.valor_atual,
        'progresso': (m.valor_atual / m.valor_alvo * 100) if m.valor_alvo > 0 else 0,
        'status': m.status,
        'data_alvo': m.data_alvo.isoformat() if m.data_alvo else None
    } for m in metas])

@app.route('/api/metas', methods=['POST'])
def add_meta():
    data = request.json
    ano = data.get('ano', datetime.now().year)
    
    nova = Meta(
        nome=data['nome'],
        descricao=data.get('descricao', ''),
        valor_alvo=data['valor_alvo'],
        ano=ano,
        status='ATIVA'
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({'message': 'Meta adicionada com sucesso', 'id': nova.id}), 201

@app.route('/api/metas/<int:id>', methods=['PUT'])
def update_meta(id):
    meta = Meta.query.get_or_404(id)
    data = request.json
    meta.valor_atual = data.get('valor_atual', meta.valor_atual)
    meta.status = data.get('status', meta.status)
    db.session.commit()
    return jsonify({'message': 'Meta atualizada com sucesso'})

@app.route('/api/metas/<int:id>', methods=['DELETE'])
def delete_meta(id):
    meta = Meta.query.get_or_404(id)
    db.session.delete(meta)
    db.session.commit()
    return jsonify({'message': 'Meta removida com sucesso'})

# Endpoint para obter anos disponíveis
@app.route('/api/anos', methods=['GET'])
def get_anos():
    anos = db.session.query(Transacao.ano).distinct().all()
    anos_list = sorted([a[0] for a in anos] + [datetime.now().year])
    return jsonify({'anos': list(set(anos_list))})

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': db_path})

# Inicializar banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
