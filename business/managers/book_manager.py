from data.database import get_session
from data.models.book import Book
from data.models.genre import Genre
from core.logger import logger

class BookManager:
    
    @staticmethod
    def add_book(title, author, genre_id, quantity, isbn=None, publisher=None, year=None, description=None):
        """Добавить книгу в каталог"""
        session = get_session()
        try:
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                publisher=publisher,
                year=year,
                genre_id=genre_id,
                quantity=quantity,
                available_quantity=quantity,
                description=description
            )
            session.add(book)
            session.commit()
            logger.info(f"Книга добавлена: {title}")
            return book
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка добавления книги: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_all_books():
        """Получить все книги"""
        session = get_session()
        try:
            books = session.query(Book).all()
            return books
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def search_books(query):
        """Универсальный поиск книг по названию, автору или ISBN"""
        session = get_session()
        try:
            books = session.query(Book).filter(
                (Book.title.like(f'%{query}%')) |
                (Book.author.like(f'%{query}%')) |
                (Book.isbn.like(f'%{query}%'))
            ).all()
            return books
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_book_by_id(book_id):
        """Получить книгу по ID"""
        session = get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            return book
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def update_book(book_id, **kwargs):
        """Обновить информацию о книге"""
        session = get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                for key, value in kwargs.items():
                    if hasattr(book, key):
                        setattr(book, key, value)
                session.commit()
                logger.info(f"Книга обновлена: ID {book_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка обновления книги: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete_book(book_id):
        """Удалить книгу"""
        session = get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                # Проверка наличия активных выдач
                from data.models.loan import Loan
                active_loans = session.query(Loan).filter(
                    Loan.book_id == book_id,
                    Loan.status == 'active'
                ).count()
                
                if active_loans > 0:
                    raise Exception("Невозможно удалить книгу с активными выдачами")
                
                session.delete(book)
                session.commit()
                logger.info(f"Книга удалена: ID {book_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка удаления книги: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_all_genres():
        """Получить все жанры"""
        session = get_session()
        try:
            genres = session.query(Genre).all()
            return genres
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_books_by_genre(genre_id):
        """Получить книги по жанру"""
        session = get_session()
        try:
            books = session.query(Book).filter(Book.genre_id == genre_id).all()
            return books
        except Exception as e:
            session.close()
            raise
    
    @staticmethod
    def get_available_books():
        """Получить доступные книги"""
        session = get_session()
        try:
            books = session.query(Book).filter(Book.available_quantity > 0).all()
            return books
        except Exception as e:
            session.close()
            raise