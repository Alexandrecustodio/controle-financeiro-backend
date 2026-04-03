import os
import json
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Configuração do GitHub
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO_OWNER = 'Alexandrecustodio'
GITHUB_REPO_NAME = 'controle-financeiro-backend'
GITHUB_BRANCH = 'main'
GITHUB_API_URL = 'https://api.github.com'

def get_github_file(filename):
    """Lê um arquivo JSON do GitHub."""
    try:
        url = f'{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/data/{filename}?ref={GITHUB_BRANCH}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3.raw',
            'User-Agent': 'FinanceApp'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 404:
            return None
        else:
            print(f'Erro ao ler {filename}: {response.status_code}')
            return None
    except Exception as e:
        print(f'Erro ao ler arquivo do GitHub: {e}')
        return None

def save_github_file(filename, data):
    """Salva um arquivo JSON no GitHub."""
    try:
        url = f'{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/data/{filename}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'FinanceApp'
        }
        
        # Primeiro, tenta obter o arquivo existente para pegar o SHA
        get_response = requests.get(url, headers=headers, timeout=10)
        sha = None
        if get_response.status_code == 200:
            sha = get_response.json().get('sha')
        
        # Codifica o conteúdo em base64
        content_str = json.dumps(data, indent=2, ensure_ascii=False)
        content_encoded = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
        
        payload = {
            'message': f'Update {filename} - {datetime.now().isoformat()}',
            'content': content_encoded,
            'branch': GITHUB_BRANCH
        }
        
        if sha:
            payload['sha'] = sha
        
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f'✓ Arquivo {filename} salvo com sucesso')
            return True
        else:
            print(f'✗ Erro ao salvar {filename}: {response.status_code}')
            print(f'Resposta: {response.text}')
            return False
    except Exception as e:
        print(f'✗ Erro ao salvar arquivo no GitHub: {e}')
        return False

def get_or_create_file(filename, default_data):
    """Obtém um arquivo ou cria com dados padrão se não existir."""
    data = get_github_file(filename)
    if data is None:
        # Arquivo não existe, cria com dados padrão
        save_github_file(filename, default_data)
        return default_data
    return data

# Endpoints de Configuração
@app.route('/api/config/nome-planilha', methods=['GET'])
def get_nome_planilha():
    try:
        config = get_or_create_file('config.json', {'nome_planilha': 'Meu Orçamento'})
        nome = config.get('nome_planilha', 'Meu Orçamento')
        return jsonify({'nome': nome})
    except Exception as e:
        print(f'Erro em get_nome_planilha: {e}')
        return jsonify({'nome': 'Meu Orçamento', 'erro': str(e)})

@app.route('/api/config/nome-planilha', methods=['POST'])
def set_nome_planilha():
    try:
        data = request.json
        nome = data.get('nome', 'Meu Orçamento')
        
        config = get_or_create_file('config.json', {'nome_planilha': 'Meu Orçamento'})
        config['nome_planilha'] = nome
        
        if save_github_file('config.json', config):
            return jsonify({'sucesso': True, 'nome': nome})
        else:
            return jsonify({'erro': 'Erro ao salvar configuração'}), 500
    except Exception as e:
        print(f'Erro em set_nome_planilha: {e}')
        return jsonify({'erro': str(e)}), 500

# Endpoints de Transações
@app.route('/api/resumo/<int:ano>/<mes>', methods=['GET'])
def get_resumo(ano, mes):
    try:
        transacoes_data = get_or_create_file('transacoes.json', {'items': []})
        transacoes_filtradas = [
            t for t in transacoes_data.get('items', [])
            if t.get('mes') == mes.upper() and t.get('ano') == ano
        ]
        
        receitas = sum(t.get('valor', 0) for t in transacoes_filtradas if t.get('tipo') == 'RECEITA')
        despesas = sum(t.get('valor', 0) for t in transacoes_filtradas if t.get('tipo') == 'DESPESA')
        
        return jsonify({'receitas': receitas, 'despesas': despesas, 'saldo': receitas - despesas})
    except Exception as e:
        print(f'Erro em get_resumo: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    try:
        mes_param = request.args.get('mes', 'JANEIRO').upper()
        ano_param = request.args.get('ano', 2026, type=int)
        
        transacoes_data = get_or_create_file('transacoes.json', {'items': []})
        transacoes = [
            t for t in transacoes_data.get('items', [])
            if t.get('mes') == mes_param and t.get('ano') == ano_param and t.get('valor', 0) > 0
        ]
        
        return jsonify(transacoes)
    except Exception as e:
        print(f'Erro em get_transacoes: {e}')
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
        
        print(f'Criando transação: {categoria} - R$ {valor} - {tipo}')
        
        transacoes_data = get_or_create_file('transacoes.json', {'items': []})
        
        MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
        
        def get_proximo_mes(mes_atual, ano_atual, meses_avancar=1):
            meses_dict = {m: i for i, m in enumerate(MESES)}
            mes_index = meses_dict.get(mes_atual, 0)
            novo_index = mes_index + meses_avancar
            novo_ano = ano_atual + (novo_index // 12)
            novo_mes_index = novo_index % 12
            return MESES[novo_mes_index], novo_ano
        
        if num_parcelas > 1:
            grupo_id = str(uuid.uuid4())
            valor_parcela = valor / num_parcelas
            
            for i in range(num_parcelas):
                mes_parcela, ano_parcela = get_proximo_mes(mes, ano, i)
                parcela_info = f"{nome_compra} - Parcela {i+1}/{num_parcelas}"
                
                transacao = {
                    'id': str(uuid.uuid4()),
                    'categoria': categoria,
                    'valor': round(valor_parcela, 2),
                    'tipo': tipo,
                    'mes': mes_parcela,
                    'ano': ano_parcela,
                    'parcela_info': parcela_info,
                    'grupo_parcelas': grupo_id,
                    'data_criacao': datetime.now().isoformat()
                }
                transacoes_data['items'].append(transacao)
                print(f'  → Parcela {i+1}/{num_parcelas}: {mes_parcela}/{ano_parcela}')
        else:
            transacao = {
                'id': str(uuid.uuid4()),
                'categoria': categoria,
                'valor': round(valor, 2),
                'tipo': tipo,
                'mes': mes,
                'ano': ano,
                'data_criacao': datetime.now().isoformat()
            }
            transacoes_data['items'].append(transacao)
        
        if save_github_file('transacoes.json', transacoes_data):
            print(f'✓ Transação salva com sucesso!')
            return jsonify({'sucesso': True, 'mensagem': 'Transação criada com sucesso!'})
        else:
            print(f'✗ Erro ao salvar transação no GitHub')
            return jsonify({'erro': 'Erro ao salvar transação no GitHub'}), 500
    except Exception as e:
        print(f'✗ Erro em criar_transacao: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/transacoes/<transacao_id>', methods=['DELETE'])
def deletar_transacao(transacao_id):
    try:
        transacoes_data = get_or_create_file('transacoes.json', {'items': []})
        transacoes_data['items'] = [
            t for t in transacoes_data.get('items', [])
            if t.get('id') != transacao_id
        ]
        
        if save_github_file('transacoes.json', transacoes_data):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao deletar transação'}), 500
    except Exception as e:
        print(f'Erro em deletar_transacao: {e}')
        return jsonify({'erro': str(e)}), 500

# Endpoints de Investimentos
@app.route('/api/investimentos', methods=['GET'])
def get_investimentos():
    try:
        ano_param = request.args.get('ano', 2026, type=int)
        investimentos_data = get_or_create_file('investimentos.json', {'items': []})
        investimentos = [
            i for i in investimentos_data.get('items', [])
            if i.get('ano') == ano_param
        ]
        
        for inv in investimentos:
            valor_inicial = inv.get('valor_inicial', 1)
            inv['rentabilidade'] = ((inv.get('valor_atual', 0) - valor_inicial) / valor_inicial * 100) if valor_inicial > 0 else 0
        
        return jsonify(investimentos)
    except Exception as e:
        print(f'Erro em get_investimentos: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos', methods=['POST'])
def criar_investimento():
    try:
        data = request.json
        investimentos_data = get_or_create_file('investimentos.json', {'items': []})
        
        investimento = {
            'id': str(uuid.uuid4()),
            'nome': data.get('nome'),
            'tipo': data.get('tipo'),
            'valor_inicial': float(data.get('valor_inicial', 0)),
            'valor_atual': float(data.get('valor_atual', 0)),
            'ano': int(data.get('ano', 2026)),
            'data_criacao': datetime.now().isoformat()
        }
        
        investimentos_data['items'].append(investimento)
        
        if save_github_file('investimentos.json', investimentos_data):
            return jsonify({'sucesso': True, 'id': investimento['id']})
        else:
            return jsonify({'erro': 'Erro ao salvar investimento'}), 500
    except Exception as e:
        print(f'Erro em criar_investimento: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos/<inv_id>', methods=['PUT'])
def atualizar_investimento(inv_id):
    try:
        data = request.json
        investimentos_data = get_or_create_file('investimentos.json', {'items': []})
        
        for inv in investimentos_data.get('items', []):
            if inv.get('id') == inv_id:
                inv['valor_atual'] = float(data.get('valor_atual', inv.get('valor_atual')))
                break
        
        if save_github_file('investimentos.json', investimentos_data):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao atualizar investimento'}), 500
    except Exception as e:
        print(f'Erro em atualizar_investimento: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/investimentos/<inv_id>', methods=['DELETE'])
def deletar_investimento(inv_id):
    try:
        investimentos_data = get_or_create_file('investimentos.json', {'items': []})
        investimentos_data['items'] = [
            i for i in investimentos_data.get('items', [])
            if i.get('id') != inv_id
        ]
        
        if save_github_file('investimentos.json', investimentos_data):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao deletar investimento'}), 500
    except Exception as e:
        print(f'Erro em deletar_investimento: {e}')
        return jsonify({'erro': str(e)}), 500

# Endpoints de Metas
@app.route('/api/metas', methods=['GET'])
def get_metas():
    try:
        ano_param = request.args.get('ano', 2026, type=int)
        metas_data = get_or_create_file('metas.json', {'items': []})
        metas = [
            m for m in metas_data.get('items', [])
            if m.get('ano') == ano_param
        ]
        
        for meta in metas:
            valor_alvo = meta.get('valor_alvo', 1)
            meta['progresso'] = (meta.get('valor_atual', 0) / valor_alvo * 100) if valor_alvo > 0 else 0
        
        return jsonify(metas)
    except Exception as e:
        print(f'Erro em get_metas: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas', methods=['POST'])
def criar_meta():
    try:
        data = request.json
        metas_data = get_or_create_file('metas.json', {'items': []})
        
        meta = {
            'id': str(uuid.uuid4()),
            'nome': data.get('nome'),
            'descricao': data.get('descricao'),
            'valor_alvo': float(data.get('valor_alvo', 0)),
            'valor_atual': float(data.get('valor_atual', 0)),
            'ano': int(data.get('ano', 2026)),
            'status': 'ATIVA',
            'data_criacao': datetime.now().isoformat()
        }
        
        metas_data['items'].append(meta)
        
        if save_github_file('metas.json', metas_data):
            return jsonify({'sucesso': True, 'id': meta['id']})
        else:
            return jsonify({'erro': 'Erro ao salvar meta'}), 500
    except Exception as e:
        print(f'Erro em criar_meta: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas/<meta_id>', methods=['PUT'])
def atualizar_meta(meta_id):
    try:
        data = request.json
        metas_data = get_or_create_file('metas.json', {'items': []})
        
        for meta in metas_data.get('items', []):
            if meta.get('id') == meta_id:
                meta['valor_atual'] = float(data.get('valor_atual', meta.get('valor_atual')))
                break
        
        if save_github_file('metas.json', metas_data):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao atualizar meta'}), 500
    except Exception as e:
        print(f'Erro em atualizar_meta: {e}')
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metas/<meta_id>', methods=['DELETE'])
def deletar_meta(meta_id):
    try:
        metas_data = get_or_create_file('metas.json', {'items': []})
        metas_data['items'] = [
            m for m in metas_data.get('items', [])
            if m.get('id') != meta_id
        ]
        
        if save_github_file('metas.json', metas_data):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao deletar meta'}), 500
    except Exception as e:
        print(f'Erro em deletar_meta: {e}')
        return jsonify({'erro': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    github_status = 'configured' if GITHUB_TOKEN else 'missing'
    return jsonify({
        'status': 'ok',
        'database': 'github',
        'github_token': github_status,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f'Iniciando servidor com GitHub Token: {"configurado" if GITHUB_TOKEN else "NÃO CONFIGURADO"}')
    app.run(debug=False, host='0.0.0.0', port=5000)
