import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa o app e a base do SQLAlchemy para manipulação
from main import app
from app.database import Base
from app.dependencies import get_db

# --- Configuração do Banco de Dados de Teste ---
# Usaremos um banco de dados SQLite em memória para os testes serem rápidos e isolados.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Sobrescrevendo a Dependência do Banco de Dados ---
# Isso garante que os endpoints usem o banco de dados de teste em vez do de produção.
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cria o cliente de teste que usaremos para fazer as chamadas à API
client = TestClient(app)

# --- Testes ---

def setup_database():
    """Limpa e recria o banco de dados antes de cada bateria de testes."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_auth_token() -> str:
    """Função auxiliar para criar um usuário e obter um token."""
    user_data = {"email": "test@example.com", "name": "Test User", "password": "password123"}
    client.post("/users/", json=user_data)
    
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/token", data=login_data)
    return response.json()["access_token"]

def test_generate_prompt_endpoint():
    """
    Testa o endpoint /ai/generate-prompt, cobrindo autenticação e lógica.
    """
    setup_database()
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    facts = "O cliente comprou um carro que apresentou defeito no motor após uma semana de uso."
    response = client.post("/ai/generate-prompt", headers=headers, json={"facts": facts})

    # Verifica se a requisição foi bem-sucedida
    assert response.status_code == 200
    data = response.json()
    
    # Verifica se a resposta contém a chave esperada e se os fatos foram inseridos no template
    assert "generated_prompt" in data
    assert facts in data["generated_prompt"]
    assert "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO" in data["generated_prompt"]

def test_generate_prompt_unauthorized():
    """
    Testa se o endpoint está devidamente protegido contra acesso não autenticado.
    """
    setup_database()
    response = client.post("/ai/generate-prompt", json={"facts": "quaisquer fatos"})

    # Acesso sem token deve retornar 401 Unauthorized
    assert response.status_code == 401

def test_generate_petition_success(mocker):
    """
    Testa o endpoint /ai/generate-petition simulando uma resposta bem-sucedida da API Gemini.
    """
    setup_database()
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Simula que a GOOGLE_API_KEY existe no ambiente
    mocker.patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-api-key"})

    # 2. Simula a resposta da biblioteca do Gemini
    mock_response_text = "Texto da petição gerado pela IA."
    mock_api_response = mocker.Mock()
    mock_api_response.text = mock_response_text
    mocker.patch("main.genai.GenerativeModel").return_value.generate_content.return_value = mock_api_response

    # 3. Chama o endpoint
    response = client.post("/ai/generate-petition", headers=headers, json={"prompt": "Prompt de teste"})

    # 4. Verifica o resultado
    assert response.status_code == 200
    assert response.json() == {"generated_petition": mock_response_text}

def test_generate_petition_no_api_key(mocker):
    """
    Testa se o endpoint retorna o erro correto quando a GOOGLE_API_KEY não está definida.
    """
    setup_database()
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Garante que a variável de ambiente não exista para este teste
    mocker.patch.dict(os.environ, clear=True)

    response = client.post("/ai/generate-petition", headers=headers, json={"prompt": "Prompt de teste"})

    assert response.status_code == 503
    assert "não está configurada no ambiente" in response.json()["detail"]
