import uuid
from sqlalchemy import Column, String, DateTime, Integer, Text , Float , ForeignKey , UniqueConstraint
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    userType = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Document(Base):
    __tablename__ = 'documents'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(Text)
    file_url = Column(String(255), nullable=False)
    uploaded_by = Column(String(36)) 
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SaccoMetric(Base):
    __tablename__ = 'sacco_metrics'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    year = Column(Integer, nullable=False)

    membership_count = Column(Integer, default=0)
    loan_book_value = Column(Float, default=0)
    asset_base = Column(Float, default=0)
    deposits = Column(Float, default=0)
    dividend_rate = Column(Float, default=0)
    interest_rebate = Column(Float, default=0)
    revenue = Column(Float, default=0)
    portfolio_at_risk = Column(Float, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('document_id', 'year', name='_doc_year_uc'),)


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    sender = Column(String(10), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())