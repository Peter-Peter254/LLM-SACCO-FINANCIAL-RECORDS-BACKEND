# cronJobs/embedder.py

import os
import uuid
import time
import requests
import schedule
from io import BytesIO
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Document
import pdfplumber
from chromadb import PersistentClient
from openai import OpenAI
from tiktoken import get_encoding

# Load .env and initialize clients
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = PersistentClient(path=".chroma")

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def extract_text_from_pdf(file_stream):
    with pdfplumber.open(file_stream) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def chunk_text(text, chunk_size=300, overlap=50):
    enc = get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(enc.decode(chunk))

    return chunks

def ingest_to_chroma(document_id, file_url):
    print(f"Ingesting: {file_url}")
    pdf_stream = download_pdf(file_url)
    text = extract_text_from_pdf(pdf_stream)
    chunks = chunk_text(text)

    if not chunks:
        print(f"No text extracted for {document_id}")
        return

    collection = chroma_client.get_or_create_collection(name="sacco_docs")

    print(f" Generating embeddings for {len(chunks)} chunks...")
    embeddings_response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=chunks
    )
    embeddings = [e.embedding for e in embeddings_response.data]

    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id} for _ in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    print(f" Embedded {len(chunks)} chunks for document {document_id}")

def run_embedding_job():
    db: Session = SessionLocal()
    docs = db.query(Document).filter(Document.status == 1).all()

    if not docs:
        print("No new documents to embed.")
        db.close()
        return

    for doc in docs:
        try:
            ingest_to_chroma(doc.id, doc.file_url)
            doc.status = 2  # Mark as embedded
            db.commit()
        except Exception as e:
            print(f"Failed to embed {doc.name}: {e}")
            db.rollback()

    db.close()

def start_embedding_cron():
    schedule.every(5).minutes.do(run_embedding_job)
    print("Embedding cron started: runs every 5 minutes")
    while True:
        schedule.run_pending()
        time.sleep(1)
