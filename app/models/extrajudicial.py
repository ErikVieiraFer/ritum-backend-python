"""
Modelos de casos extrajudiciais, jurisprudência e intimações.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class ExtrajudicialCase(Base):
    __tablename__ = "extrajudicial_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    case_type = Column(String, nullable=False)
    case_name = Column(String, nullable=False)
    status = Column(String, default="InProgress")
    data = Column(JSONB, nullable=True, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="extrajudicial_cases")


class JurisprudenceDocument(Base):
    __tablename__ = "jurisprudence_documents"

    id = Column(Integer, primary_key=True, index=True)
    court = Column(String, nullable=False, index=True)
    case_number = Column(String, nullable=False, index=True)
    publication_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)


class Intimation(Base):
    __tablename__ = "intimations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_date = Column(DateTime, nullable=False, index=True)
    process_number = Column(String, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="intimations")