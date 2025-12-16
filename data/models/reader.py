from sqlalchemy import Column, Integer, String, Date, Boolean, Text, DateTime
from datetime import datetime, date
from data.database import Base

class Reader(Base):
    __tablename__ = 'readers'
    
    id = Column(Integer, primary_key=True)
    card_number = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    birth_date = Column(Date)
    category = Column(String(20), nullable=False)  # student, teacher, staff, external
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(300))
    photo = Column(String(500))
    registration_date = Column(Date, default=date.today)
    is_blocked = Column(Boolean, default=False)
    notes = Column(Text)
    
    def get_full_name(self) -> str:
        """Получить полное имя"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    def __repr__(self):
        return f"<Reader(card_number='{self.card_number}', name='{self.get_full_name()}')>"