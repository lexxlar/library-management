from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QComboBox,
                             QSpinBox, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from business.managers.book_manager import BookManager

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Добавить книгу')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Форма
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText('Введите название книги')
        form_layout.addRow('Название *:', self.title_input)
        
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText('Введите автора')
        form_layout.addRow('Автор *:', self.author_input)
        
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText('ISBN (опционально)')
        form_layout.addRow('ISBN:', self.isbn_input)
        
        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText('Издательство')
        form_layout.addRow('Издательство:', self.publisher_input)
        
        self.year_input = QSpinBox()
        self.year_input.setRange(1000, 2100)
        self.year_input.setValue(2024)
        form_layout.addRow('Год издания:', self.year_input)
        
        self.genre_combo = QComboBox()
        self.load_genres()
        form_layout.addRow('Жанр *:', self.genre_combo)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.quantity_input.setValue(1)
        form_layout.addRow('Количество *:', self.quantity_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText('Краткое описание книги')
        form_layout.addRow('Описание:', self.description_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_button = QPushButton('Сохранить')
        save_button.setStyleSheet('background-color: #4CAF50; color: white; padding: 8px 15px;')
        save_button.clicked.connect(self.save_book)
        
        cancel_button = QPushButton('Отмена')
        cancel_button.setStyleSheet('background-color: #f44336; color: white; padding: 8px 15px;')
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_genres(self):
        """Загрузка жанров"""
        genres = BookManager.get_all_genres()
        for genre in genres:
            self.genre_combo.addItem(genre.name, genre.id)
    
    def save_book(self):
        """Сохранение книги"""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        
        if not title or not author:
            QMessageBox.warning(self, 'Ошибка', 'Заполните обязательные поля!')
            return
        
        try:
            BookManager.add_book(
                title=title,
                author=author,
                isbn=self.isbn_input.text().strip() or None,
                publisher=self.publisher_input.text().strip() or None,
                year=self.year_input.value(),
                genre_id=self.genre_combo.currentData(),
                quantity=self.quantity_input.value(),
                description=self.description_input.toPlainText().strip() or None
            )
            QMessageBox.information(self, 'Успех', 'Книга успешно добавлена!')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка добавления книги:\n{str(e)}')