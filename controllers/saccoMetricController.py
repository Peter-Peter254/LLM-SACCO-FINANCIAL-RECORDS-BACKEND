from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from database.database import SessionLocal
from database.models import SaccoMetric
from schemas.saccoMetricSchema import SaccoMetricCreate, SaccoMetricResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=SaccoMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(metric: SaccoMetricCreate, db: db_dependency):
    new_metric = SaccoMetric(**metric.dict())
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric

@router.get("/", response_model=List[SaccoMetricResponse])
async def list_metrics(db: db_dependency):
    return db.query(SaccoMetric).order_by(SaccoMetric.year.desc()).all()
