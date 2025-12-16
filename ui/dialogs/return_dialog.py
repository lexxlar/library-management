from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QTextEdit, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from business.managers.loan_manager import LoanManager
from datetime import datetime

class ReturnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_loan_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Возврат книги')
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel('Возврат книги в библиотеку')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; padding: 10px;')
        layout.addWidget(title_label)
        
        # Поиск активных выдач
        search_layout = QHBoxLayout()
        search_label = QLabel('Поиск:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Введите фамилию читателя, название книги или номер билета')
        self.search_button = QPushButton('Найти активные выдачи')
        self.search_button.setStyleSheet('background-color: #2196F3; color: white; padding: 8px 15px;')
        self.search_button.clicked.connect(self.search_active_loans)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Таблица активных выдач
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(7)
        self.loans_table.setHorizontalHeaderLabels([
            'ID', 'Читатель', 'Книга', 'Автор', 'Дата выдачи', 
            'Дата возврата', 'Просрочка'
        ])
        self.loans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.loans_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.loans_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.loans_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.loans_table.itemSelectionChanged.connect(self.on_loan_selected)
        layout.addWidget(self.loans_table)
        
        # Информация о выбранной выдаче
        info_label = QLabel('Информация о выдаче')
        info_label.setStyleSheet('font-size: 14px; font-weight: bold; margin-top: 10px;')
        layout.addWidget(info_label)
        
        self.loan_info_label = QLabel('Выберите выдачу из списка')
        self.loan_info_label.setStyleSheet('padding: 10px; background-color: #f5f5f5; border-radius: 5px;')
        self.loan_info_label.setWordWrap(True)
        layout.addWidget(self.loan_info_label)
        
        # Форма возврата
        form_layout = QFormLayout()
        
        # Состояние книги
        self.condition_input = QTextEdit()
        self.condition_input.setMaximumHeight(60)
        self.condition_input.setPlaceholderText('Опишите состояние книги (опционально)')
        form_layout.addRow('Состояние книги:', self.condition_input)
        
        # Штраф (если есть просрочка)
        self.fine_input = QSpinBox()
        self.fine_input.setRange(0, 100000)
        self.fine_input.setValue(0)
        self.fine_input.setSuffix(' руб.')
        self.fine_input.setEnabled(False)
        form_layout.addRow('Штраф:', self.fine_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.return_button = QPushButton('Оформить возврат')
        self.return_button.setStyleSheet('''
            background-color: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            font-weight: bold;
            font-size: 13px;
        ''')
        self.return_button.clicked.connect(self.process_return)
        self.return_button.setEnabled(False)
        
        cancel_button = QPushButton('Отмена')
        cancel_button.setStyleSheet('background-color: #f44336; color: white; padding: 10px 20px;')
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.return_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Загрузка всех активных выдач при открытии
        self.load_all_active_loans()
    
    def load_all_active_loans(self):
        """Загрузка всех активных выдач"""
        try:
            loans = LoanManager.get_active_loans()
            self.display_loans(loans)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки данных:\n{str(e)}')
    
    def search_active_loans(self):
        """Поиск активных выдач"""
        search_text = self.search_input.text().strip()
        
        try:
            if search_text:
                loans = LoanManager.search_active_loans(search_text)
            else:
                loans = LoanManager.get_active_loans()
            
            if not loans:
                QMessageBox.information(self, 'Результат', 'Активные выдачи не найдены')
                self.loans_table.setRowCount(0)
                return
            
            self.display_loans(loans)
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка поиска:\n{str(e)}')
    
    def display_loans(self, loans):
        """Отображение выдач в таблице"""
        self.loans_table.setRowCount(0)
        
        for loan in loans:
            row = self.loans_table.rowCount()
            self.loans_table.insertRow(row)
            
            # ID выдачи
            self.loans_table.setItem(row, 0, QTableWidgetItem(str(loan.id)))
            
            # Читатель
            reader_name = loan.reader.get_full_name()
            self.loans_table.setItem(row, 1, QTableWidgetItem(reader_name))
            
            # Книга
            self.loans_table.setItem(row, 2, QTableWidgetItem(loan.book.title))
            
            # Автор
            self.loans_table.setItem(row, 3, QTableWidgetItem(loan.book.author))
            
            # Дата выдачи
            loan_date = loan.loan_date.strftime('%d.%m.%Y')
            self.loans_table.setItem(row, 4, QTableWidgetItem(loan_date))
            
            # Дата возврата
            due_date = loan.due_date.strftime('%d.%m.%Y')
            self.loans_table.setItem(row, 5, QTableWidgetItem(due_date))
            
            # Просрочка
            overdue_days = loan.get_overdue_days()
            if overdue_days > 0:
                overdue_item = QTableWidgetItem(f'{overdue_days} дн.')
                overdue_item.setForeground(Qt.red)
                overdue_item.setBackground(Qt.yellow)
                self.loans_table.setItem(row, 6, overdue_item)
            else:
                self.loans_table.setItem(row, 6, QTableWidgetItem('-'))
    
    def on_loan_selected(self):
        """Обработка выбора выдачи"""
        selected_items = self.loans_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        self.selected_loan_id = int(self.loans_table.item(row, 0).text())
        
        # Получение подробной информации о выдаче
        try:
            loan = LoanManager.get_loan_by_id(self.selected_loan_id)
            
            # Формирование информации
            info_text = f"""
<b>Читатель:</b> {loan.reader.get_full_name()}<br>
<b>Читательский билет:</b> {loan.reader.card_number}<br>
<b>Книга:</b> "{loan.book.title}"<br>
<b>Автор:</b> {loan.book.author}<br>
<b>Дата выдачи:</b> {loan.loan_date.strftime('%d.%m.%Y')}<br>
<b>Дата возврата:</b> {loan.due_date.strftime('%d.%m.%Y')}<br>
            """
            
            # Проверка просрочки
            overdue_days = loan.get_overdue_days()
            if overdue_days > 0:
                info_text += f'<br><b style="color: red;">ПРОСРОЧКА: {overdue_days} дней</b>'
                # Автоматический расчет штрафа (например, 10 руб/день)
                fine = overdue_days * 10
                self.fine_input.setValue(fine)
                self.fine_input.setEnabled(True)
            else:
                info_text += '<br><b style="color: green;">Книга возвращается вовремя</b>'
                self.fine_input.setValue(0)
                self.fine_input.setEnabled(False)
            
            self.loan_info_label.setText(info_text)
            self.return_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка получения данных:\n{str(e)}')
    
    def process_return(self):
        """Обработка возврата книги"""
        if not self.selected_loan_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите выдачу для возврата!')
            return
        
        # Подтверждение
        reply = QMessageBox.question(
            self, 
            'Подтверждение', 
            'Оформить возврат книги?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            condition_notes = self.condition_input.toPlainText().strip() or None
            fine_amount = self.fine_input.value() if self.fine_input.isEnabled() else 0
            
            LoanManager.return_book(
                loan_id=self.selected_loan_id,
                condition_notes=condition_notes,
                fine_amount=fine_amount
            )
            
            success_msg = 'Книга успешно возвращена!'
            if fine_amount > 0:
                success_msg += f'\n\nНачислен штраф: {fine_amount} руб.'
            
            QMessageBox.information(self, 'Успех', success_msg)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка возврата книги:\n{str(e)}')