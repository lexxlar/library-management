from data.database import get_session
from data.models.reader import Reader
from data.models.loan import Loan
from datetime import datetime, date
from core.logger import logger
from config import LOAN_LIMITS

class ReaderManager:
    
    @staticmethod
    def generate_card_number():
        """Генерация номера читательского билета"""
        session = get_session()
        try:
            year = date.today().year
            # Находим максимальный номер за текущий год
            last_reader = session.query(Reader).filter(
                Reader.card_number.like(f'{year}-%')
            ).order_by(Reader.id.desc()).first()
            
            if last_reader:
                last_num = int(last_reader.card_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            return f"{year}-{new_num:04d}"
        finally:
            session.close()
    
    @staticmethod
    def add_reader(first_name, last_name, category, middle_name=None, birth_date=None,
                   phone=None, email=None, address=None, notes=None):
        """Зарегистрировать нового читателя"""
        session = get_session()
        try:
            card_number = ReaderManager.generate_card_number()
            
            reader = Reader(
                card_number=card_number,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birth_date=birth_date,
                category=category,
                phone=phone,
                email=email,
                address=address,
                notes=notes
            )
            session.add(reader)
            session.commit()
            logger.info(f"Читатель зарегистрирован: {card_number}")
            return reader
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка регистрации читателя: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_all_readers():
        """Получить всех читателей"""
        session = get_session()
        try:
            readers = session.query(Reader).all()
            return readers
        finally:
            session.close()
    
    @staticmethod
    def search_readers(query):
        """Поиск читателей"""
        session = get_session()
        try:
            readers = session.query(Reader).filter(
                (Reader.last_name.like(f'%{query}%')) |
                (Reader.first_name.like(f'%{query}%')) |
                (Reader.card_number.like(f'%{query}%'))
            ).all()
            return readers
        finally:
            session.close()
    
    @staticmethod
    def get_reader_by_id(reader_id):
        """Получить читателя по ID"""
        session = get_session()
        try:
            reader = session.query(Reader).filter(Reader.id == reader_id).first()
            return reader
        finally:
            session.close()
    
    @staticmethod
    def get_reader_by_card(card_number):
        """Получить читателя по номеру билета"""
        session = get_session()
        try:
            reader = session.query(Reader).filter(Reader.card_number == card_number).first()
            return reader
        finally:
            session.close()
    
    @staticmethod
    def update_reader(reader_id, **kwargs):
        """Обновить данные читателя"""
        session = get_session()
        try:
            reader = session.query(Reader).filter(Reader.id == reader_id).first()
            if reader:
                for key, value in kwargs.items():
                    if hasattr(reader, key):
                        setattr(reader, key, value)
                session.commit()
                logger.info(f"Читатель обновлен: ID {reader_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка обновления читателя: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def block_reader(reader_id, block=True):
        """Заблокировать/разблокировать читателя"""
        session = get_session()
        try:
            reader = session.query(Reader).filter(Reader.id == reader_id).first()
            if reader:
                reader.is_blocked = block
                session.commit()
                status = "заблокирован" if block else "разблокирован"
                logger.info(f"Читатель {status}: ID {reader_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка блокировки читателя: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def can_borrow(reader_id):
        """Проверка возможности выдачи книг"""
        session = get_session()
        try:
            reader = session.query(Reader).filter(Reader.id == reader_id).first()
            if not reader:
                return False, "Читатель не найден"
            
            if reader.is_blocked:
                return False, "Читательский билет заблокирован"
            
            # Проверка просрочек
            overdue_loans = session.query(Loan).filter(
                Loan.reader_id == reader_id,
                Loan.status == 'active',
                Loan.due_date < date.today()
            ).count()
            
            if overdue_loans > 0:
                return False, f"Имеется {overdue_loans} просроченных книг"
            
            # Проверка лимита
            active_loans = session.query(Loan).filter(
                Loan.reader_id == reader_id,
                Loan.status == 'active'
            ).count()
            
            limit = LOAN_LIMITS.get(reader.category, 5)
            if active_loans >= limit:
                return False, f"Превышен лимит выдачи ({limit} книг)"
            
            return True, "OK"
        finally:
            session.close()
    
    @staticmethod
    def get_reader_loans(reader_id, active_only=True):
        """Получить выдачи читателя"""
        session = get_session()
        try:
            query = session.query(Loan).filter(Loan.reader_id == reader_id)
            if active_only:
                query = query.filter(Loan.status == 'active')
            loans = query.all()
            return loans
        finally:
            session.close()