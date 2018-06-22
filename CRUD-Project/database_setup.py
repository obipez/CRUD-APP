import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class FoodItem(Base):
	__tablename__ = 'food_item'

	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	calories = Column(Integer)
	fat_cals = Column(Integer)
	total_fat = Column(Integer)
	saturated_fat = Column(Integer)
	trans_fat = Column(Integer)
	cholesterol = Column(Integer)
	sodium = Column(Integer)
	carbohydrates = Column(Integer)
	dietary_fiber = Column(Integer)
	sugars = Column(Integer)
	protein = Column(Integer)
	vitamin_a = Column(Integer)
	vitamin_c = Column(Integer)
	calcium = Column(Integer)
	iron = Column(Integer)

########INSERT AT END OF FILE #############

engine = create_engine('sqlite:///foodlists.db')
Base.metadata.create_all(engine)