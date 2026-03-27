import os
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados SQLite em /tmp para o Render
db_path = os.path.join('/tmp', 'orcamento.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Dados
class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # RECEITA ou DESPESA
    mes = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='A RECEBER')

# Dados Iniciais da Planilha
INITIAL_DATA = 

# Rotas da API
@app.route('/api/resumo/<mes>', methods=['GET'])
def get_resumo(mes):
    transacoes = Transacao.query.filter_by(mes=mes.upper()).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
    return jsonify({
        'receitas': receitas,
        'despesas': despesas,
        'saldo': receitas - despesas
    })

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    mes = request.args.get('mes', 'AGOSTO').upper()
    transacoes = Transacao.query.filter_by(mes=mes).all()
    return jsonify([{
        'id': t.id,
        'categoria': t.categoria,
        'valor': t.valor,
        'tipo': t.tipo,
        'mes': t.mes,
        'status': t.status
    } for t in transacoes])

@app.route('/api/transacoes', methods=['POST'])
def add_transacao():
    data = request.json
    nova = Transacao(
        categoria=data['categoria'],
        valor=data['valor'],
        tipo=data['tipo'],
        mes=data['mes'].upper(),
        status=data.get('status', 'A RECEBER')
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({'message': 'Sucesso'}), 201

@app.route('/api/transacoes/<int:id>', methods=['PUT'])
def update_transacao(id):
    t = Transacao.query.get_or_404(id)
    data = request.json
    t.categoria = data['categoria']
    t.valor = data['valor']
    t.tipo = data['tipo']
    t.status = data.get('status', t.status)
    db.session.commit()
    return jsonify({'message': 'Atualizado'})

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    t = Transacao.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Deletado'})

# Inicialização do Banco de Dados
with app.app_context():
    db.create_all()
    if Transacao.query.count() == 0:
        for item in INITIAL_DATA:
            t = Transacao(**item)
            db.session.add(t)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
