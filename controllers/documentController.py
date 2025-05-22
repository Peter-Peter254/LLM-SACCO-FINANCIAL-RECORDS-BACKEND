from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from schemas.documentSchema import DocumentCreate, DocumentResponse
from database.models import Document, User
from database.database import SessionLocal
from auth.dependencies import get_current_user
import os
import requests
import base64

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc: DocumentCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    new_doc = Document(**doc.dict(), uploaded_by=current_user.id)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.get("/base64/{document_id}")
async def get_document_base64(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        res = requests.get(doc.file_url)
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch file from Supabase")

        base64_pdf = base64.b64encode(res.content).decode('utf-8')
        data_uri = f"data:application/pdf;base64,{base64_pdf}"

        return {
            "name": doc.name,
            "file_url": data_uri
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
