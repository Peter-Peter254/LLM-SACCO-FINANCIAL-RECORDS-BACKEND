
---

### 🧠 Backend `README.md` – [LLM-SACCO-FINANCIAL-RECORDS-BACKEND](https://github.com/Peter-Peter254/LLM-SACCO-FINANCIAL-RECORDS-BACKEND)

```markdown
# SACCO Financial Records LLM - Backend

A FastAPI backend that powers intelligent querying of SACCO financial statements. It uses OpenAI, ChromaDB, and cron-based extraction pipelines to transform PDFs into structured metrics and embeddings.

## 📚 API Docs

Access full interactive Swagger docs here:  
👉 [https://llm-sacco-financial-records-backend-production.up.railway.app/docs](https://llm-sacco-financial-records-backend-production.up.railway.app/docs)

## ⚙️ Technologies Used

- **FastAPI** – High-performance Python backend
- **MySQL** – Primary database
- **Supabase Auth** – Auth as a Service
- **JWT** – Token-based authentication
- **Docker** – Containerized deployment
- **Railway** – Cloud hosting
- **ChromaDB** – Local vector store for embeddings
- **OpenAI** – GPT-based natural language interface

## 🔄 Flow of Data

1. Admin uploads PDF via frontend
2. Backend stores file & triggers CRON job
3. Background job extracts:
   - Raw text via `pdfplumber`
   - Metrics for dashboard
   - Embeddings for ChromaDB
4. User queries AI → GPT + Chroma returns results

## 🚀 Running Locally

### 1. Clone & Setup

```bash
git clone https://github.com/Peter-Peter254/LLM-SACCO-FINANCIAL-RECORDS-BACKEND.git
cd LLM-SACCO-FINANCIAL-RECORDS-BACKEND
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

start command: uvicorn main:app --reload    
