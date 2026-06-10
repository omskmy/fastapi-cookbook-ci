from sqlalchemy import Column, Integer, String, Text
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    cooking_time = Column(Integer, nullable=False)   # минуты
    views = Column(Integer, default=0)
    ingredients = Column(Text, nullable=False)
    description = Column(Text, nullable=False)