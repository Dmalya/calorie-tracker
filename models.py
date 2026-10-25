from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    calories_per_serving = Column(Float, nullable=False)
    protein_per_serving = Column(Float, nullable=False)


class DailyLog(Base):
    __tablename__ = "daily_log"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    servings = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)

    food_item = relationship("FoodItem")


class DailySummary(Base):
    __tablename__ = "daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    calories_burnt = Column(Float, nullable=False, default=0)