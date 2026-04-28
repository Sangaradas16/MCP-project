from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from .database import get_db
from .schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseDelete,
    ExpenseOut,
    AnalyticsRequest,
    PredictionResponse,
    ChatRequest,
    ChatResponse,
)
from .tools.db_tool import DatabaseTool
from .tools.analysis_tool import AnalysisTool
from .tools.prediction_tool import PredictionTool
from .agent.agent import MCPAgent
from .assistant import AIResponder
from .models import Expense
from .database import engine
from pathlib import Path
import os

router = APIRouter()


def get_agent(db: Session):
    return MCPAgent(db)


@router.post("/add-expense", response_model=ExpenseOut)
def add_expense(item: ExpenseCreate, db: Session = Depends(get_db)):
    tool = DatabaseTool(db)
    result = tool.add_expense(item.dict())
    return result


@router.get("/get-expenses", response_model=list[ExpenseOut])
def get_expenses(db: Session = Depends(get_db)):
    return DatabaseTool(db).get_expenses()


@router.post("/update-expense", response_model=ExpenseOut)
def update_expense(update: ExpenseUpdate, db: Session = Depends(get_db)):
    tool = DatabaseTool(db)
    data = update.dict(exclude_unset=True)
    expense_id = data.pop("id")
    result = tool.update_expense(expense_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    return result


@router.post("/delete-expense", response_model=ExpenseOut)
def delete_expense(delete: ExpenseDelete, db: Session = Depends(get_db)):
    tool = DatabaseTool(db)
    result = tool.delete_expense(delete.id)
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    return result


@router.post("/analytics")
def analytics(request: AnalyticsRequest, db: Session = Depends(get_db)):
    db_tool = DatabaseTool(db)
    analysis = AnalysisTool(db_tool.get_expenses())
    category_trends = analysis.category_trends()
    anomalies = analysis.anomaly_detection()
    summary = db_tool.category_summary(period=request.period)
    trend = db_tool.monthly_trend()
    return {"category_trends": category_trends, "anomalies": anomalies, "category_summary": summary, "monthly_trend": trend}


@router.get("/predict", response_model=PredictionResponse)
def predict(db: Session = Depends(get_db)):
    tool = PredictionTool(DatabaseTool(db).get_expenses())
    return tool.predict_next_month()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    agent = get_agent(db)
    answer, tool_outputs = agent.handle(request.question)

    # If MCP agent generated a response (not empty), use it directly
    if answer.strip():
        response_text = answer
    else:
        # For general queries, let AI assistant handle the conversation
        responder = AIResponder()
        response_text = responder.generate(request.question, tool_outputs)

    return {"answer": response_text, "tool_outputs": tool_outputs}


@router.get("/")
def root():
    static_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")))
    return FileResponse(static_path)
