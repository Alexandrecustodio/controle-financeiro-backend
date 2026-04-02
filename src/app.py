import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
CORS(app)

# Configurar banco de dados PostgreSQL do Supabase
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Fallback para SQLite local se a variável não estiver definida
    db_path = os.path.join(os.environ.get("RENDER_DISK_PATH", "/tmp"), 'controle_financeiro.db')
    DATABASE_URL = f'sqlite:///{db_path}'
else:
    # Converter postgresql:// para postgresql+psycopg2://
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
db = SQLAlchemy(app)

# Modelos do Banco de Dados
class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.String(500), nullable=False)

class Transacao(db.Model):
    __tablename__ = 'transacao'
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(20), nullable=False)
    ano = db.Column(db.Integer, default=2026, nullable=False)
    status = db.Column(db.String(50), default='PENDENTE')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    parcela_info = db.Column(db.String(100))
    grupo_parcelas = db.Column(db.String(100))

class Investimento(db.Model):
    __tablename__ = 'investimento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    valor_inicial = db.Column(db.Float, nullable=False)
    valor_atual = db.Column(db.Float, nullable=False)
    data_compra = db.Column(db.DateTime, default=datetime.utcnow)
    ano = db.Column(db.Integer, default=2026, nullable=False)

class Meta(db.Model):
    __tablename__ = 'meta'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    valor_alvo = db.Column(db.Float, nullable=False)
    valor_atual = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_alvo = db.Column(db.DateTime)
    ano = db.Column(db.Integer, default=2026, nullable=False)
    status = db.Column(db.String(20), default='ATIVA')

CATEGORIAS_DESPESAS = [
    "Tributos Igreja", "Aluguel", "Plano de Saúde",
    "Contas", "Cartão de Crédito", "Pagamento Amor",
    "Transporte", "Empréstimo", "Viagens", "Outros Gastos",
    "Alimentação", "Investimentos", "Carro"
]

CATEGORIAS_RECEITAS = ["Salário", "Bonificação"]

MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

def get_proximo_mes(mes_atual, ano_atual, meses_avancar=1):
    """Calcula o próximo mês e ano após avançar um número de meses."""
    meses_dict = {m: i for i, m in enumerate(MESES)}
    mes_index = meses_dict.get(mes_atual.upper(), 0)
    
    novo_index = mes_index + meses_avancar
    novo_ano = ano_atual + (novo_index // 12)
    novo_mes_index = novo_index % 12
    
    return MESES[novo_mes_index], novo_ano

# Endpoints de Configuração
@app.route('/api/config/nome-planilha', methods=['GET'])
def get_nome_planilha():
    try:
        config = Configuracao.query.filter_by(chave='nome_planilha').first()
        nome = config.valor if config else "Meu Orçamento"
        return jsonify({'nome': nome})
    except Exception as e:
        return jsonify({'nome': 'Meu Orçamento', 'erro': str(e)})

@app.route('/api/config/nome-planilha', methods=['POST'])
def set_nome_planilha():
    try:
        data = request.json
        nome = data.get('nome', 'Meu Orçamento')
        
        config = Configuracao.query.filter_by(chave='nome_planilha').first()
        if config:
            config.valor = nome
        else:
            config = Configuracao(chave='nome_planilha', valor=nome)
        
        db.session.add(config)
        db.session.commit()
        return jsonify({'sucesso': True, 'nome': nome})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Endpoints de Transações
@app.route('/api/resumo/<int:ano>/<mes>', methods=['GET'])
def get_resumo(ano, mes):
    try:
        transacoes = Transacao.query.filter_by(mes=mes.upper(), ano=ano).all()
        receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
        despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
        return jsonify({'receitas': receitas, 'despesas': despesas, 'saldo': receitas - despesas})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    try:
        mes_param = request.args.get('mes', 'JANEIRO').upper()
        ano_param = request.args.get('ano', 2026, type=int)
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
            'status': t.status,
            'parcela_info': t.parcela_info
        } for t in transacoes])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/transacoes', methods=['POST'])
def criar_transacao():
    try:
        data = request.json
        categoria = data.get('categoria')
        valor = float(data.get('valor', 0))
        tipo = data.get('tipo', 'DESPESA')
        mes = data.get('mes', 'JANEIRO').upper()
        ano = int(data.get('ano', 2026))
        num_parcelas = int(data.get('num_parcelas', 1))
        nome_compra = data.get('nome_compra', categoria)
        
        if num_parcelas > 1:
            grupo_id = str(uuid.uuid4())
            valor_parcela = valor / num_parcelas
            
            for i in range(num_parcelas):
                mes_parcela, ano_parcela = get_proximo_mes(mes, ano, i)
                parcela_info = f"{nome_compra} - Parcela {i+1}/{num_parcelas}"
                
                transacao = Transacao(
                    categoria=categoria,
                    valor=valor_parcela,
                    tipo=tipo,
                    mes=mes_parcela,
                    ano=ano_parcela,
                    parcela_info=parcela_info,
                    grupo_parcelas=grupo_id
                )
                db.session.add(transacao)
        else:
            transacao = Transacao(
                categoria=categoria,
                valor=valor,
                tipo=tipo,
                mes=mes,
                ano=ano
            )
            db.session.add(transacao)
        
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Transação criada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/transacoes/<int:transacao_id>', methods=['DELETE'])
def deletar_transacao(transacao_id):
    try:
        transacao = Transacao.query.get(transacao_id)
        if transacao:
            db.session.delete(transacao)
            db.session.commit()
            return jsonify({'sucesso': True})
        return jsonify({'erro': 'Transação não encontrada'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Endpoints de Investimentos
@app.route('/api/investimentos', methods=['GET'])
def get_investimentos():
    try:
        ano_param = request.args.get('ano', 2026, type=int)
        investimentos = Investimento.query.filter_by(ano=ano_param).all()
        return jsonify([{
            'id': i.id,
            'nome': i.nome,
            'tipo': i.tipo,
            'valor_inicial': i.valor_inicial,
            'valor_atual': i.valor_atual,
            'rentabilidade': ((i.valor_atual - i.valor_inicial) / i.valor_inicial * 100) if i.valor_inicial > 0 else 0
        } for i in investimentos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos', methods=['POST'])
def criar_investimento():
    try:
        data = request.json
        investimento = Investimento(
            nome=data.get('nome'),
            tipo=data.get('tipo'),
            valor_inicial=float(data.get('valor_inicial', 0)),
            valor_atual=float(data.get('valor_atual', 0)),
            ano=int(data.get('ano', 2026))
        )
        db.session.add(investimento)
        db.session.commit()
        return jsonify({'sucesso': True, 'id': investimento.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos/<int:inv_id>', methods=['PUT'])
def atualizar_investimento(inv_id):
    try:
        investimento = Investimento.query.get(inv_id)
        if investimento:
            data = request.json
            investimento.valor_atual = float(data.get('valor_atual', investimento.valor_atual))
            db.session.commit()
            return jsonify({'sucesso': True})
        return jsonify({'erro': 'Investimento não encontrado'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos/<int:inv_id>', methods=['DELETE'])
def deletar_investimento(inv_id):
    try:
        investimento = Investimento.query.get(inv_id)
        if investimento:
            db.session.delete(investimento)
            db.session.commit()
            return jsonify({'sucesso': True})
        return jsonify({'erro': 'Investimento não encontrado'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Endpoints de Metas
@app.route('/api/metas', methods=['GET'])
def get_metas():
    try:
        ano_param = request.args.get('ano', 2026, type=int)
        metas = Meta.query.filter_by(ano=ano_param).all()
        return jsonify([{
            'id': m.id,
            'nome': m.nome,
            'descricao': m.descricao,
            'valor_alvo': m.valor_alvo,
            'valor_atual': m.valor_atual,
            'progresso': (m.valor_atual / m.valor_alvo * 100) if m.valor_alvo > 0 else 0,
            'status': m.status
        } for m in metas])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas', methods=['POST'])
def criar_meta():
    try:
        data = request.json
        meta = Meta(
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            valor_alvo=float(data.get('valor_alvo', 0)),
            valor_atual=float(data.get('valor_atual', 0)),
            ano=int(data.get('ano', 2026))
        )
        db.session.add(meta)
        db.session.commit()
        return jsonify({'sucesso': True, 'id': meta.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas/<int:meta_id>', methods=['PUT'])
def atualizar_meta(meta_id):
    try:
        meta = Meta.query.get(meta_id)
        if meta:
            data = request.json
            meta.valor_atual = float(data.get('valor_atual', meta.valor_atual))
            db.session.commit()
            return jsonify({'sucesso': True})
        return jsonify({'erro': 'Meta não encontrada'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas/<int:meta_id>', methods=['DELETE'])
def deletar_meta(meta_id):
    try:
        meta = Meta.query.get(meta_id)
        if meta:
            db.session.delete(meta)
            db.session.commit()
            return jsonify({'sucesso': True})
        return jsonify({'erro': 'Meta não encontrada'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': 'connected'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
