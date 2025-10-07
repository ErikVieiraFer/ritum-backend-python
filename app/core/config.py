"""
Configurações centralizadas da aplicação Ritum.
Gerencia variáveis de ambiente e settings globais.
"""

import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    """
    
    # === APLICAÇÃO ===
    APP_NAME: str = "Ritum API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # === SEGURANÇA ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # === DATABASE ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # === CORS ===
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """
        Retorna lista de origens permitidas baseado no ambiente.
        """
        if self.ENVIRONMENT == "production":
            return [
                "https://ritum-app.web.app",
            ]
        else:
            return [
                "http://localhost",
                "http://localhost:3000",
                "http://localhost:8080",
                "http://localhost:8081",
            ]
    
    # === APIS EXTERNAS ===
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    DATAJUD_API_KEY: str = os.getenv("DATAJUD_API_KEY", "")
    BROWSERLESS_URL: str = os.getenv("BROWSERLESS_URL", "")
    
    # === RATE LIMITING ===
    RATE_LIMIT_ENABLED: bool = ENVIRONMENT == "production"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True
    
    def validate_required_settings(self):
        """
        Valida se todas as configurações obrigatórias estão presentes.
        Lança ValueError se alguma estiver faltando.
        """
        required = {
            "SECRET_KEY": self.SECRET_KEY,
            "DATABASE_URL": self.DATABASE_URL,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"❌ Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing)}\n"
                f"Configure-as no arquivo .env antes de iniciar a aplicação."
            )
        
        # Validar comprimento mínimo da SECRET_KEY
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                f"❌ SECRET_KEY muito curta! Deve ter pelo menos 32 caracteres.\n"
                f"Atual: {len(self.SECRET_KEY)} caracteres"
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações.
    Cached para evitar recarregar a cada chamada.
    """
    return Settings()


# Instância global das configurações
settings = get_settings()