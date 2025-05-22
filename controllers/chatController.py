from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Document, Chat
from openai import OpenAI
from chromadb import PersistentClient
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = PersistentClient(path=".chroma")

class ChatRequest(BaseModel):
    query: str
    userId: str



@router.get("/chat/{document_id}/{user_id}")
def get_chat_history(document_id: str, user_id: str, db: Session = Depends(get_db)):
    history = db.query(Chat).filter(
        Chat.document_id == document_id,
        Chat.user_id == user_id
    ).order_by(Chat.timestamp).all()

    return [
        {"sender": chat.sender, "text": chat.message}
        for chat in history
    ]


@router.post("/chat/{document_id}")
def chat_with_document(document_id: str, body: ChatRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    normalized = body.query.strip().lower()

    # Handle common greetings or casual expressions
    casual_replies = {
        "hi": "Hello! Ask me something about the financial report.",
        "hello": "Hey there! What would you like to know about this report?",
        "hey": "Hi! I’m ready when you are.",
        "thanks": "You're welcome! Let me know if you need help with anything in the document.",
        "thank you": "Always happy to help!",
        "bye": "Goodbye! Come back anytime to explore the financials.",
    }

    for key, reply in casual_replies.items():
        if normalized.startswith(key):
            db.add(Chat(
                id=str(uuid4()),
                user_id=body.userId,
                document_id=document_id,
                sender='user',
                message=body.query
            ))

            db.add(Chat(
                id=str(uuid4()),
                user_id=body.userId,
                document_id=document_id,
                sender='assistant',
                message=reply
            ))

            db.commit()
            return {"response": reply}
    embedded_query = client.embeddings.create(
        model="text-embedding-ada-002",
        input=body.query
    ).data[0].embedding

    collection = chroma_client.get_or_create_collection(name="sacco_docs")
    results = collection.query(
        query_embeddings=[embedded_query],
        n_results=5,
        where={"document_id": document_id}
    )
    chunks = results['documents'][0] if results['documents'] else []
    context = "\n\n".join(chunks) or "No relevant content found in the document."

    past_chats = db.query(Chat).filter(
        Chat.document_id == document_id,
        Chat.user_id == body.userId
    ).order_by(Chat.timestamp).all()

    messages = [
        {"role": "system", "content": "You are a helpful financial assistant. Use only the document context provided."}
    ] + [
        {"role": chat.sender, "content": chat.message} for chat in past_chats
    ]

    messages.append({
        "role": "user",
        "content": f"Document context:\n{context}\n\n{body.query}"
    })

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    response_text = completion.choices[0].message.content

    db.add(Chat(
        id=str(uuid4()),
        user_id=body.userId,
        document_id=document_id,
        sender='user',
        message=body.query
    ))

    db.add(Chat(
        id=str(uuid4()),
        user_id=body.userId,
        document_id=document_id,
        sender='assistant',
        message=response_text
    ))

    db.commit()

    return {"response": response_text}


@router.delete("/chat/{document_id}/{user_id}")
def delete_chat_history(document_id: str, user_id: str, db: Session = Depends(get_db)):
    deleted = db.query(Chat).filter(
        Chat.document_id == document_id,
        Chat.user_id == user_id
    ).delete()
    db.commit()
    return {"message": f"Deleted {deleted} messages."}

