from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base

class Fine(Base):
    __tablename__ = 'fines'
    
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey('loans.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0.00)
    status = Column(String(20), default='unpaid')  # unpaid, partially_paid, paid
    created_at = Column(DateTime, default=datetime.now)
    paid_at = Column(DateTime)
    
    # Связи
    loan = relationship("Loan", backref="fines")
    
    def pay_partial(self, amount: float):
        """Частичная оплата штрафа"""
        self.paid_amount = float(self.paid_amount) + amount
        if self.paid_amount >= float(self.amount):
            self.status = 'paid'
            self.paid_at = datetime.now()
        else:
            self.status = 'partially_paid'
    
    def pay_full(self):
        """Полная оплата штрафа"""
        self.paid_amount = self.amount
        self.status = 'paid'
        self.paid_at = datetime.now()
    
    def is_paid(self) -> bool:
        """Проверка оплаты"""
        return self.status == 'paid'
    
    def __repr__(self):
        return f"<Fine(loan_id={self.loan_id}, amount={self.amount}, status='{self.status}')>"