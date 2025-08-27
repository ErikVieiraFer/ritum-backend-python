# seed_db.py
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime

# Importa o nosso motor de banco de dados e os modelos
from app.database import SessionLocal, Base, engine
from app.models import JurisprudenceDocument

# Exemplo de documentos de jurisprudência
sample_docs = [
    {
        "court": "STJ",
        "case_number": "REsp 1827821-DF",
        "publication_date": datetime.strptime("2023-05-18", "%Y-%m-%d"),
        "summary": "DIREITO DO CONSUMIDOR. RESPONSABILIDADE CIVIL. INTERNET. PROVEDOR. CONTEÚDO OFENSIVO. REMOÇÃO. NOTIFICAÇÃO. O provedor de aplicações de internet somente será responsabilizado civilmente por danos decorrentes de conteúdo gerado por terceiros se, após notificação judicial para remoção do conteúdo, não o fizer no prazo legal.",
        "full_text": "DIREITO DO CONSUMIDOR. RESPONSABILIDADE CIVIL. INTERNET. PROVEDOR DE APLICAÇÕES. CONTEÚDO OFENSIVO. REMOÇÃO. NOTIFICAÇÃO JUDICIAL. O provedor de aplicações de internet, tal como redes sociais e plataformas de vídeo, somente será responsabilizado civilmente por danos decorrentes de conteúdo gerado por terceiros se, após notificação judicial específica para remoção do conteúdo, não o fizer no prazo legal, nos termos do art. 19 da Lei do Marco Civil da Internet. A notificação extrajudicial não é suficiente para caracterizar a responsabilidade. Precedente do STJ."
    },
    {
        "court": "TJSP",
        "case_number": "Apelação Cível 1005872-35.2021.8.26.0007",
        "publication_date": datetime.strptime("2024-02-14", "%Y-%m-%d"),
        "summary": "CONTRATO. COMPRA E VENDA DE IMÓVEL. ATRASO NA ENTREGA. INADIMPLÊNCIA. DANO MORAL. INDENIZAÇÃO. Configurado o atraso injustificado na entrega de imóvel, é devida a indenização por danos morais ao consumidor, pois a situação ultrapassa o mero dissabor do cotidiano. Jurisprudência do TJSP.",
        "full_text": "APELAÇÃO. COMPRA E VENDA DE IMÓVEL. ATRASO. DANO MORAL. Conforme entendimento consolidado nesta Corte, o atraso na entrega de imóvel por culpa exclusiva da construtora enseja a reparação por danos morais, visto que a situação de incerteza e insegurança gerada ao consumidor ultrapassa o mero aborrecimento e gera grave abalo psicológico. Sentença mantida. Recurso desprovido."
    }
]

def seed_database():
    print("Carregando variáveis de ambiente...")
    load_dotenv()
    
    # Verifica se a DATABASE_URL foi carregada
    if not os.getenv("DATABASE_URL"):
        print("Erro: A variável de ambiente DATABASE_URL não foi encontrada.")
        print("Verifique se o arquivo .env existe e está configurado corretamente.")
        return

    db: Session = SessionLocal()
    print("Sessão com o banco de dados iniciada.")
    try:
        # Verifica se já existem documentos, para não duplicar
        doc_count = db.query(JurisprudenceDocument).count()
        print(f"Encontrados {doc_count} documentos existentes.")

        if doc_count == 0:
            print("Populando o banco de dados com documentos de jurisprudência...")
            for doc_data in sample_docs:
                db_doc = JurisprudenceDocument(**doc_data)
                db.add(db_doc)
            db.commit()
            print("Documentos de jurisprudência adicionados com sucesso!")
        else:
            print("O banco de dados já contém documentos. Não é necessário popular novamente.")
    except Exception as e:
        db.rollback()
        print(f"Ocorreu um erro ao popular o banco de dados: {e}")
    finally:
        db.close()
        print("Sessão com o banco de dados fechada.")

if __name__ == "__main__":
    seed_database()
