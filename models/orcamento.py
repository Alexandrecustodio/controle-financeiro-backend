from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    mes = db.Column(db.String(20), nullable=False)  # Ex: "JANEIRO", "FEVEREIRO", etc.
    status = db.Column(db.String(20), nullable=True)  # Ex: "PAGO", "A RECEBER", "DEVEDOR"
    tipo = db.Column(db.String(20), nullable=False)  # "RECEITA" ou "DESPESA"
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria': self.categoria,
            'valor': self.valor,
            'mes': self.mes,
            'status': self.status,
            'tipo': self.tipo
        }

