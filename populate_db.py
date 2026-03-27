import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from src.main import app, db
from src.models.orcamento import Transacao

def populate_database():
    # Ler o CSV processado
    df = pd.read_csv('/home/ubuntu/orcamento_processado.csv')
    
    # Meses disponíveis na planilha
    meses = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    
    # Categorias que são receitas (baseado na planilha)
    receitas_categorias = ["Salario", "Bonificação"]
    
    with app.app_context():
        # Limpar o banco de dados antes de popular
        db.drop_all()
        db.create_all()
        
        # Iterar sobre cada linha do DataFrame
        for _, row in df.iterrows():
            categoria = row['Categoria']
            
            # Determinar se é receita ou despesa
            tipo = "RECEITA" if categoria in receitas_categorias else "DESPESA"
            
            # Iterar sobre cada mês
            for mes in meses:
                valor_col = f"Valor_{mes}"
                status_col = f"Status_{mes}"
                
                # Verificar se as colunas existem no DataFrame
                if valor_col in df.columns:
                    valor = row[valor_col]
                    status = row[status_col] if status_col in df.columns else None
                    
                    # Apenas adicionar transações com valor diferente de zero
                    if pd.notna(valor) and valor != 0:
                        transacao = Transacao(
                            categoria=categoria,
                            valor=float(valor),
                            mes=mes,
                            status=status if pd.notna(status) else None,
                            tipo=tipo
                        )
                        db.session.add(transacao)
        
        db.session.commit()
        print("Banco de dados populado com sucesso!")

if __name__ == '__main__':
    populate_database()

