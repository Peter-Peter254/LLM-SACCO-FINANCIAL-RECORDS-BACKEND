import os
import uuid
import time
import json
import schedule
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Document, SaccoMetric
from openai import OpenAI
from chromadb import PersistentClient

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = PersistentClient(path=".chroma")


def clean_metrics(metrics_dict):
    def safe_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0

    def safe_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0

    return {
        "membership_count": safe_int(metrics_dict.get("membership_count")),
        "loan_book_value": safe_float(metrics_dict.get("loan_book_value")),
        "asset_base": safe_float(metrics_dict.get("asset_base")),
        "deposits": safe_float(metrics_dict.get("deposits")),
        "dividend_rate": safe_float(metrics_dict.get("dividend_rate")),
        "interest_rebate": safe_float(metrics_dict.get("interest_rebate")),
        "revenue": safe_float(metrics_dict.get("revenue")),
        "portfolio_at_risk": safe_float(metrics_dict.get("portfolio_at_risk")),
    }


def ask_gpt_for_metrics(chunks):
    joined = "\n---\n".join(chunks)
    prompt = f"""
From the following SACCO report snippets, extract the following numeric values and return them in JSON format:
- membership_count
- loan_book_value
- asset_base
- deposits
- dividend_rate
- interest_rebate
- revenue
- portfolio_at_risk

Return format:
{{
  "membership_count": 220650,
  "loan_book_value": 50.24,
  ...
}}

TEXT:
{joined}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a financial data extractor."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip()
    print(f"GPT Response:\n{content}")

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.startswith("```"):
        content = content.removeprefix("```").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    try:
        parsed = json.loads(content)
        return clean_metrics(parsed)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return clean_metrics({})

def fetch_relevant_chunks(document_id, top_k=5):
    collection = chroma_client.get_or_create_collection(name="sacco_docs")

    embedding = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Summarize key SACCO financial metrics from this document"
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where={"document_id": document_id}
    )

    return results['documents'][0] if results and results['documents'] else []

def run_metrics_job():
    db: Session = SessionLocal()
    docs = db.query(Document).filter(Document.status == 2).all()

    if not docs:
        print("No embedded documents to process.")
        db.close()
        return

    for doc in docs:
        try:
            existing = db.query(SaccoMetric).filter(
                        SaccoMetric.document_id == doc.id,
                        SaccoMetric.year == doc.year
                    ).first()
            
            if existing:
                print(f"Skipping {doc.name} (already has metrics)")
                continue

            print(f"Processing: {doc.name}")
            chunks = fetch_relevant_chunks(doc.id)

            if not chunks:
                print(f"No chunks found for: {doc.name}")
                continue

            metrics = ask_gpt_for_metrics(chunks)

            db.add(SaccoMetric(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                year=doc.year,
                **metrics
            ))

            doc.status = 3
            db.commit()
            print(f"Metrics saved for: {doc.name}")

        except Exception as e:
            print(f" Error saving metrics for {doc.name}: {e}")
            db.rollback()

    db.close()


def start_dashboard_cron():
    #Changed this due to compute costs incurred should be 2
    schedule.every(200000).minutes.do(run_metrics_job)
    print("Dashboard Metrics Cron Started (every 5 minutes)")
    while True:
        schedule.run_pending()
        time.sleep(1)
