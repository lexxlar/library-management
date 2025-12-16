from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from data.database import get_session
from data.models.user import User
from datetime import datetime
from core.logger import logger

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Вход в систему')
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title_label = QLabel('Система управления библиотекой')
        title_font = QFont('Arial', 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel('Авторизация в системе')
        subtitle_font = QFont('Arial', 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet('color: #666;')
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)
        
        # Поле логина
        login_layout = QHBoxLayout()
        login_label = QLabel('Логин:')
        login_label.setFixedWidth(80)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Введите логин')
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        layout.addLayout(login_layout)
        
        # Поле пароля
        password_layout = QHBoxLayout()
        password_label = QLabel('Пароль:')
        password_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Введите пароль')
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        layout.addSpacing(10)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.login_button = QPushButton('Войти')
        self.login_button.setFixedSize(100, 35)
        self.login_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        self.login_button.clicked.connect(self.handle_login)
        
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.setFixedSize(100, 35)
        self.cancel_button.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        ''')
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        # Информация
        info_label = QLabel('По умолчанию: admin / admin123')
        info_label.setStyleSheet('color: #999; font-size: 9px;')
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
        # Enter для входа
        self.password_input.returnPressed.connect(self.handle_login)
        
    def handle_login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return
        
        # Проверка в базе данных
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            
            if user and user.check_password(password):
                # Обновление времени последнего входа
                user.last_login = datetime.now()
                session.commit()
                
                self.current_user = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role
                }
                logger.info(f"Пользователь вошел: {username}")
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка входа', 
                                   'Неверный логин или пароль!')
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            logger.error(f"Ошибка входа: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Ошибка подключения к базе данных:\n{str(e)}')
        finally:
            session.close()