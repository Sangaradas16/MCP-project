from datetime import date
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Expense


def seed_sample_data():
    db: Session = SessionLocal()
    try:
        count = db.query(Expense).count()
        if count > 0:
            return
        samples = [
            {"description": "Monthly groceries", "category": "Food", "amount": 420.75, "date": date(2024, 1, 15)},
            {"description": "Parking fees", "category": "Transportation", "amount": 62.50, "date": date(2024, 1, 23)},
            {"description": "Gym membership", "category": "Health", "amount": 55.00, "date": date(2024, 2, 2)},
            {"description": "Electricity bill", "category": "Utilities", "amount": 120.40, "date": date(2024, 2, 10)},
            {"description": "Online subscription", "category": "Entertainment", "amount": 18.99, "date": date(2024, 2, 18)},
            {"description": "Dinner out", "category": "Food", "amount": 86.20, "date": date(2024, 3, 9)},
            {"description": "Gas refill", "category": "Transportation", "amount": 45.00, "date": date(2024, 3, 19)},
            {"description": "Doctor checkup", "category": "Health", "amount": 98.40, "date": date(2024, 3, 26)},
            {"description": "Water bill", "category": "Utilities", "amount": 33.80, "date": date(2024, 4, 4)},
            {"description": "Movie night", "category": "Entertainment", "amount": 28.00, "date": date(2024, 4, 14)},
            {"description": "Weekend groceries", "category": "Food", "amount": 175.40, "date": date(2024, 4, 22)},
        ]
        for record in samples:
            db.add(Expense(**record))
        db.commit()
    finally:
        db.close()
