from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional
import models
from database import engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ----------- Pydantic Schemas -----------

class FoodItemCreate(BaseModel):
    name: str
    calories_per_serving: float
    protein_per_serving: float

class FoodItemUpdate(BaseModel):
    name: str
    calories_per_serving: float
    protein_per_serving: float

class DailyLogCreate(BaseModel):
    date: date
    food_item_id: int
    servings: float

class CaloriesBurntUpdate(BaseModel):
    date: date
    calories_burnt: float


# ----------- Page Routes -----------

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# ----------- Inventory API -----------

@app.get("/api/food-items")
def get_food_items(db: Session = Depends(get_db)):
    return db.query(models.FoodItem).order_by(models.FoodItem.name).all()

@app.post("/api/food-items")
def create_food_item(item: FoodItemCreate, db: Session = Depends(get_db)):
    existing = db.query(models.FoodItem).filter(
        func.lower(models.FoodItem.name) == item.name.strip().lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Food item already exists")
    db_item = models.FoodItem(
        name=item.name.strip(),
        calories_per_serving=item.calories_per_serving,
        protein_per_serving=item.protein_per_serving
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/api/food-items/{item_id}")
def update_food_item(item_id: int, item: FoodItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.FoodItem).filter(models.FoodItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name.strip()
    db_item.calories_per_serving = item.calories_per_serving
    db_item.protein_per_serving = item.protein_per_serving
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/food-items/{item_id}")
def delete_food_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.FoodItem).filter(models.FoodItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}


# ----------- Daily Log API -----------

@app.get("/api/daily-log")
def get_daily_log(date: date, db: Session = Depends(get_db)):
    entries = db.query(models.DailyLog).filter(models.DailyLog.date == date).all()
    result = []
    for e in entries:
        result.append({
            "id": e.id,
            "date": str(e.date),
            "food_item_id": e.food_item_id,
            "food_item_name": e.food_item.name,
            "servings": e.servings,
            "calories": e.calories,
            "protein": e.protein
        })
    return result

@app.post("/api/daily-log")
def add_daily_log(entry: DailyLogCreate, db: Session = Depends(get_db)):
    food_item = db.query(models.FoodItem).filter(models.FoodItem.id == entry.food_item_id).first()
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
    log = models.DailyLog(
        date=entry.date,
        food_item_id=entry.food_item_id,
        servings=entry.servings,
        calories=round(food_item.calories_per_serving * entry.servings, 1),
        protein=round(food_item.protein_per_serving * entry.servings, 1)
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {
        "id": log.id,
        "date": str(log.date),
        "food_item_id": log.food_item_id,
        "food_item_name": food_item.name,
        "servings": log.servings,
        "calories": log.calories,
        "protein": log.protein
    }

@app.delete("/api/daily-log/{log_id}")
def delete_daily_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.DailyLog).filter(models.DailyLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log)
    db.commit()
    return {"ok": True}


# ----------- Calories Burnt API -----------

@app.get("/api/calories-burnt")
def get_calories_burnt(date: date, db: Session = Depends(get_db)):
    summary = db.query(models.DailySummary).filter(models.DailySummary.date == date).first()
    return {"date": str(date), "calories_burnt": summary.calories_burnt if summary else 0}

@app.post("/api/calories-burnt")
def save_calories_burnt(data: CaloriesBurntUpdate, db: Session = Depends(get_db)):
    summary = db.query(models.DailySummary).filter(models.DailySummary.date == data.date).first()
    if summary:
        summary.calories_burnt = data.calories_burnt
    else:
        summary = models.DailySummary(date=data.date, calories_burnt=data.calories_burnt)
        db.add(summary)
    db.commit()
    return {"ok": True}


# ----------- Weekly Stats API -----------

@app.get("/api/weekly-stats")
def get_weekly_stats(week_start: date, db: Session = Depends(get_db)):
    week_end = week_start + timedelta(days=6)
    rows = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        consumed = db.query(func.sum(models.DailyLog.calories)).filter(
            models.DailyLog.date == day
        ).scalar() or 0
        protein = db.query(func.sum(models.DailyLog.protein)).filter(
            models.DailyLog.date == day
        ).scalar() or 0
        summary = db.query(models.DailySummary).filter(
            models.DailySummary.date == day
        ).first()
        burnt = summary.calories_burnt if summary else 0
        balance = consumed - burnt
        rows.append({
            "date": str(day),
            "consumed": round(consumed, 1),
            "protein": round(protein, 1),
            "burnt": round(burnt, 1),
            "balance": round(balance, 1)
        })
    return rows