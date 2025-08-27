
import chromadb
import google.generativeai as genai
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a API Key do Gemini a partir das variáveis de ambiente
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")

genai.configure(api_key=GOOGLE_API_KEY)

# Cria um cliente ChromaDB. Ele gerencia as coleções.
# Usaremos um cliente "persistente" para que os dados sejam salvos em disco.
client = chromadb.PersistentClient(path="./chroma_db")

# Função para criar a função de embedding usando o Gemini
gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GOOGLE_API_KEY)

# Tenta obter ou criar uma coleção (tabela) de jurisprudência.
# A função de embedding é especificada aqui.
try:
    jurisprudence_collection = client.get_or_create_collection(
        name="jurisprudence",
        embedding_function=gemini_ef
    )
except Exception as e:
    print(f"Erro ao criar/obter a coleção do ChromaDB: {e}")
    jurisprudence_collection = None

def add_jurisprudence_document(doc_id: str, document_text: str, metadata: dict):
    """
    Adiciona um único documento de jurisprudência à coleção.

    Args:
        doc_id: Um identificador único para o documento (ex: número do processo).
        document_text: O texto completo do documento.
        metadata: Um dicionário com metadados (ex: tribunal, data, etc.).
    """
    if jurisprudence_collection is None:
        print("A coleção de jurisprudência não está disponível.")
        return

    try:
        jurisprudence_collection.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Documento {doc_id} adicionado com sucesso.")
    except Exception as e:
        print(f"Erro ao adicionar o documento {doc_id}: {e}")


def search_jurisprudence(query_text: str, n_results: int = 5) -> list:
    """
    Busca por jurisprudências relevantes para uma consulta.

    Args:
        query_text: A pergunta ou descrição do caso do usuário.
        n_results: O número de resultados a serem retornados.

    Returns:
        Uma lista de documentos relevantes.
    """
    if jurisprudence_collection is None:
        print("A coleção de jurisprudência não está disponível.")
        return []
        
    try:
        results = jurisprudence_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0] if results and results['documents'] else []
    except Exception as e:
        print(f"Erro ao realizar a busca: {e}")
        return []

# Exemplo de como usar (para teste futuro)
if __name__ == '__main__':
    # Exemplo de adição de um documento (isso viria da API do CNJ)
    # sample_id = "REsp_123456"
    # sample_text = "O Superior Tribunal de Justiça, em decisão sobre o Recurso Especial nº 123456, entendeu que o mero inadimplemento contratual, como o atraso na entrega de imóvel, não gera, por si só, dano moral indenizável, sendo necessária a comprovação de circunstâncias excepcionais que configurem o abalo psíquico."
    # sample_metadata = {"tribunal": "STJ", "ano": 2023}
    # add_jurisprudence_document(sample_id, sample_text, sample_metadata)

    # Exemplo de busca
    # query = "advogado busca caso de atraso na entrega de apartamento que gerou dano moral"
    # relevant_docs = search_jurisprudence(query)
    # print("Documentos relevantes encontrados:")
    # for doc in relevant_docs:
    #     print(f"- {doc[:100]}...")

    print("Módulo vector_db.py carregado.")
