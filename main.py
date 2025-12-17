import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from data.database import init_database
from core.logger import logger
from config import APP_NAME, APP_VERSION


def main():
    """Главная функция приложения"""
    
    # Инициализация приложения
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Включение High DPI масштабирования
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Инициализация базы данных
        logger.info("Запуск приложения...")
        init_database()
        
        # Диалог входа
        login_dialog = LoginDialog()
        
        if login_dialog.exec_():
            # Успешная авторизация
            current_user = login_dialog.current_user
            logger.info(f"Авторизация успешна: {current_user['username']}")
            
            # Создание и показ главного окна
            main_window = MainWindow(current_user)
            main_window.show()
            
            # Запуск цикла приложения
            sys.exit(app.exec_())
        else:
            # Отмена входа
            logger.info("Вход отменен пользователем")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            'Критическая ошибка',
            f'Произошла критическая ошибка:\n{str(e)}\n\nПриложение будет закрыто.'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()