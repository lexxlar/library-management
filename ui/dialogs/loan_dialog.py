from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QMessageBox, QFormLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from business.managers.loan_manager import LoanManager
from business.managers.book_manager import BookManager
from business.managers.reader_manager import ReaderManager

class LoanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_book_id = None
        self.selected_reader_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Выдача книги')
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel('Выдача книги читателю')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; padding: 10px;')
        layout.addWidget(title_label)
        
        # Форма
        form_layout = QFormLayout()
        
        # Поиск читателя
        reader_search_layout = QHBoxLayout()
        self.reader_search_input = QLineEdit()
        self.reader_search_input.setPlaceholderText('Введите фамилию или читательский билет')
        self.reader_search_button = QPushButton('Найти')
        self.reader_search_button.setStyleSheet('background-color: #2196F3; color: white; padding: 5px 15px;')
        self.reader_search_button.clicked.connect(self.search_reader)
        reader_search_layout.addWidget(self.reader_search_input)
        reader_search_layout.addWidget(self.reader_search_button)
        form_layout.addRow('Поиск читателя:', reader_search_layout)
        
        # Выбранный читатель
        self.reader_label = QLabel('Читатель не выбран')
        self.reader_label.setStyleSheet('color: #666; padding: 5px;')
        form_layout.addRow('Выбран:', self.reader_label)
        
        # Таблица найденных читателей
        self.readers_table = QTableWidget()
        self.readers_table.setColumnCount(4)
        self.readers_table.setHorizontalHeaderLabels(['ID', 'ФИО', 'Категория', 'Билет'])
        self.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.readers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.readers_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.readers_table.setMaximumHeight(150)
        self.readers_table.itemSelectionChanged.connect(self.on_reader_selected)
        self.readers_table.setVisible(False)
        layout.addWidget(self.readers_table)
        
        # Поиск книги
        book_search_layout = QHBoxLayout()
        self.book_search_input = QLineEdit()
        self.book_search_input.setPlaceholderText('Введите название книги или автора')
        self.book_search_button = QPushButton('Найти')
        self.book_search_button.setStyleSheet('background-color: #2196F3; color: white; padding: 5px 15px;')
        self.book_search_button.clicked.connect(self.search_book)
        book_search_layout.addWidget(self.book_search_input)
        book_search_layout.addWidget(self.book_search_button)
        form_layout.addRow('Поиск книги:', book_search_layout)
        
        # Выбранная книга
        self.book_label = QLabel('Книга не выбрана')
        self.book_label.setStyleSheet('color: #666; padding: 5px;')
        form_layout.addRow('Выбрана:', self.book_label)
        
        # Таблица найденных книг
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(['ID', 'Название', 'Автор', 'Доступно', 'Всего'])
        self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.books_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.books_table.setMaximumHeight(200)
        self.books_table.itemSelectionChanged.connect(self.on_book_selected)
        self.books_table.setVisible(False)
        layout.addWidget(self.books_table)
        
        # Дата возврата
        self.return_date_input = QDateEdit()
        self.return_date_input.setCalendarPopup(True)
        self.return_date_input.setDate(QDate.currentDate().addDays(14))  # 2 недели по умолчанию
        self.return_date_input.setMinimumDate(QDate.currentDate().addDays(1))
        form_layout.addRow('Дата возврата *:', self.return_date_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.loan_button = QPushButton('Выдать книгу')
        self.loan_button.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px 20px; font-weight: bold;')
        self.loan_button.clicked.connect(self.create_loan)
        self.loan_button.setEnabled(False)
        
        cancel_button = QPushButton('Отмена')
        cancel_button.setStyleSheet('background-color: #f44336; color: white; padding: 10px 20px;')
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.loan_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def search_reader(self):
        """Поиск читателя"""
        search_text = self.reader_search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, 'Ошибка', 'Введите данные для поиска!')
            return
        
        try:
            readers = ReaderManager.search_readers(search_text)
            
            self.readers_table.setRowCount(0)
            self.readers_table.setVisible(True)
            
            if not readers:
                QMessageBox.information(self, 'Результат', 'Читатели не найдены')
                return
            
            for reader in readers:
                row = self.readers_table.rowCount()
                self.readers_table.insertRow(row)
                
                self.readers_table.setItem(row, 0, QTableWidgetItem(str(reader.id)))
                self.readers_table.setItem(row, 1, QTableWidgetItem(reader.get_full_name()))
                self.readers_table.setItem(row, 2, QTableWidgetItem(reader.category))
                self.readers_table.setItem(row, 3, QTableWidgetItem(reader.card_number))
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка поиска:\n{str(e)}')
    
    def search_book(self):
        """Поиск книги"""
        search_text = self.book_search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, 'Ошибка', 'Введите данные для поиска!')
            return
        
        try:
            books = BookManager.search_books(search_text)
            
            self.books_table.setRowCount(0)
            self.books_table.setVisible(True)
            
            if not books:
                QMessageBox.information(self, 'Результат', 'Книги не найдены')
                return
            
            for book in books:
                row = self.books_table.rowCount()
                self.books_table.insertRow(row)
                
                self.books_table.setItem(row, 0, QTableWidgetItem(str(book.id)))
                self.books_table.setItem(row, 1, QTableWidgetItem(book.title))
                self.books_table.setItem(row, 2, QTableWidgetItem(book.author))
                self.books_table.setItem(row, 3, QTableWidgetItem(str(book.available_quantity)))
                self.books_table.setItem(row, 4, QTableWidgetItem(str(book.quantity)))
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка поиска:\n{str(e)}')
    
    def on_reader_selected(self):
        """Обработка выбора читателя"""
        selected_items = self.readers_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.selected_reader_id = int(self.readers_table.item(row, 0).text())
            reader_name = self.readers_table.item(row, 1).text()
            card_number = self.readers_table.item(row, 3).text()
            
            self.reader_label.setText(f'{reader_name} (билет: {card_number})')
            self.reader_label.setStyleSheet('color: #4CAF50; font-weight: bold; padding: 5px;')
            self.check_can_loan()
    
    def on_book_selected(self):
        """Обработка выбора книги"""
        selected_items = self.books_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.selected_book_id = int(self.books_table.item(row, 0).text())
            book_title = self.books_table.item(row, 1).text()
            book_author = self.books_table.item(row, 2).text()
            available = int(self.books_table.item(row, 3).text())
            
            if available <= 0:
                self.book_label.setText(f'"{book_title}" - {book_author} (НЕТ В НАЛИЧИИ)')
                self.book_label.setStyleSheet('color: #f44336; font-weight: bold; padding: 5px;')
                self.selected_book_id = None
            else:
                self.book_label.setText(f'"{book_title}" - {book_author} (доступно: {available})')
                self.book_label.setStyleSheet('color: #4CAF50; font-weight: bold; padding: 5px;')
            
            self.check_can_loan()
    
    def check_can_loan(self):
        """Проверка возможности выдачи"""
        self.loan_button.setEnabled(
            self.selected_reader_id is not None and 
            self.selected_book_id is not None
        )
    
    def create_loan(self):
        """Создание выдачи книги"""
        if not self.selected_reader_id or not self.selected_book_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите читателя и книгу!')
            return
        
        try:
            return_date = self.return_date_input.date().toPyDate()
            
            LoanManager.create_loan(
                reader_id=self.selected_reader_id,
                book_id=self.selected_book_id,
                due_date=return_date
            )
            
            QMessageBox.information(self, 'Успех', 'Книга успешно выдана!')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка выдачи книги:\n{str(e)}')