"""
Serviço de busca vetorial com ChromaDB para RAG de jurisprudência.
"""

import chromadb
import google.generativeai as genai
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")

genai.configure(api_key=GOOGLE_API_KEY)

# Cliente ChromaDB persistente
client = chromadb.PersistentClient(path="./chroma_db")

# Função de embedding usando o Gemini
gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GOOGLE_API_KEY)

# Coleção de jurisprudência
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
        doc_id: Identificador único para o documento.
        document_text: O texto completo do documento.
        metadata: Dicionário com metadados (tribunal, data, etc.).
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


if __name__ == '__main__':
    print("Módulo vector_db.py carregado.")