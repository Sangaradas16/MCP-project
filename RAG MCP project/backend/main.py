import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .router import router
from .sample_data import seed_sample_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("expense_assistant")

app = FastAPI(title="Local Expense Tracking Assistant")
app.include_router(router)

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.on_event("startup")
def startup_event():
    logger.info("Creating database tables and seeding sample data")
    Base.metadata.create_all(bind=engine)
    seed_sample_data()


@app.get("/health")
def health_check():
    return {"status": "ok"}
