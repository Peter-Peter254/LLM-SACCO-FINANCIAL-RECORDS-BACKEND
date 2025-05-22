from fastapi import FastAPI
from database.models import Base
from database.database import engine
from fastapi.middleware.cors import CORSMiddleware
import threading
from routes.api import api_router
from cronJobs.embedder import start_embedding_cron 
from cronJobs.metricsextractor import start_dashboard_cron

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB schema
Base.metadata.create_all(bind=engine)

# Routes
app.include_router(api_router)

# Background cron tasks
@app.on_event("startup")
def schedule_background_tasks():
    threading.Thread(target=start_dashboard_cron, daemon=True).start() 
    threading.Thread(target=start_embedding_cron, daemon=True).start()
