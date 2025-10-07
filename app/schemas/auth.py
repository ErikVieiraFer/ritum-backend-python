"""
Schemas de autenticação.
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema para resposta de login (legado, sem refresh token)."""
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    """Schema para resposta de login com refresh token."""
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Dados extraídos do token JWT."""
    email: Optional[str] = None