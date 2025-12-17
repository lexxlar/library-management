from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text
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
    notes = Column(Text)
    condition_notes = Column(Text)  # Примечания о состоянии книги при возврате
    
    # Связи
    book = relationship("Book", backref="loans")
    reader = relationship("Reader", backref="loans")
    librarian = relationship("User", backref="loans")
    
    def is_overdue(self) -> bool:
        """Проверка просрочки"""
        if self.status == 'returned':
            return False
        return date.today() > self.due_date
    
    def get_overdue_days(self) -> int:
        """Расчет дней просрочки (используется в UI)"""
        if self.status == 'returned':
            # Если книга уже возвращена, считаем просрочку от даты возврата
            if self.return_date:
                return_date_only = self.return_date.date()
                if return_date_only > self.due_date:
                    return (return_date_only - self.due_date).days
            return 0
        
        # Для активных выдач считаем от текущей даты
        if date.today() > self.due_date:
            return (date.today() - self.due_date).days
        return 0
    
    def calculate_days_overdue(self) -> int:
        """Алиас для обратной совместимости"""
        return self.get_overdue_days()
    
    def mark_as_returned(self, condition_notes=None):
        """Пометить как возвращенную"""
        self.return_date = datetime.now()
        self.status = 'returned'
        if condition_notes:
            self.condition_notes = condition_notes
    
    def __repr__(self):
        return f"<Loan(book_id={self.book_id}, reader_id={self.reader_id}, status='{self.status}')>"