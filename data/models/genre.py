from sqlalchemy import Column, Integer, String, Text
from data.database import Base

class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    def __repr__(self):
        return f"<Genre(name='{self.name}')>"