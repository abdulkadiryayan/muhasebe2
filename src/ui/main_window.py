from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog)
from PySide6.QtCore import Qt
from .transaction_dialog import TransactionDialog
from .title_dialog import TitleDialog

class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Muhasebe Programı")
        self.setMinimumSize(1200, 800)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Butonlar
        btn_new_transaction = QPushButton("Yeni İşlem")
        btn_new_transaction.clicked.connect(self.show_transaction_dialog)
        layout.addWidget(btn_new_transaction)

        btn_new_title = QPushButton("Yeni Başlık")
        btn_new_title.clicked.connect(self.show_title_dialog)
        layout.addWidget(btn_new_title)

        # Tablo
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)

    def setup_table(self):
        headers = ["Tarih", "Başlık", "Kasa Sahibi", "Firma", "Açıklama",
                  "Harcama", "Alınan Ödeme", "Alınan Çek", "Verilen Çek",
                  "Daire Satış", "Fatura Tutarı", "Miktar", "Birim Fiyat"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        transactions = self.database.get_transactions()
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(trans['date']))
            self.table.setItem(row, 1, QTableWidgetItem(trans['title_name']))
            self.table.setItem(row, 2, QTableWidgetItem(trans['cash_owner_name']))
            self.table.setItem(row, 3, QTableWidgetItem(trans['company_name']))
            self.table.setItem(row, 4, QTableWidgetItem(trans['description']))
            self.table.setItem(row, 5, QTableWidgetItem(str(trans['expense'])))
            self.table.setItem(row, 6, QTableWidgetItem(str(trans['payment_received'])))
            self.table.setItem(row, 7, QTableWidgetItem(str(trans['check_received'])))
            self.table.setItem(row, 8, QTableWidgetItem(str(trans['check_given'])))
            self.table.setItem(row, 9, QTableWidgetItem(str(trans['apartment_sale'])))
            self.table.setItem(row, 10, QTableWidgetItem(str(trans['invoice_amount'])))
            self.table.setItem(row, 11, QTableWidgetItem(str(trans['quantity'])))
            self.table.setItem(row, 12, QTableWidgetItem(str(trans['unit_price'])))

    def show_transaction_dialog(self):
        dialog = TransactionDialog(self.database)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def show_title_dialog(self):
        dialog = TitleDialog(self.database)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table() 