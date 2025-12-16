from data.database import get_session
from data.models.fine import Fine
from data.models.loan import Loan
from core.logger import logger
from config import FINE_RATE_PER_DAY

class FineManager:
    
    @staticmethod
    def create_fine(loan_id, days_overdue, session=None):
        """Создать штраф"""
        close_session = False
        if session is None:
            session = get_session()
            close_session = True
        
        try:
            amount = days_overdue * FINE_RATE_PER_DAY
            
            fine = Fine(
                loan_id=loan_id,
                amount=amount,
                status='unpaid'
            )
            
            session.add(fine)
            if close_session:
                session.commit()
            
            logger.info(f"Штраф создан: Loan ID {loan_id}, Amount {amount}")
            return amount
        except Exception as e:
            if close_session:
                session.rollback()
            logger.error(f"Ошибка создания штрафа: {e}")
            raise
        finally:
            if close_session:
                session.close()
    
    @staticmethod
    def pay_fine(fine_id, amount=None):
        """Оплатить штраф"""
        session = get_session()
        try:
            fine = session.query(Fine).filter(Fine.id == fine_id).first()
            if not fine:
                raise Exception("Штраф не найден")
            
            if amount is None:
                # Полная оплата
                fine.pay_full()
            else:
                # Частичная оплата
                fine.pay_partial(amount)
            
            session.commit()
            logger.info(f"Штраф оплачен: Fine ID {fine_id}, Amount {amount}")
            return fine
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка оплаты штрафа: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_unpaid_fines_by_reader(reader_id):
        """Получить неоплаченные штрафы читателя"""
        session = get_session()
        try:
            fines = session.query(Fine).join(Loan).filter(
                Loan.reader_id == reader_id,
                Fine.status.in_(['unpaid', 'partially_paid'])
            ).all()
            return fines
        finally:
            session.close()
    
    @staticmethod
    def get_all_unpaid_fines():
        """Получить все неоплаченные штрафы"""
        session = get_session()
        try:
            fines = session.query(Fine).filter(
                Fine.status.in_(['unpaid', 'partially_paid'])
            ).all()
            return fines
        finally:
            session.close()
    
    @staticmethod
    def get_fine_by_loan(loan_id):
        """Получить штраф по выдаче"""
        session = get_session()
        try:
            fine = session.query(Fine).filter(Fine.loan_id == loan_id).first()
            return fine
        finally:
            session.close()