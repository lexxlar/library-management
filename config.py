import os

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'library.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

# Создание директорий, если их нет
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Параметры приложения
APP_NAME = "Система управления библиотекой"
APP_VERSION = "1.0.0"

# Настройки выдачи книг (в днях)
LOAN_PERIODS = {
    'student': 14,
    'teacher': 30,
    'staff': 21,
    'external': 7
}

# Лимиты выдачи (количество книг одновременно)
LOAN_LIMITS = {
    'student': 5,
    'teacher': 10,
    'staff': 7,
    'external': 3
}

# Настройки штрафов
FINE_RATE_PER_DAY = 10.0  # рублей за день просрочки
MAX_EXTENSION_COUNT = 2
RESERVATION_EXPIRY_DAYS = 3