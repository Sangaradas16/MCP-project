from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Expense


class DatabaseTool:
    def __init__(self, db: Session):
        self.db = db

    def add_expense(self, data):
        item = Expense(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_expenses(self):
        return self.db.query(Expense).order_by(Expense.date.desc()).all()

    def get_expense(self, expense_id: int):
        return self.db.query(Expense).filter(Expense.id == expense_id).first()

    def update_expense(self, expense_id: int, updates: dict):
        expense = self.get_expense(expense_id)
        if not expense:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(expense, key):
                setattr(expense, key, value)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete_expense(self, expense_id: int):
        expense = self.get_expense(expense_id)
        if not expense:
            return None
        self.db.delete(expense)
        self.db.commit()
        return expense

    def category_summary(self, period: str = "monthly"):
        query = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.strftime("%Y-%m", Expense.date).label("period")
        )
        query = query.group_by(Expense.category, "period")
        rows = query.order_by("period").all()
        result = {}
        for category, total, period_key in rows:
            if category not in result:
                result[category] = []
            result[category].append({"period": period_key, "total": float(total)})
        return result

    def monthly_trend(self, months: int = 12):
        query = self.db.query(
            func.strftime("%Y-%m", Expense.date).label("period"),
            func.sum(Expense.amount).label("total")
        ).group_by("period").order_by("period")
        rows = query.all()
        history = [{"period": period, "total": float(total)} for period, total in rows]
        return history
