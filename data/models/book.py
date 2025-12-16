from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), unique=True)
    title = Column(String(300), nullable=False)
    author = Column(String(200), nullable=False)
    publisher = Column(String(200))
    year = Column(Integer)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    quantity = Column(Integer, nullable=False, default=1)
    available_quantity = Column(Integer, nullable=False, default=1)
    description = Column(Text)
    cover_image = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # Связи
    genre = relationship("Genre", backref="books")
    
    def decrease_quantity(self):
        """Уменьшить доступное количество"""
        if self.available_quantity > 0:
            self.available_quantity -= 1
            return True
        return False
    
    def increase_quantity(self):
        """Увеличить доступное количество"""
        if self.available_quantity < self.quantity:
            self.available_quantity += 1
            return True
        return False
    
    def is_available(self) -> bool:
        """Проверка доступности книги"""
        return self.available_quantity > 0
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"