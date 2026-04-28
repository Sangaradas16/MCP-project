from datetime import date
from pydantic import BaseModel
from typing import List, Optional, Dict


class ExpenseBase(BaseModel):
    description: str
    category: str
    amount: float
    date: date


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    id: int
    description: Optional[str]
    category: Optional[str]
    amount: Optional[float]
    date: Optional[date]


class ExpenseDelete(BaseModel):
    id: int


class ExpenseOut(ExpenseBase):
    id: int

    class Config:
        from_attributes = True


class AnalyticsRequest(BaseModel):
    period: str = "monthly"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PredictionResponse(BaseModel):
    next_period: str
    forecast: float
    history: List[Dict[str, float]]


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    tool_outputs: Optional[Dict[str, object]] = None
