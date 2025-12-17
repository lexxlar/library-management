from data.database import get_session
from data.models.loan import Loan
from data.models.book import Book
from data.models.reader import Reader
from datetime import datetime, date, timedelta
from core.logger import logger
from config import LOAN_PERIODS

class LoanManager:
    
    @staticmethod
    def calculate_due_date(category, due_date=None):
        """Расчет срока возврата"""
        if due_date:
            return due_date
        days = LOAN_PERIODS.get(category, 14)
        return date.today() + timedelta(days=days)
    
    @staticmethod
    def create_loan(reader_id, book_id, due_date, librarian_id=None, notes=None):
        """Создать выдачу книги"""
        session = get_session()
        try:
            # Проверка доступности книги
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book or not book.is_available():
                raise Exception("Книга недоступна")
            
            # Проверка читателя
            reader = session.query(Reader).filter(Reader.id == reader_id).first()
            if not reader:
                raise Exception("Читатель не найден")
            
            if reader.is_blocked:
                raise Exception("Читательский билет заблокирован")
            
            # Создание выдачи
            loan = Loan(
                book_id=book_id,
                reader_id=reader_id,
                librarian_id=librarian_id,
                due_date=due_date,
                status='active',
                notes=notes
            )
            
            # Уменьшение доступного количества
            book.decrease_quantity()
            
            session.add(loan)
            session.commit()
            logger.info(f"Книга выдана: Book ID {book_id}, Reader ID {reader_id}")
            return loan
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка выдачи книги: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def return_book(loan_id, condition_notes=None, fine_amount=0):
        """Вернуть книгу"""
        session = get_session()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                raise Exception("Выдача не найдена")
            
            if loan.status == 'returned':
                raise Exception("Книга уже возвращена")
            
            # Обновление статуса выдачи
            loan.return_date = datetime.now()
            loan.status = 'returned'
            loan.condition_notes = condition_notes
            
            # Увеличение доступного количества
            book = session.query(Book).filter(Book.id == loan.book_id).first()
            book.increase_quantity()
            
            # Создание штрафа если указана сумма
            if fine_amount > 0:
                from business.managers.fine_manager import FineManager
                from data.models.fine import Fine
                
                fine = Fine(
                    loan_id=loan_id,
                    amount=fine_amount,
                    status='unpaid'
                )
                session.add(fine)
            
            session.commit()
            logger.info(f"Книга возвращена: Loan ID {loan_id}")
            return loan
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка возврата книги: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def extend_loan(loan_id):
        """Продлить срок пользования"""
        session = get_session()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                raise Exception("Выдача не найдена")
            
            if loan.status != 'active':
                raise Exception("Невозможно продлить завершенную выдачу")
            
            # Получение читателя для расчета периода продления
            reader = session.query(Reader).filter(Reader.id == loan.reader_id).first()
            days = LOAN_PERIODS.get(reader.category, 14)
            
            # Продление от текущего срока возврата
            loan.due_date = loan.due_date + timedelta(days=days)
            
            session.commit()
            logger.info(f"Срок продлен: Loan ID {loan_id}")
            return loan
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка продления срока: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_active_loans():
        """Получить все активные выдачи"""
        session = get_session()
        try:
            loans = session.query(Loan).filter(Loan.status == 'active').all()
            # Важно: не закрываем сессию, чтобы можно было обращаться к связанным объектам
            return loans
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_overdue_loans():
        """Получить просроченные выдачи"""
        session = get_session()
        try:
            loans = session.query(Loan).filter(
                Loan.status == 'active',
                Loan.due_date < date.today()
            ).all()
            return loans
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_loans_due_today():
        """Получить выдачи, срок которых истекает сегодня"""
        session = get_session()
        try:
            loans = session.query(Loan).filter(
                Loan.status == 'active',
                Loan.due_date == date.today()
            ).all()
            return loans
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def search_active_loans(query):
        """Поиск активных выдач"""
        session = get_session()
        try:
            loans = session.query(Loan).join(Reader).join(Book).filter(
                Loan.status == 'active',
                (Reader.last_name.like(f'%{query}%')) |
                (Reader.first_name.like(f'%{query}%')) |
                (Reader.card_number.like(f'%{query}%')) |
                (Book.title.like(f'%{query}%'))
            ).all()
            return loans
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_loan_history(limit=100):
        """Получить историю выдач"""
        session = get_session()
        try:
            loans = session.query(Loan).order_by(Loan.loan_date.desc()).limit(limit).all()
            return loans
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_loan_by_id(loan_id):
        """Получить выдачу по ID"""
        session = get_session()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            return loan
        except Exception as e:
            session.close()
            raise