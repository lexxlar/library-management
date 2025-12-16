from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
from data.database import Base

class Loan(Base):
    __tablename__ = 'loans'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    reader_id = Column(Integer, ForeignKey('readers.id'), nullable=False)
    loan_date = Column(DateTime, default=datetime.now)
    due_date = Column(Date, nullable=False)
    return_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, returned, overdue
    librarian_id = Column(Integer, ForeignKey('users.id'))
    notes = Column(String(500))
    
    # Связи
    book = relationship("Book", backref="loans")
    reader = relationship("Reader", backref="loans")
    librarian = relationship("User", backref="loans")
    
    def is_overdue(self) -> bool:
        """Проверка просрочки"""
        if self.status == 'returned':
            return False
        return date.today() > self.due_date
    
    def calculate_days_overdue(self) -> int:
        """Расчет дней просрочки"""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days
    
    def __repr__(self):
        return f"<Loan(book_id={self.book_id}, reader_id={self.reader_id}, status='{self.status}')>"