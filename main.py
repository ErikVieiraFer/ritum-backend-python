"""
Ritum API - Backend FastAPI
SaaS jurídico para advogados brasileiros
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importar configurações
from app.core.config import settings

# Importar routers
from app.routers import (
    auth,
    users,
    clients,
    processes,
    kanban,
    ai,
    extrajudicial,
    documents,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida da aplicação.
    Executa validações no startup e cleanup no shutdown.
    """
    # === STARTUP ===
    print("🚀 Iniciando Ritum API...")
    
    # Validar configurações obrigatórias
    try:
        settings.validate_required_settings()
        print("✅ Configurações validadas com sucesso")
    except ValueError as e:
        print(f"❌ ERRO DE CONFIGURAÇÃO:\n{e}")
        sys.exit(1)
    
    # Criar diretórios necessários
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    (static_dir / "generated_documents").mkdir(exist_ok=True)
    print("✅ Diretórios criados")
    
    print(f"✅ Ambiente: {settings.ENVIRONMENT}")
    print(f"✅ CORS origins: {settings.CORS_ORIGINS}")
    print("✅ Ritum API pronta!")
    
    yield  # Aplicação roda aqui
    
    # === SHUTDOWN ===
    print("👋 Encerrando Ritum API...")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend para o SaaS jurídico Ritum",
    lifespan=lifespan,
)


# === MIDDLEWARE ===

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ✅ Lista restrita
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# === STATIC FILES ===

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# === ROUTERS ===

# Autenticação (sem prefixo, endpoints na raiz)
app.include_router(auth.router)

# Usuários
app.include_router(users.router)

# Clientes
app.include_router(clients.router)

# Processos
app.include_router(processes.router)

# Kanban
app.include_router(kanban.router)

# IA (Redator + Jurisprudência)
app.include_router(ai.router)

# Assistente Extrajudicial
app.include_router(extrajudicial.router)

# Gerador de Documentos
app.include_router(documents.router)


# === ENDPOINTS DE SAÚDE ===

@app.get("/", tags=["Health"])
def root():
    """
    Endpoint raiz - verifica se a API está online.
    """
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check para monitoramento.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# === EXECUÇÃO LOCAL ===

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )