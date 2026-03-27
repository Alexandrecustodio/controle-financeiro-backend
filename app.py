import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_path = os.path.join(os.environ.get("RENDER_DISK_PATH", "/tmp"), 'controle_financeiro.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='PENDENTE')

CATEGORIAS_DESPESAS = [
    "Tributos Igreja", "Aluguel", "Plano de Saúde / Remedios",
    "Contas Agua / Luz / Internet", "Cartão de Credito", "Pagamento Amor",
    "Transporte", "Emprestimo Cartão", "Viagens", "Outros Gastos",
    "Alimentação", "Investimentos", "Carro"
]
MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

@app.route('/api/resumo/<mes>', methods=['GET'])
def get_resumo(mes):
    transacoes = Transacao.query.filter_by(mes=mes.upper()).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
    return jsonify({'receitas': receitas, 'despesas': despesas, 'saldo': receitas - despesas})

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    mes_param = request.args.get('mes', 'JANEIRO').upper()
    transacoes = Transacao.query.filter(Transacao.mes == mes_param, Transacao.valor > 0).order_by(Transacao.id.desc()).all()
    return jsonify([{'id': t.id, 'categoria': t.categoria, 'valor': t.valor, 'tipo': t.tipo, 'mes': t.mes, 'status': t.status} for t in transacoes])

@app.route('/api/transacoes', methods=['POST'])
def add_transacao():
    data = request.json
    # Verifica se já existe uma transação com valor 0 para essa categoria e mês
    transacao_existente = Transacao.query.filter_by(categoria=data['categoria'], mes=data['mes'].upper(), tipo='DESPESA').first()
    if transacao_existente and transacao_existente.valor == 0:
        transacao_existente.valor = data['valor']
        db.session.commit()
        return jsonify({'message': 'Transação atualizada com sucesso'}), 200
    else:
        nova = Transacao(
            categoria=data['categoria'],
            valor=data['valor'],
            tipo=data['tipo'],
            mes=data['mes'].upper(),
            status='RECEBIDO' if data['tipo'] == 'RECEITA' else 'PAGO'
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({'message': 'Transação adicionada com sucesso'}), 201

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    t = Transacao.query.get_or_404(id)
    # Em vez de deletar, zera o valor se for uma despesa das categorias padrão
    if t.tipo == 'DESPESA' and t.categoria in CATEGORIAS_DESPESAS:
        t.valor = 0
    else:
        db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Transação removida com sucesso'})

with app.app_context():
    db.create_all()
    if Transacao.query.count() == 0:
        initial_data = []
        for mes in MESES:
            for cat in CATEGORIAS_DESPESAS:
                initial_data.append(Transacao(categoria=cat, valor=0.0, tipo='DESPESA', mes=mes, status='PENDENTE'))
        db.session.bulk_save_objects(initial_data)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
