from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_PATH
from core.logger import logger

# Создание движка базы данных
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Получение сессии БД"""
    return SessionLocal()

def init_database():
    """Инициализация базы данных"""
    try:
        # Импорт моделей
        from data.models import user, genre, book, reader, loan, fine
        
        # Создание таблиц
        Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована")
        
        # Создание начальных данных
        session = get_session()
        
        # Проверка существования жанров
        from data.models.genre import Genre
        if session.query(Genre).count() == 0:
            genres = [
                Genre(name='Художественная литература'),
                Genre(name='Научная литература'),
                Genre(name='Учебная литература'),
                Genre(name='Справочная литература'),
                Genre(name='Детская литература'),
                Genre(name='Техническая литература')
            ]
            session.add_all(genres)
            session.commit()
            logger.info("Жанры добавлены")
        
        # Проверка существования администратора
        from data.models.user import User
        from core.security import hash_password
        
        if session.query(User).count() == 0:
            admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                full_name='Администратор системы',
                role='admin'
            )
            librarian = User(
                username='librarian',
                password_hash=hash_password('lib123'),
                full_name='Библиотекарь',
                role='librarian'
            )
            session.add_all([admin, librarian])
            session.commit()
            logger.info("Пользователи по умолчанию созданы")
        
        session.close()
        
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise