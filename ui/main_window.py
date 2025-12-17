from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QMessageBox, QHeaderView, QAbstractItemView,
                             QToolBar, QAction, QStatusBar, QMenuBar, QMenu, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont
from datetime import datetime

from ui.dialogs.add_book_dialog import AddBookDialog
from ui.dialogs.add_reader_dialog import AddReaderDialog
from ui.dialogs.loan_dialog import LoanDialog
from ui.dialogs.return_dialog import ReturnDialog
from business.managers.book_manager import BookManager
from business.managers.reader_manager import ReaderManager
from business.managers.loan_manager import LoanManager
from core.logger import logger


class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        self.load_initial_data()
        
    def init_ui(self):
        self.setWindowTitle('Система управления библиотекой')
        self.setGeometry(100, 100, 1200, 700)
        
        # Создание меню
        self.create_menu_bar()
        
        # Создание панели инструментов
        self.create_toolbar()
        
        # Создание центрального виджета с вкладками
        self.create_tabs()
        
        # Создание статус-бара
        self.create_status_bar()
        
        # Применение стилей
        self.apply_styles()
        
    def create_menu_bar(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        refresh_action = QAction('Обновить', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all_data)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Книги"
        books_menu = menubar.addMenu('Книги')
        
        add_book_action = QAction('Добавить книгу', self)
        add_book_action.setShortcut('Ctrl+B')
        add_book_action.triggered.connect(self.add_book)
        books_menu.addAction(add_book_action)
        
        # Меню "Читатели"
        readers_menu = menubar.addMenu('Читатели')
        
        add_reader_action = QAction('Зарегистрировать читателя', self)
        add_reader_action.setShortcut('Ctrl+R')
        add_reader_action.triggered.connect(self.add_reader)
        readers_menu.addAction(add_reader_action)
        
        # Меню "Выдача"
        loans_menu = menubar.addMenu('Выдача')
        
        loan_action = QAction('Выдать книгу', self)
        loan_action.setShortcut('Ctrl+L')
        loan_action.triggered.connect(self.create_loan)
        loans_menu.addAction(loan_action)
        
        return_action = QAction('Вернуть книгу', self)
        return_action.setShortcut('Ctrl+T')
        return_action.triggered.connect(self.return_book)
        loans_menu.addAction(return_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # Кнопки быстрого доступа
        add_book_btn = QAction('📚 Добавить книгу', self)
        add_book_btn.triggered.connect(self.add_book)
        toolbar.addAction(add_book_btn)
        
        add_reader_btn = QAction('👤 Новый читатель', self)
        add_reader_btn.triggered.connect(self.add_reader)
        toolbar.addAction(add_reader_btn)
        
        toolbar.addSeparator()
        
        loan_btn = QAction('➡️ Выдать книгу', self)
        loan_btn.triggered.connect(self.create_loan)
        toolbar.addAction(loan_btn)
        
        return_btn = QAction('⬅️ Вернуть книгу', self)
        return_btn.triggered.connect(self.return_book)
        toolbar.addAction(return_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QAction('🔄 Обновить', self)
        refresh_btn.triggered.connect(self.refresh_all_data)
        toolbar.addAction(refresh_btn)
        
    def create_tabs(self):
        """Создание вкладок"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка "Книги"
        self.books_tab = self.create_books_tab()
        self.tabs.addTab(self.books_tab, '📚 Книги')
        
        # Вкладка "Читатели"
        self.readers_tab = self.create_readers_tab()
        self.tabs.addTab(self.readers_tab, '👥 Читатели')
        
        # Вкладка "Выдачи"
        self.loans_tab = self.create_loans_tab()
        self.tabs.addTab(self.loans_tab, '📋 Активные выдачи')
        
        # Вкладка "История"
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, '📜 История')
        
    def create_books_tab(self):
        """Создание вкладки книг"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel('Поиск:')
        self.books_search_input = QLineEdit()
        self.books_search_input.setPlaceholderText('Введите название книги или автора...')
        self.books_search_input.returnPressed.connect(self.search_books)
        
        search_btn = QPushButton('🔍 Найти')
        search_btn.clicked.connect(self.search_books)
        
        clear_btn = QPushButton('✖ Очистить')
        clear_btn.clicked.connect(lambda: (self.books_search_input.clear(), self.load_books()))
        
        add_btn = QPushButton('➕ Добавить книгу')
        add_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 5px 15px;')
        add_btn.clicked.connect(self.add_book)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.books_search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        search_layout.addStretch()
        search_layout.addWidget(add_btn)
        
        layout.addLayout(search_layout)
        
        # Таблица книг
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Автор', 'Жанр', 'Год', 'Всего', 'Доступно'
        ])
        self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.books_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.books_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.books_table)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton('✏️ Редактировать')
        edit_btn.clicked.connect(self.edit_book)
        
        delete_btn = QPushButton('🗑️ Удалить')
        delete_btn.setStyleSheet('background-color: #f44336; color: white;')
        delete_btn.clicked.connect(self.delete_book)
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_readers_tab(self):
        """Создание вкладки читателей"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel('Поиск:')
        self.readers_search_input = QLineEdit()
        self.readers_search_input.setPlaceholderText('Введите фамилию читателя...')
        self.readers_search_input.returnPressed.connect(self.search_readers)
        
        search_btn = QPushButton('🔍 Найти')
        search_btn.clicked.connect(self.search_readers)
        
        clear_btn = QPushButton('✖ Очистить')
        clear_btn.clicked.connect(lambda: (self.readers_search_input.clear(), self.load_readers()))
        
        add_btn = QPushButton('➕ Новый читатель')
        add_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 5px 15px;')
        add_btn.clicked.connect(self.add_reader)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.readers_search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        search_layout.addStretch()
        search_layout.addWidget(add_btn)
        
        layout.addLayout(search_layout)
        
        # Таблица читателей
        self.readers_table = QTableWidget()
        self.readers_table.setColumnCount(6)
        self.readers_table.setHorizontalHeaderLabels([
            'ID', 'ФИО', 'Дата рождения', 'Категория', 'Телефон', 'Читательский билет'
        ])
        self.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.readers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.readers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.readers_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.readers_table)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        view_btn = QPushButton('👁️ Просмотр')
        view_btn.clicked.connect(self.view_reader)
        
        edit_btn = QPushButton('✏️ Редактировать')
        edit_btn.clicked.connect(self.edit_reader)
        
        actions_layout.addWidget(view_btn)
        actions_layout.addWidget(edit_btn)
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_loans_tab(self):
        """Создание вкладки активных выдач"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок и статистика
        header_layout = QHBoxLayout()
        title_label = QLabel('Активные выдачи книг')
        title_label.setStyleSheet('font-size: 14px; font-weight: bold;')
        
        self.loans_count_label = QLabel('Всего: 0')
        self.overdue_count_label = QLabel('Просрочено: 0')
        self.overdue_count_label.setStyleSheet('color: red; font-weight: bold;')
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.loans_count_label)
        header_layout.addWidget(self.overdue_count_label)
        
        layout.addLayout(header_layout)
        
        # Фильтры
        filter_layout = QHBoxLayout()
        filter_label = QLabel('Фильтр:')
        self.loans_filter_combo = QComboBox()
        self.loans_filter_combo.addItem('Все выдачи', 'all')
        self.loans_filter_combo.addItem('Только просроченные', 'overdue')
        self.loans_filter_combo.addItem('Срок истекает сегодня', 'today')
        self.loans_filter_combo.currentIndexChanged.connect(self.load_loans)
        
        refresh_loans_btn = QPushButton('🔄 Обновить')
        refresh_loans_btn.clicked.connect(self.load_loans)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.loans_filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_loans_btn)
        
        layout.addLayout(filter_layout)
        
        # Таблица выдач
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(7)
        self.loans_table.setHorizontalHeaderLabels([
            'ID', 'Читатель', 'Книга', 'Автор', 'Дата выдачи', 'Срок возврата', 'Просрочка'
        ])
        self.loans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.loans_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.loans_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.loans_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.loans_table)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        return_btn = QPushButton('⬅️ Вернуть книгу')
        return_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 8px 15px;')
        return_btn.clicked.connect(self.return_book)
        
        actions_layout.addWidget(return_btn)
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self):
        """Создание вкладки истории"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel('История выдач')
        title_label.setStyleSheet('font-size: 14px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            'ID', 'Читатель', 'Книга', 'Автор', 'Дата выдачи', 
            'Дата возврата', 'Фактический возврат', 'Статус'
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.history_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_bar(self):
        """Создание статус-бара"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Информация о пользователе
        user_info = f"Пользователь: {self.current_user['full_name']} ({self.current_user['role']})"
        self.status_bar.showMessage(user_info)
        
        # Время
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        self.update_time()
        
        # Таймер для обновления времени
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
    
    def update_time(self):
        """Обновление времени в статус-баре"""
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        self.time_label.setText(current_time)
    
    def apply_styles(self):
        """Применение глобальных стилей"""
        self.setStyleSheet('''
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QPushButton {
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        ''')
    
    # ========== ЗАГРУЗКА ДАННЫХ ==========
    
    def load_initial_data(self):
        """Первоначальная загрузка данных"""
        self.load_books()
        self.load_readers()
        self.load_loans()
        self.load_history()
        logger.info("Данные загружены в главное окно")
    
    def load_books(self):
        """Загрузка списка книг"""
        try:
            books = BookManager.get_all_books()
            self.display_books(books)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки книг:\n{str(e)}')
            logger.error(f"Ошибка загрузки книг: {e}")
    
    def load_readers(self):
        """Загрузка списка читателей"""
        try:
            readers = ReaderManager.get_all_readers()
            self.display_readers(readers)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки читателей:\n{str(e)}')
            logger.error(f"Ошибка загрузки читателей: {e}")
    
    def load_loans(self):
        """Загрузка активных выдач"""
        try:
            filter_type = self.loans_filter_combo.currentData()
            
            if filter_type == 'overdue':
                loans = LoanManager.get_overdue_loans()
            elif filter_type == 'today':
                loans = LoanManager.get_loans_due_today()
            else:
                loans = LoanManager.get_active_loans()
            
            self.display_loans(loans)
            
            # Обновление статистики
            all_loans = LoanManager.get_active_loans()
            overdue_loans = LoanManager.get_overdue_loans()
            
            self.loans_count_label.setText(f'Всего: {len(all_loans)}')
            self.overdue_count_label.setText(f'Просрочено: {len(overdue_loans)}')
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки выдач:\n{str(e)}')
            logger.error(f"Ошибка загрузки выдач: {e}")
    
    def load_history(self):
        """Загрузка истории"""
        try:
            history = LoanManager.get_loan_history()
            self.display_history(history)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки истории:\n{str(e)}')
            logger.error(f"Ошибка загрузки истории: {e}")
    
    # ========== ОТОБРАЖЕНИЕ ДАННЫХ ==========
    
    def display_books(self, books):
        """Отображение книг в таблице"""
        self.books_table.setRowCount(0)
        
        for book in books:
            row = self.books_table.rowCount()
            self.books_table.insertRow(row)
            
            self.books_table.setItem(row, 0, QTableWidgetItem(str(book.id)))
            self.books_table.setItem(row, 1, QTableWidgetItem(book.title))
            self.books_table.setItem(row, 2, QTableWidgetItem(book.author))
            self.books_table.setItem(row, 3, QTableWidgetItem(book.genre.name if book.genre else '-'))
            self.books_table.setItem(row, 4, QTableWidgetItem(str(book.year) if book.year else '-'))
            self.books_table.setItem(row, 5, QTableWidgetItem(str(book.quantity)))
            
            # Доступное количество с цветовой индикацией
            available_item = QTableWidgetItem(str(book.available_quantity))
            if book.available_quantity == 0:
                available_item.setForeground(Qt.red)
            elif book.available_quantity <= 2:
                available_item.setForeground(Qt.darkYellow)
            else:
                available_item.setForeground(Qt.darkGreen)
            self.books_table.setItem(row, 6, available_item)
    
    def display_readers(self, readers):
        """Отображение читателей в таблице"""
        self.readers_table.setRowCount(0)
        
        for reader in readers:
            row = self.readers_table.rowCount()
            self.readers_table.insertRow(row)
            
            self.readers_table.setItem(row, 0, QTableWidgetItem(str(reader.id)))
            self.readers_table.setItem(row, 1, QTableWidgetItem(reader.get_full_name()))
            self.readers_table.setItem(row, 2, QTableWidgetItem(
                reader.birth_date.strftime('%d.%m.%Y') if reader.birth_date else '-'
            ))
            self.readers_table.setItem(row, 3, QTableWidgetItem(reader.category))
            self.readers_table.setItem(row, 4, QTableWidgetItem(reader.phone or '-'))
            self.readers_table.setItem(row, 5, QTableWidgetItem(reader.card_number))
    
    def display_loans(self, loans):
        """Отображение выдач в таблице"""
        self.loans_table.setRowCount(0)
        
        for loan in loans:
            row = self.loans_table.rowCount()
            self.loans_table.insertRow(row)
            
            self.loans_table.setItem(row, 0, QTableWidgetItem(str(loan.id)))
            self.loans_table.setItem(row, 1, QTableWidgetItem(loan.reader.get_full_name()))
            self.loans_table.setItem(row, 2, QTableWidgetItem(loan.book.title))
            self.loans_table.setItem(row, 3, QTableWidgetItem(loan.book.author))
            self.loans_table.setItem(row, 4, QTableWidgetItem(loan.loan_date.strftime('%d.%m.%Y')))
            self.loans_table.setItem(row, 5, QTableWidgetItem(loan.due_date.strftime('%d.%m.%Y')))
            
            # Просрочка
            overdue_days = loan.get_overdue_days()
            if overdue_days > 0:
                overdue_item = QTableWidgetItem(f'{overdue_days} дн.')
                overdue_item.setForeground(Qt.white)
                overdue_item.setBackground(Qt.red)
                self.loans_table.setItem(row, 6, overdue_item)
            else:
                self.loans_table.setItem(row, 6, QTableWidgetItem('-'))
    
    def display_history(self, history):
        """Отображение истории в таблице"""
        self.history_table.setRowCount(0)
        
        for loan in history[:100]:  # Показываем последние 100 записей
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(str(loan.id)))
            self.history_table.setItem(row, 1, QTableWidgetItem(loan.reader.get_full_name()))
            self.history_table.setItem(row, 2, QTableWidgetItem(loan.book.title))
            self.history_table.setItem(row, 3, QTableWidgetItem(loan.book.author))
            self.history_table.setItem(row, 4, QTableWidgetItem(loan.loan_date.strftime('%d.%m.%Y')))
            self.history_table.setItem(row, 5, QTableWidgetItem(loan.due_date.strftime('%d.%m.%Y')))
            
            if loan.return_date:
                self.history_table.setItem(row, 6, QTableWidgetItem(loan.return_date.strftime('%d.%m.%Y')))
                
                # Статус
                if loan.get_overdue_days() > 0:
                    status_item = QTableWidgetItem('Просрочено')
                    status_item.setForeground(Qt.red)
                else:
                    status_item = QTableWidgetItem('Вовремя')
                    status_item.setForeground(Qt.darkGreen)
                self.history_table.setItem(row, 7, status_item)
            else:
                self.history_table.setItem(row, 6, QTableWidgetItem('-'))
                self.history_table.setItem(row, 7, QTableWidgetItem('Активна'))
    
    # ========== ДЕЙСТВИЯ ==========
    
    def add_book(self):
        """Добавление книги"""
        dialog = AddBookDialog(self)
        if dialog.exec_():
            self.load_books()
            self.status_bar.showMessage('Книга добавлена', 3000)
    
    def add_reader(self):
        """Добавление читателя"""
        dialog = AddReaderDialog(self)
        if dialog.exec_():
            self.load_readers()
            self.status_bar.showMessage('Читатель зарегистрирован', 3000)
    
    def create_loan(self):
        """Создание выдачи"""
        dialog = LoanDialog(self)
        if dialog.exec_():
            self.load_loans()
            self.load_books()
            self.status_bar.showMessage('Книга выдана', 3000)
    
    def return_book(self):
        """Возврат книги"""
        dialog = ReturnDialog(self)
        if dialog.exec_():
            self.load_loans()
            self.load_books()
            self.load_history()
            self.status_bar.showMessage('Книга возвращена', 3000)
    
    def search_books(self):
        """Поиск книг"""
        search_text = self.books_search_input.text().strip()
        if not search_text:
            self.load_books()
            return
        
        try:
            books = BookManager.search_books(search_text)
            self.display_books(books)
            self.status_bar.showMessage(f'Найдено книг: {len(books)}', 3000)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка поиска:\n{str(e)}')
    
    def search_readers(self):
        """Поиск читателей"""
        search_text = self.readers_search_input.text().strip()
        if not search_text:
            self.load_readers()
            return
        
        try:
            readers = ReaderManager.search_readers(search_text)
            self.display_readers(readers)
            self.status_bar.showMessage(f'Найдено читателей: {len(readers)}', 3000)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка поиска:\n{str(e)}')
    
    def edit_book(self):
        """Редактирование книги"""
        selected_items = self.books_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Внимание', 'Выберите книгу для редактирования!')
            return
        
        row = selected_items[0].row()
        book_id = int(self.books_table.item(row, 0).text())
        
        # TODO: Создать диалог редактирования книги
        QMessageBox.information(self, 'Информация', 
                              f'Редактирование книги с ID {book_id} будет реализовано')
    
    def delete_book(self):
        """Удаление книги"""
        selected_items = self.books_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Внимание', 'Выберите книгу для удаления!')
            return
        
        row = selected_items[0].row()
        book_id = int(self.books_table.item(row, 0).text())
        book_title = self.books_table.item(row, 1).text()
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы уверены, что хотите удалить книгу "{book_title}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                BookManager.delete_book(book_id)
                self.load_books()
                self.status_bar.showMessage('Книга удалена', 3000)
                logger.info(f"Книга удалена: {book_title} (ID: {book_id})")
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка удаления книги:\n{str(e)}')
                logger.error(f"Ошибка удаления книги: {e}")
    
    def view_reader(self):
        """Просмотр информации о читателе"""
        selected_items = self.readers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Внимание', 'Выберите читателя!')
            return
        
        row = selected_items[0].row()
        reader_id = int(self.readers_table.item(row, 0).text())
        
        try:
            reader = ReaderManager.get_reader_by_id(reader_id)
            
            # Формирование информации
            info = f"""
<h3>Информация о читателе</h3>
<p><b>ФИО:</b> {reader.get_full_name()}</p>
<p><b>Дата рождения:</b> {reader.birth_date.strftime('%d.%m.%Y') if reader.birth_date else '-'}</p>
<p><b>Категория:</b> {reader.category}</p>
<p><b>Телефон:</b> {reader.phone or '-'}</p>
<p><b>Email:</b> {reader.email or '-'}</p>
<p><b>Адрес:</b> {reader.address or '-'}</p>
<p><b>Читательский билет:</b> {reader.card_number}</p>
<p><b>Дата регистрации:</b> {reader.registration_date.strftime('%d.%m.%Y')}</p>
            """
            
            msg = QMessageBox(self)
            msg.setWindowTitle('Информация о читателе')
            msg.setTextFormat(Qt.RichText)
            msg.setText(info)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка получения данных:\n{str(e)}')
    
    def edit_reader(self):
        """Редактирование читателя"""
        selected_items = self.readers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Внимание', 'Выберите читателя для редактирования!')
            return
        
        row = selected_items[0].row()
        reader_id = int(self.readers_table.item(row, 0).text())
        
        # TODO: Создать диалог редактирования читателя
        QMessageBox.information(self, 'Информация', 
                              f'Редактирование читателя с ID {reader_id} будет реализовано')
    
    def refresh_all_data(self):
        """Обновление всех данных"""
        self.load_initial_data()
        self.status_bar.showMessage('Данные обновлены', 3000)
        logger.info("Выполнено обновление всех данных")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        <h2>Система управления библиотекой</h2>
        <p><b>Версия:</b> 1.0.0</p>
        <p><b>Описание:</b> Программа для автоматизации работы библиотеки</p>
        <br>
        <p><b>Функции:</b></p>
        <ul>
            <li>Управление книжным фондом</li>
            <li>Регистрация читателей</li>
            <li>Выдача и возврат книг</li>
            <li>Учет просрочек и штрафов</li>
            <li>История операций</li>
        </ul>
        <br>
        <p><b>Технологии:</b> Python, PyQt5, SQLAlchemy</p>
        <p>© 2024 Библиотечная система</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle('О программе')
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите выйти из программы?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info(f"Пользователь {self.current_user['username']} вышел из системы")
            event.accept()
        else:
            event.ignore()