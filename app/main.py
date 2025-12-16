from fastapi import FastAPI, Depends
from app.auth import get_current_user
from app.db import engine
from app import models
from app.ingest import start_watcher
import threading
from app.db import SessionLocal
from app.models import Experiment

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RTG Microscopy Ingest Service")

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_watcher, daemon=True).start()

@app.get("/experiments")
def list_experiments(user=Depends(get_current_user)):
    if user.role != "admin":
        return {"detail": "Forbidden"}

    db = SessionLocal()
    experiments = db.query(Experiment).all()
    return experiments

    
