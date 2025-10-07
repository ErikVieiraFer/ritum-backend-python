"""
Endpoints de IA (Redator Judicial e Busca de Jurisprudência).
"""

import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["Inteligência Artificial"])


@router.post("/generate-prompt", response_model=schemas.PromptGenerationResponse)
def generate_prompt(
    request: schemas.PromptGenerationRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Gera um prompt otimizado para a IA a partir dos fatos narrados.
    """
    super_prompt_template = (
        "Você é um assistente jurídico especialista em direito civil brasileiro, atuando como um advogado sênior. "
        "Sua tarefa é elaborar uma Petição Inicial clara, bem fundamentada e tecnicamente precisa.\n\n"
        "Analise a narração dos fatos a seguir e estruture o documento final contendo os seguintes elementos obrigatórios, nesta ordem:\n"
        "1. Endereçamento (Ex: EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ... VARA CÍVEL DA COMARCA DE ...).\n"
        "2. Qualificação completa das partes (Autor e Réu).\n"
        "3. Uma seção clara e objetiva intitulada 'DOS FATOS'.\n"
        "4. Uma seção robusta intitulada 'DO DIREITO', apresentando a fundamentação jurídica pertinente ao caso (cite artigos de lei e, se possível, jurisprudência relevante).\n"
        "5. Uma seção final intitulada 'DOS PEDIDOS', listando de forma clara e inequívoca tudo o que se pleiteia.\n\n"
        "A seguir, a narração dos fatos fornecida pelo usuário:\n"
        "--- INÍCIO DOS FATOS ---\n"
        f"{request.facts}\n"
        "--- FIM DOS FATOS ---\n\n"
        "Elabore a petição com base estritamente nos fatos apresentados."
    )
    return schemas.PromptGenerationResponse(generated_prompt=super_prompt_template)


@router.post("/generate-petition", response_model=schemas.PetitionGenerationResponse)
def generate_petition(
    request: schemas.PetitionGenerationRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Gera uma petição judicial usando IA generativa (Google Gemini).
    """
    if not genai:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="A biblioteca 'google-generativeai' não está instalada."
        )
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A chave de API do Google (GOOGLE_API_KEY) não está configurada."
        )
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(request.prompt)
        
        if hasattr(response, 'text'):
            return schemas.PetitionGenerationResponse(generated_petition=response.text)
        else:
            block_reason = response.prompt_feedback.block_reason.name
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conteúdo bloqueado pela API do Gemini. Motivo: {block_reason}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API do Gemini: {str(e)}"
        )


@router.post("/api/v1/jurisprudence/search", response_model=schemas.DataJudSearchResponse)
def search_jurisprudence(
    request: schemas.JurisprudenceSearchRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Busca jurisprudência na API DataJud do CNJ.
    """
    datajud_api_key = os.getenv("DATAJUD_API_KEY")
    if not datajud_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A chave da API do DataJud não está configurada.",
        )
    
    datajud_url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search"
    headers = {
        "Authorization": f"APIKey {datajud_api_key}",
        "Content-Type": "application/json",
    }
    
    es_query = {
        "size": 20,
        "query": {
            "multi_match": {
                "query": request.q,
                "fields": ["assuntos.nome^3", "classe.nome^2", "movimentos.nome", "orgaoJulgador.nome"],
                "fuzziness": "AUTO"
            }
        }
    }
    
    try:
        response = requests.post(datajud_url, headers=headers, json=es_query, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        
        hits = response_data.get("hits", {}).get("hits", [])
        formatted_results = []
        
        for hit in hits:
            source = hit.get("_source", {})
            formatted_results.append({
                "score": hit.get("_score"),
                "processo": source.get("numeroProcesso"),
                "tribunal": source.get("tribunal"),
                "data_ajuizamento": source.get("dataAjuizamento"),
                "classe": source.get("classe", {}).get("nome"),
                "assuntos": [assunto.get("nome") for assunto in source.get("assuntos", [])],
                "orgao_julgador": source.get("orgaoJulgador", {}).get("nome"),
            })
        
        return {"results": formatted_results}
    
    except requests.exceptions.HTTPError as http_err:
        try:
            detail = http_err.response.json()
        except:
            detail = http_err.response.text
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Erro ao comunicar com a API do DataJud: {detail}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )