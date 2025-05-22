from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SaccoMetricCreate(BaseModel):
    document_id: str
    year: int
    membership_count: Optional[int] = 0
    loan_book_value: Optional[float] = 0
    asset_base: Optional[float] = 0
    deposits: Optional[float] = 0
    dividend_rate: Optional[float] = 0
    interest_rebate: Optional[float] = 0
    revenue: Optional[float] = 0
    portfolio_at_risk: Optional[float] = 0

class SaccoMetricResponse(SaccoMetricCreate):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
