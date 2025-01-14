from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog, QMenu, QMessageBox,
                              QLabel, QDateEdit, QComboBox, QFrame)
from PySide6.QtCore import Qt, QPoint, QDate
from .transaction_dialog import TransactionDialog
from .title_dialog import TitleDialog
from .report_dialog import ReportDialog

class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()
        self.setup_context_menu()

    def setup_ui(self):
        self.setWindowTitle("Muhasebe Programı")
        self.setMinimumSize(1200, 800)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst butonlar için yatay düzen
        button_layout = QHBoxLayout()
        
        # Sol taraftaki butonlar
        btn_new_transaction = QPushButton("Yeni İşlem")
        btn_new_transaction.clicked.connect(self.show_transaction_dialog)
        button_layout.addWidget(btn_new_transaction)

        btn_new_title = QPushButton("Yeni Başlık")
        btn_new_title.clicked.connect(self.show_title_dialog)
        button_layout.addWidget(btn_new_title)

        btn_report = QPushButton("Raporla")
        btn_report.clicked.connect(self.show_report_dialog)
        button_layout.addWidget(btn_report)
        
        button_layout.addStretch()  # Sağ ve sol butonlar arasında boşluk
        layout.addLayout(button_layout)

        # Filtreleme paneli
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        filter_layout = QHBoxLayout(filter_frame)

        # Tarih aralığı
        filter_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Varsayılan olarak 1 ay öncesi
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("Bitiş Tarihi:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)

        # Başlık filtresi
        filter_layout.addWidget(QLabel("Başlık:"))
        self.filter_title = QComboBox()
        self.filter_title.addItem("Tümü", None)
        self.refresh_filter_titles()
        filter_layout.addWidget(self.filter_title)

        # Kasa sahibi filtresi
        filter_layout.addWidget(QLabel("Kasa Sahibi:"))
        self.filter_cash_owner = QComboBox()
        self.filter_cash_owner.addItem("Tümü", None)
        self.refresh_filter_cash_owners()
        filter_layout.addWidget(self.filter_cash_owner)

        # Filtreleme butonu
        btn_filter = QPushButton("Filtrele")
        btn_filter.clicked.connect(self.apply_filters)
        filter_layout.addWidget(btn_filter)

        # Filtreleri temizle butonu
        btn_clear_filters = QPushButton("Filtreleri Temizle")
        btn_clear_filters.clicked.connect(self.clear_filters)
        filter_layout.addWidget(btn_clear_filters)

        layout.addWidget(filter_frame)

        # Tablo
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)

    def refresh_filter_titles(self):
        self.filter_title.clear()
        self.filter_title.addItem("Tümü", None)
        titles = self.database.get_titles()
        for title in titles:
            self.filter_title.addItem(title['name'], title['id'])

    def refresh_filter_cash_owners(self):
        self.filter_cash_owner.clear()
        self.filter_cash_owner.addItem("Tümü", None)
        cash_owners = self.database.get_cash_owners()
        for owner in cash_owners:
            self.filter_cash_owner.addItem(owner['name'], owner['id'])

    def apply_filters(self):
        filters = {}
        
        # Tarih aralığı filtresi
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)
        filters['date_range'] = (start_date, end_date)

        # Başlık filtresi
        if self.filter_title.currentData():
            filters['title_id'] = self.filter_title.currentData()

        # Kasa sahibi filtresi
        if self.filter_cash_owner.currentData():
            filters['cash_owner_id'] = self.filter_cash_owner.currentData()

        self.refresh_table(filters)

    def clear_filters(self):
        # Tarih seçicileri temizle
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate())
        
        # Comboboxları sıfırla
        self.filter_title.setCurrentIndex(0)
        self.filter_cash_owner.setCurrentIndex(0)
        
        # Tabloyu yenile (tüm işlemleri göster)
        self.refresh_table({})

    def refresh_table(self, filters=None):
        self.table.setRowCount(0)
        # Eğer filtre yoksa tüm işlemleri göster
        if filters is None:
            filters = {}
        transactions = self.database.get_transactions(filters)
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # İlk hücrede transaction ID'sini sakla
            date_item = QTableWidgetItem(trans['date'])
            date_item.setData(Qt.UserRole, trans['id'])
            self.table.setItem(row, 0, date_item)

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
            
            # Toplam Tutar hesaplama ve ekleme
            total = trans['quantity'] * trans['unit_price']
            self.table.setItem(row, 13, QTableWidgetItem(str(total)))

    def show_transaction_dialog(self):
        dialog = TransactionDialog(self.database)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def show_title_dialog(self):
        dialog = TitleDialog(self.database)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def show_report_dialog(self):
        dialog = ReportDialog(self.database)
        dialog.exec()

    def setup_context_menu(self):
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos: QPoint):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("Düzenle")
        delete_action = menu.addAction("Sil")

        # Menüyü göster ve seçilen aksiyonu al
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == edit_action:
            self.edit_transaction(row)
        elif action == delete_action:
            self.delete_transaction(row)

    def edit_transaction(self, row):
        transaction_id = self.table.item(row, 0).data(Qt.UserRole)  # ID'yi UserRole'da saklayacağız
        dialog = TransactionDialog(self.database, transaction_id)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def delete_transaction(self, row):
        transaction_id = self.table.item(row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(
            self, 'İşlemi Sil',
            'Bu işlemi silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.database.delete_transaction(transaction_id)
            self.refresh_table() 

    def setup_table(self):
        headers = ["Tarih", "Başlık", "Kasa Sahibi", "Firma", "Açıklama",
                  "Yapılan Ödeme", "Alınan Ödeme", "Alınan Çek", "Verilen Çek",
                  "Daire Satış", "Fatura Tutarı", "Miktar", "Birim Fiyat",
                  "Toplam Tutar"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Sütun genişliklerini ayarla
        self.table.horizontalHeader().setStretchLastSection(True)
        for i in range(len(headers)):
            self.table.setColumnWidth(i, 120)  # Her sütuna 120 piksel genişlik
        
        # Başlangıç verilerini yükle
        self.refresh_table() 