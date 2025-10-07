"""
Schemas de IA (Redator Judicial e Jurisprudência).
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PromptGenerationRequest(BaseModel):
    facts: str


class PromptGenerationResponse(BaseModel):
    generated_prompt: str


class PetitionGenerationRequest(BaseModel):
    prompt: str


class PetitionGenerationResponse(BaseModel):
    generated_petition: str


class JurisprudenceSearchRequest(BaseModel):
    q: str = Field(..., description="Query de busca do usuário.")


class DataJudResult(BaseModel):
    score: Optional[float] = None
    processo: Optional[str] = None
    tribunal: Optional[str] = None
    data_ajuizamento: Optional[str] = None
    classe: Optional[str] = None
    assuntos: List[str] = []
    orgao_julgador: Optional[str] = None


class DataJudSearchResponse(BaseModel):
    results: List[DataJudResult]