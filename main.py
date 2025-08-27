import asyncio
import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

# Adições para o Gerador de Documentos
from fastapi.staticfiles import StaticFiles
from app import document_generator

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from typing import List, Optional
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, models, schemas, security
from app.dependencies import get_db, get_current_user
from app.scraper import scrape_tjsp_process

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    browser_ws_url = os.getenv("BROWSERLESS_URL")
    if not browser_ws_url:
        raise RuntimeError("A variável de ambiente BROWSERLESS_URL não está definida.")

    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.connect(browser_ws_url)
        app.state.browser = browser
        app.state.playwright = playwright
        print("INFO: Conectado ao navegador remoto com sucesso.")
        yield
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao navegador remoto: {e}")
        # Mesmo com falha na conexão, precisamos garantir que o playwright pare.
        yield # Permite que a aplicação inicie, mas os endpoints de scraping falharão.
    finally:
        # Shutdown
        print("INFO: Iniciando processo de shutdown do browser e Playwright.")
        if 'browser' in app.state and app.state.browser and not app.state.browser.is_closed():
            await app.state.browser.close()
            print("INFO: Conexão com o navegador remoto fechada.")
        
        if 'playwright' in app.state and app.state.playwright:
            await app.state.playwright.stop()
            print("INFO: Instância do Playwright parada.")

app = FastAPI(
    title="API do Ritum",
    description="Backend para o SaaS jurídico Ritum, gerenciando processos, clientes e mais.",
    version="0.1.0",
    lifespan=lifespan
)

# --- Montagem de diretórios estáticos ---
# Cria o diretório se não existir
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configuração do CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints de Autenticação e Usuários ---

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Autenticação e Usuários"])
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Este email já está cadastrado.")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token, tags=["Autenticação e Usuários"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User, tags=["Autenticação e Usuários"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.patch("/users/me", response_model=schemas.User, tags=["Autenticação e Usuários"])
def update_users_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_user = crud.update_user_profile(db=db, user_id=current_user.id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return updated_user

@app.patch("/users/me/password", status_code=status.HTTP_204_NO_CONTENT, tags=["Autenticação e Usuários"])
def update_password(password_update: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.update_user_password(db=db, user=current_user, password_update=password_update)
    if not success:
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    return

# --- Endpoints de Clientes (Corrigido) ---

@app.post("/api/v1/clients", response_model=schemas.Client, status_code=status.HTTP_201_CREATED, tags=["Clientes"])
def create_client_for_user(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_user_client(db=db, client=client, user_id=current_user.id)

@app.get("/api/v1/clients", response_model=List[schemas.Client], tags=["Clientes"])
def read_user_clients(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), skip: int = 0, limit: int = 100):
    return crud.get_user_clients(db=db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/api/v1/clients/{clientId}", response_model=schemas.Client, tags=["Clientes"])
def read_client_by_id(clientId: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_client = crud.get_client_by_id(db=db, client_id=clientId, user_id=current_user.id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou permissão negada.")
    return db_client

@app.put("/api/v1/clients/{clientId}", response_model=schemas.Client, tags=["Clientes"])
def update_client_data(clientId: UUID, client: schemas.ClientUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_client = crud.update_client(db=db, client_id=clientId, client_update=client, user_id=current_user.id)
    if updated_client is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou permissão negada.")
    return updated_client

@app.delete("/api/v1/clients/{clientId}", status_code=status.HTTP_204_NO_CONTENT, tags=["Clientes"])
def delete_client_data(clientId: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    deleted_client = crud.delete_client(db=db, client_id=clientId, user_id=current_user.id)
    if deleted_client is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou permissão negada.")
    return

# --- Endpoints do Gerador de Documentos ---

@app.get("/api/v1/document-templates", tags=["Gerador de Documentos"])
def list_document_templates():
    """Retorna a lista de templates de documentos disponíveis."""
    return document_generator.get_available_templates()

@app.post("/api/v1/documents/generate", response_model=schemas.GenerateDocumentResponse, tags=["Gerador de Documentos"])
def generate_document_endpoint(request: schemas.GenerateDocumentRequest, current_user: models.User = Depends(get_current_user)):
    """
    Gera um novo documento a partir de um modelo, dados do cliente e detalhes do caso.
    """
    try:
        lawyer_data = schemas.User.model_validate(current_user).model_dump(by_alias=True)
        client_data = request.clientData.model_dump(by_alias=True)
        case_details = request.caseDetails.model_dump(by_alias=True) if request.caseDetails else {}

        output_path_str = document_generator.generate_document(
            template_id=request.templateId,
            client_data=client_data,
            lawyer_data=lawyer_data,
            case_details=case_details
        )
        
        output_path = Path(output_path_str)
        file_name = output_path.name
        
        document_url = f"/static/generated_documents/{file_name}"

        return {"documentUrl": document_url, "fileName": file_name}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao gerar o documento: {str(e)}")

# --- Endpoints de Processos ---

@app.post("/processes/", response_model=schemas.Process, status_code=status.HTTP_201_CREATED, tags=["Processos"])
def create_process_for_user(process: schemas.ProcessCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_user_process(db=db, process=process, user_id=current_user.id)

@app.get("/processes/", response_model=List[schemas.Process], tags=["Processos"])
def read_user_processes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), skip: int = 0, limit: int = 100):
    return crud.get_user_processes(db=db, user_id=current_user.id, skip=skip, limit=limit)

# --- Endpoints do Kanban ---

@app.get("/board/", response_model=List[schemas.TaskColumnWithCards], tags=["Kanban"])
def get_user_board(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_board_for_user(db=db, user_id=current_user.id)

@app.post("/columns/", response_model=schemas.TaskColumn, status_code=status.HTTP_201_CREATED, tags=["Kanban"])
def create_column_for_user(column: schemas.TaskColumnCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_task_column(db=db, column=column, user_id=current_user.id)

@app.post("/columns/{column_id}/cards/", response_model=schemas.TaskCard, status_code=status.HTTP_201_CREATED, tags=["Kanban"])
def create_card_for_column(column_id: int, card: schemas.TaskCardCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_card = crud.create_task_card(db=db, card=card, column_id=column_id, user_id=current_user.id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="Coluna não encontrada ou não pertence ao usuário.")
    return db_card

@app.patch("/cards/{card_id}/move", response_model=schemas.TaskCard, tags=["Kanban"])
def move_card_to_another_column(card_id: int, move_data: schemas.TaskCardMove, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = crud.move_task_card(db=db, card_id=card_id, new_column_id=move_data.new_column_id, user_id=current_user.id)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result["card"]

@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Kanban"])
def delete_card(card_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    deleted_card = crud.delete_task_card(db=db, card_id=card_id, user_id=current_user.id)
    if deleted_card is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado ou permissão negada.")
    return

@app.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Kanban"])
def delete_column(column_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    deleted_column = crud.delete_task_column(db=db, column_id=column_id, user_id=current_user.id)
    if deleted_column is None:
        raise HTTPException(status_code=404, detail="Coluna não encontrada ou permissão negada.")
    return

@app.patch("/columns/{column_id}", response_model=schemas.TaskColumn, tags=["Kanban"])
def update_column(column_id: int, column_update: schemas.TaskColumnUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_column = crud.update_task_column(db=db, column_id=column_id, column_update=column_update, user_id=current_user.id)
    if updated_column is None:
        raise HTTPException(status_code=404, detail="Coluna não encontrada ou permissão negada.")
    return updated_column

@app.patch("/cards/{card_id}", response_model=schemas.TaskCard, tags=["Kanban"])
def update_card_details(card_id: int, card_update: schemas.TaskCardUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_card = crud.update_task_card(db=db, card_id=card_id, card_update=card_update, user_id=current_user.id)
    if updated_card is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado ou permissão negada.")
    return updated_card

# --- Endpoints do Redator Extrajudicial ---

@app.post("/api/v1/extrajudicial-cases", response_model=schemas.CaseResponse, status_code=status.HTTP_201_CREATED, tags=["Redator Extrajudicial"])
def create_extrajudicial_case(case: schemas.CaseCreateRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_extrajudicial_case(db=db, case=case, user_id=current_user.id)

@app.get("/api/v1/extrajudicial-cases/{case_id}", response_model=schemas.CaseResponse, tags=["Redator Extrajudicial"])
def get_extrajudicial_case(case_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_case = crud.get_extrajudicial_case(db=db, case_id=case_id, user_id=current_user.id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado ou permissão negada.")
    return db_case

@app.put("/api/v1/extrajudicial-cases/{case_id}", response_model=schemas.CaseResponse, tags=["Redator Extrajudicial"])
def update_extrajudicial_case(case_id: UUID, case_data: schemas.CaseUpdateRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_case = crud.update_extrajudicial_case(db=db, case_id=case_id, case_data=case_data, user_id=current_user.id)
    if updated_case is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado ou permissão negada.")
    return updated_case

# --- Endpoints de Inteligência Artificial ---

@app.post("/ai/generate-prompt", response_model=schemas.PromptGenerationResponse, tags=["Inteligência Artificial"])
def generate_prompt_for_petition(request: schemas.PromptGenerationRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
        "--- INÍCIO DOS FATOS ---"
        f"{request.facts}"
        "\n--- FIM DOS FATOS ---"
        "\n\n"
        "Elabore a petição com base estritamente nos fatos apresentados."
    )
    return schemas.PromptGenerationResponse(generated_prompt=super_prompt_template)

@app.post("/ai/generate-petition", response_model=schemas.PetitionGenerationResponse, tags=["Inteligência Artificial"])
def generate_petition(request: schemas.PetitionGenerationRequest, current_user: models.User = Depends(get_current_user)):
    if not genai:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="A biblioteca 'google-generativeai' não está instalada. Instale-a com 'pip install google-generativeai'.")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A chave de API do Google (GOOGLE_API_KEY) não está configurada no ambiente.")
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
                detail=f"A geração de conteúdo foi bloqueada pela API do Gemini. Motivo: {block_reason}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro inesperado ao se comunicar com a API do Gemini: {str(e)}")

# --- Endpoints de Busca de Jurisprudência (Fase 1: DataJud) ---

@app.post("/api/v1/jurisprudence/search", response_model=schemas.DataJudSearchResponse, tags=["Busca de Jurisprudência (RAG)"])
def search_jurisprudence_datajud(request: schemas.JurisprudenceSearchRequest, current_user: models.User = Depends(get_current_user)):
    datajud_api_key = os.getenv("DATAJUD_API_KEY")
    if not datajud_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A chave da API do DataJud (DATAJUD_API_KEY) não está configurada no ambiente.",
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
            detail=f"Ocorreu um erro inesperado ao se comunicar com a API do Gemini: {str(e)}")

# --- Endpoints de Teste do Scraper (Fase 2) ---

@app.post("/api/v1/scrape_test/{process_number}", tags=["Busca de Jurisprudência (RAG)"])
async def test_scrape_process(process_number: str, request: Request, current_user: models.User = Depends(get_current_user)):
    try:
        if len(process_number) == 20:
            formatted_number = f"{process_number[:7]}-{process_number[7:9]}.{process_number[9:13]}.{process_number[13]}.{process_number[14:16]}.{process_number[16:]}"
        else:
            formatted_number = process_number
        screenshot_path = await scrape_tjsp_process(request.app.state.browser, formatted_number)
        return {"message": "Scraping test completed.", "screenshot_path": screenshot_path}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during scraping: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
