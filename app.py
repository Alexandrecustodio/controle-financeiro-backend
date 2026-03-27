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

# Dados Iniciais da Planilha (serão inseridos via script)INITIAL_DATA = [
  {
    "categoria": "Tributos Igreja",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Aluguel",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Plano de Saúde / Remedios",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Contas Agua / Luz / Internet",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Cartão de Credito",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Pagamento Amor",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Transporte",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Emprestimo Cartão",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Viagens",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Outros Gastos",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Alimentação",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Investimentos",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Carro",
    "valor": 0.0,
    "tipo": "DESPESA",
    "mes": "JANEIRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Salario",
    "valor": 6000.0,
    "tipo": "RECEITA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario",
    "valor": 6000.0,
    "tipo": "RECEITA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario",
    "valor": 6000.0,
    "tipo": "RECEITA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario",
    "valor": 6000.0,
    "tipo": "RECEITA",
    "mes": "OUTUBRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Salario",
    "valor": 6000.0,
    "tipo": "RECEITA",
    "mes": "NOVEMBRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Bonificação",
    "valor": 3000.0,
    "tipo": "RECEITA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Bonificação",
    "valor": 3000.0,
    "tipo": "RECEITA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Bonificação",
    "valor": 3000.0,
    "tipo": "RECEITA",
    "mes": "SETEMBRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Bonificação",
    "valor": 3000.0,
    "tipo": "RECEITA",
    "mes": "OUTUBRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Bonificação",
    "valor": 3000.0,
    "tipo": "RECEITA",
    "mes": "NOVEMBRO",
    "status": "A RECEBER"
  },
  {
    "categoria": "Dizimos",
    "valor": 184.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Dizimos",
    "valor": 184.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Dizimos",
    "valor": 184.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Dizimos",
    "valor": 184.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Dizimos",
    "valor": 184.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Primicias",
    "valor": 532.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Primicias",
    "valor": 532.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Primicias",
    "valor": 532.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Primicias",
    "valor": 532.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Primicias",
    "valor": 532.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Ofertas",
    "valor": 55.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Ofertas",
    "valor": 55.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Ofertas",
    "valor": 55.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Ofertas",
    "valor": 55.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Ofertas",
    "valor": 55.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "investimentos",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "investimentos",
    "valor": 373.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "investimentos",
    "valor": 373.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "investimentos",
    "valor": 373.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Aluguel",
    "valor": 1050.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Aluguel",
    "valor": 1050.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Aluguel",
    "valor": 1050.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Aluguel",
    "valor": 1050.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Aluguel",
    "valor": 1050.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "luz",
    "valor": 121.05,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "luz",
    "valor": 153.31,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "luz",
    "valor": 163.54,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "luz",
    "valor": 163.54,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "luz",
    "valor": 163.54,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "água/esgoto",
    "valor": 338.55,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "água/esgoto",
    "valor": 110.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "água/esgoto",
    "valor": 110.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "água/esgoto",
    "valor": 110.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "água/esgoto",
    "valor": 110.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "telefone - Claro",
    "valor": 258.29,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "telefone - Claro",
    "valor": 258.29,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "telefone - Claro",
    "valor": 258.29,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "telefone - Claro",
    "valor": 258.29,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "telefone - Claro",
    "valor": 258.29,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Internet",
    "valor": 115.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Internet",
    "valor": 115.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Internet",
    "valor": 115.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Internet",
    "valor": 115.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Internet",
    "valor": 115.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Compras / Cartão Inter",
    "valor": 1000.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Compras / Cartão Inter",
    "valor": 1223.2,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Compras / Cartão Inter",
    "valor": 1460.42,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Compras / Cartão Inter",
    "valor": 1200.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Compras / Cartão Inter",
    "valor": 1200.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Salario amor",
    "valor": 600.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario amor",
    "valor": 600.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario amor",
    "valor": 600.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Salario amor",
    "valor": 600.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Salario amor",
    "valor": 600.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Consultas / Plano",
    "valor": 440.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "PAGO"
  },
  {
    "categoria": "Consultas / Plano",
    "valor": 738.25,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "PAGO"
  },
  {
    "categoria": "Consultas / Plano",
    "valor": 1432.19,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "PAGO"
  },
  {
    "categoria": "Consultas / Plano",
    "valor": 1476.49,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Consultas / Plano",
    "valor": 1476.49,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Transporte publico",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Transporte publico",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Transporte publico",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Transporte publico",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Transporte publico",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Saude",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Saude",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Saude",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Saude",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Saude",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Lazer",
    "valor": 200.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Lazer",
    "valor": 200.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Lazer",
    "valor": 200.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Lazer",
    "valor": 200.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Lazer",
    "valor": 200.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Carro",
    "valor": 500.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Carro",
    "valor": 500.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Carro",
    "valor": 500.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Carro",
    "valor": 500.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Carro",
    "valor": 500.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Alimentação",
    "valor": 800.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Alimentação",
    "valor": 800.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Alimentação",
    "valor": 800.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Alimentação",
    "valor": 800.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Alimentação",
    "valor": 800.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Educação",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Educação",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Educação",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Educação",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Educação",
    "valor": 300.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Vestuário",
    "valor": 150.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Vestuário",
    "valor": 150.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Vestuário",
    "valor": 150.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Vestuário",
    "valor": 150.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Vestuário",
    "valor": 150.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Viagem",
    "valor": 250.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Viagem",
    "valor": 250.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Viagem",
    "valor": 250.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Viagem",
    "valor": 250.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Viagem",
    "valor": 250.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Presentes",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Presentes",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Presentes",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Presentes",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Presentes",
    "valor": 50.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Assinaturas",
    "valor": 70.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Assinaturas",
    "valor": 70.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Assinaturas",
    "valor": 70.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Assinaturas",
    "valor": 70.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Assinaturas",
    "valor": 70.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros gastos",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "JULHO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros gastos",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "AGOSTO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros gastos",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "SETEMBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros gastos",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "OUTUBRO",
    "status": "DEVEDOR"
  },
  {
    "categoria": "Outros gastos",
    "valor": 100.0,
    "tipo": "DESPESA",
    "mes": "NOVEMBRO",
    "status": "DEVEDOR"
  }
] Rotas da API
@app.route('/api/resumo/<mes>', methods=['GET'])
def get_resumo(mes):
    try:
        transacoes = Transacao.query.filter_by(mes=mes.upper()).all()
        receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
        despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
        return jsonify({
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    try:
      mmes = request.args.get(\'mes\', \'JANEIRO\').upper()       transacoes = Transacao.query.filter_by(mes=mes).all()
        return jsonify([{
            'id': t.id,
            'categoria': t.categoria,
            'valor': t.valor,
            'tipo': t.tipo,
            'mes': t.mes,
            'status': t.status
        } for t in transacoes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacoes', methods=['POST'])
def add_transacao():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacoes/<int:id>', methods=['PUT'])
def update_transacao(id):
    try:
        t = Transacao.query.get_or_404(id)
        data = request.json
        t.categoria = data['categoria']
        t.valor = data['valor']
        t.tipo = data['tipo']
        t.status = data.get('status', t.status)
        db.session.commit()
        return jsonify({'message': 'Atualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    try:
        t = Transacao.query.get_or_404(id)
        db.session.delete(t)
        db.session.commit()
        return jsonify({'message': 'Deletado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
