from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import SaccoMetric, Document , User
from sqlalchemy import func
from auth.dependencies import get_current_user

router = APIRouter()

@router.get("/years")
def get_available_years(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    years = db.query(SaccoMetric.year).distinct().order_by(SaccoMetric.year.desc()).all()
    return [year[0] for year in years]

@router.get("/documents")
def get_documents_for_year(year: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document.id, Document.name).filter(Document.year == year).order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "name": d.name} for d in docs]

@router.get("/metrics")
def get_average_metrics(year: int = Query(None), document_id: str = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if document_id:
        metric = db.query(SaccoMetric).filter(SaccoMetric.document_id == document_id).first()
    elif year:
        metric = db.query(
            func.avg(SaccoMetric.membership_count).label("membership_count"),
            func.avg(SaccoMetric.loan_book_value).label("loan_book_value"),
            func.avg(SaccoMetric.asset_base).label("asset_base"),
            func.avg(SaccoMetric.deposits).label("deposits"),
            func.avg(SaccoMetric.dividend_rate).label("dividend_rate"),
            func.avg(SaccoMetric.interest_rebate).label("interest_rebate"),
            func.avg(SaccoMetric.revenue).label("revenue"),
            func.avg(SaccoMetric.portfolio_at_risk).label("portfolio_at_risk")
        ).filter(SaccoMetric.year == year).first()
    else:
        metric = db.query(
            func.avg(SaccoMetric.membership_count).label("membership_count"),
            func.avg(SaccoMetric.loan_book_value).label("loan_book_value"),
            func.avg(SaccoMetric.asset_base).label("asset_base"),
            func.avg(SaccoMetric.deposits).label("deposits"),
            func.avg(SaccoMetric.dividend_rate).label("dividend_rate"),
            func.avg(SaccoMetric.interest_rebate).label("interest_rebate"),
            func.avg(SaccoMetric.revenue).label("revenue"),
            func.avg(SaccoMetric.portfolio_at_risk).label("portfolio_at_risk")
        ).first()

    return {
        "membershipCount": int(metric.membership_count or 0),
        "loanBookValue": float(metric.loan_book_value or 0),
        "assetBase": float(metric.asset_base or 0),
        "deposits": float(metric.deposits or 0),
        "dividendRate": float(metric.dividend_rate or 0),
        "interestRebate": float(metric.interest_rebate or 0),
        "revenue": float(metric.revenue or 0),
        "portfolioAtRisk": float(metric.portfolio_at_risk or 0),
    }
