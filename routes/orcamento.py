from flask import Blueprint, request, jsonify
from src.models.orcamento import db, Transacao

orcamento_bp = Blueprint('orcamento', __name__)

# Listar todas as transações
@orcamento_bp.route('/transacoes', methods=['GET'])
def get_transacoes():
    mes = request.args.get('mes')  # Filtrar por mês, se fornecido
    if mes:
        transacoes = Transacao.query.filter_by(mes=mes).all()
    else:
        transacoes = Transacao.query.all()
    return jsonify([t.to_dict() for t in transacoes])

# Obter uma transação específica
@orcamento_bp.route('/transacoes/<int:id>', methods=['GET'])
def get_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    return jsonify(transacao.to_dict())

# Criar uma nova transação
@orcamento_bp.route('/transacoes', methods=['POST'])
def create_transacao():
    data = request.get_json()
    nova_transacao = Transacao(
        categoria=data['categoria'],
        valor=data['valor'],
        mes=data['mes'],
        status=data.get('status'),
        tipo=data['tipo']
    )
    db.session.add(nova_transacao)
    db.session.commit()
    return jsonify(nova_transacao.to_dict()), 201

# Atualizar uma transação existente
@orcamento_bp.route('/transacoes/<int:id>', methods=['PUT'])
def update_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    data = request.get_json()
    transacao.categoria = data.get('categoria', transacao.categoria)
    transacao.valor = data.get('valor', transacao.valor)
    transacao.mes = data.get('mes', transacao.mes)
    transacao.status = data.get('status', transacao.status)
    transacao.tipo = data.get('tipo', transacao.tipo)
    db.session.commit()
    return jsonify(transacao.to_dict())

# Deletar uma transação
@orcamento_bp.route('/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    return jsonify({'message': 'Transação deletada com sucesso'}), 200

# Obter resumo mensal (receitas, despesas, saldo)
@orcamento_bp.route('/resumo/<string:mes>', methods=['GET'])
def get_resumo(mes):
    transacoes = Transacao.query.filter_by(mes=mes).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
    saldo = receitas - despesas
    return jsonify({
        'mes': mes,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo
    })

