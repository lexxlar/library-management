import logging
import os
from datetime import datetime

def setup_logger():
    """Настройка логгера для приложения"""
    
    # Создание директории для логов
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Имя файла лога с датой
    log_file = os.path.join(log_dir, f'library_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Настройка логгера
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('LibraryApp')

logger = setup_logger()