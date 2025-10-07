"""
Módulo de segurança - Autenticação, criptografia e JWT.
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt
from typing import Optional, Dict, Any

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica uma senha em texto plano contra um hash bcrypt.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash bcrypt da senha
        
    Returns:
        True se a senha corresponder ao hash, False caso contrário
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Gera o hash de uma senha usando bcrypt com 12 rounds.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash bcrypt da senha
    """
    hashed_bytes = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)  # Explícito: 12 rounds
    )
    return hashed_bytes.decode('utf-8')


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Cria um JWT access token com tempo de expiração curto.
    
    Args:
        data: Dados a serem incluídos no token (ex: {"sub": "email@example.com"})
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Cria um JWT refresh token com tempo de expiração longo.
    
    Args:
        data: Dados a serem incluídos no token (ex: {"sub": "email@example.com"})
        
    Returns:
        Refresh token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um access token JWT.
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        Payload do token se válido, None se inválido/expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Validar tipo do token
        if payload.get("type") != "access":
            return None
            
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um refresh token JWT.
    
    Args:
        token: Refresh token JWT a ser decodificado
        
    Returns:
        Payload do token se válido, None se inválido/expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Validar tipo do token
        if payload.get("type") != "refresh":
            return None
            
        return payload
    except JWTError:
        return None