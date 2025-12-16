from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QMessageBox, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from business.managers.reader_manager import ReaderManager

class AddReaderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Регистрация читателя')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Форма
        form_layout = QFormLayout()
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText('Фамилия')
        form_layout.addRow('Фамилия *:', self.last_name_input)
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText('Имя')
        form_layout.addRow('Имя *:', self.first_name_input)
        
        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText('Отчество (опционально)')
        form_layout.addRow('Отчество:', self.middle_name_input)
        
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate().addYears(-20))
        form_layout.addRow('Дата рождения:', self.birth_date_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem('Студент', 'student')
        self.category_combo.addItem('Преподаватель', 'teacher')
        self.category_combo.addItem('Сотрудник', 'staff')
        self.category_combo.addItem('Внешний читатель', 'external')
        form_layout.addRow('Категория *:', self.category_combo)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('+7 (___) ___-__-__')
        form_layout.addRow('Телефон:', self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('email@example.com')
        form_layout.addRow('Email:', self.email_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.address_input.setPlaceholderText('Адрес')
        form_layout.addRow('Адрес:', self.address_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_button = QPushButton('Зарегистрировать')
        save_button.setStyleSheet('background-color: #4CAF50; color: white; padding: 8px 15px;')
        save_button.clicked.connect(self.save_reader)
        
        cancel_button = QPushButton('Отмена')
        cancel_button.setStyleSheet('background-color: #f44336; color: white; padding: 8px 15px;')
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def save_reader(self):
        """Сохранение читателя"""
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        
        # Валидация обязательных полей
        if not last_name or not first_name:
            QMessageBox.warning(self, 'Ошибка', 'Заполните обязательные поля (Фамилия и Имя)!')
            return
        
        # Валидация email (если указан)
        email = self.email_input.text().strip()
        if email and '@' not in email:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный формат email!')
            return
        
        try:
            # Получение данных из формы
            middle_name = self.middle_name_input.text().strip() or None
            birth_date = self.birth_date_input.date().toPyDate()
            category = self.category_combo.currentData()
            phone = self.phone_input.text().strip() or None
            address = self.address_input.toPlainText().strip() or None
            
            # Добавление читателя через менеджер
            ReaderManager.add_reader(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                birth_date=birth_date,
                category=category,
                phone=phone,
                email=email or None,
                address=address
            )
            
            QMessageBox.information(self, 'Успех', 
                                  f'Читатель {last_name} {first_name} успешно зарегистрирован!')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', 
                               f'Ошибка регистрации читателя:\n{str(e)}')