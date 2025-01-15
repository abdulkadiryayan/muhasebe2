from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog, QMenu, QMessageBox,
                              QLabel, QDateEdit, QComboBox, QFrame, QHeaderView)
from PySide6.QtCore import Qt, QPoint, QDate
from PySide6.QtGui import QFont, QColor, QPalette
from .transaction_dialog import TransactionDialog
from .title_dialog import TitleDialog
from .report_dialog import ReportDialog

class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()
        self.database = database
        
        # Filtreleme widget'larını başlangıçta oluştur
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        
        # Tarih seçicileri için ayarlar
        for date_edit in [self.start_date, self.end_date]:
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("dd.MM.yyyy")
            date_edit.setDate(QDate.currentDate())
        
        self.filter_title = QComboBox()
        self.filter_cash_owner = QComboBox()
        
        # Filtreleme combobox'larını doldur
        self.refresh_filter_titles()
        self.refresh_filter_cash_owners()
        
        self.setup_styles()  # Stil ayarlarını uygula
        self.setup_ui()
        self.setup_context_menu()
        
        # Başlangıçta tüm verileri göster
        self.refresh_table()

    def setup_ui(self):
        self.setWindowTitle("Muhasebe Programı")
        self.setMinimumSize(1400, 800)

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst butonlar paneli
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # Ana butonlar
        btn_new_transaction = QPushButton("Yeni İşlem")
        btn_new_title = QPushButton("Yeni Başlık")
        btn_report = QPushButton("Raporla")

        for btn in [btn_new_transaction, btn_new_title, btn_report]:
            button_layout.addWidget(btn)
            btn.setMinimumHeight(35)

        btn_new_transaction.clicked.connect(self.show_transaction_dialog)
        btn_new_title.clicked.connect(self.show_title_dialog)
        btn_report.clicked.connect(self.show_report_dialog)
        
        button_layout.addStretch()
        layout.addWidget(button_frame)

        # Filtreleme paneli
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(10)

        # Tarih filtreleri
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)

        # Tarih seçicileri için etiketler ve widget'lar
        for label_text, date_edit in [
            ("Başlangıç Tarihi:", self.start_date),
            ("Bitiş Tarihi:", self.end_date)
        ]:
            label = QLabel(label_text)
            label.setMinimumWidth(100)
            date_layout.addWidget(label)
            date_layout.addWidget(date_edit)

        filter_layout.addWidget(date_widget)

        # Başlık ve kasa sahibi filtreleri
        for label_text, combo in [
            ("Başlık:", self.filter_title),
            ("Kasa Sahibi:", self.filter_cash_owner)
        ]:
            label = QLabel(label_text)
            label.setMinimumWidth(80)
            filter_layout.addWidget(label)
            filter_layout.addWidget(combo)

        # Filtre butonları
        btn_filter = QPushButton("Filtrele")
        btn_clear_filters = QPushButton("Filtreleri Temizle")
        
        filter_layout.addWidget(btn_filter)
        filter_layout.addWidget(btn_clear_filters)

        btn_filter.clicked.connect(self.apply_filters)
        btn_clear_filters.clicked.connect(self.clear_filters)

        layout.addWidget(filter_frame)

        # Tablo oluşturma ve temel ayarlar
        self.table = QTableWidget()
        
        # Tablo başlıklarını tanımla
        headers = [
            "Tarih", "Başlık", "Kasa Sahibi", "İnşaat Grubu", "Firma", "Açıklama", 
            "Yapılan Ödeme", "Alınan Ödeme", "Alınan Çek", "Verilen Çek", 
            "Daire Satış", "Fatura Tutarı", "Miktar", "Birim Fiyatı", "Toplam Tutar"
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Başlık ve satır numarası ayarları
        header = self.table.horizontalHeader()
        vertical_header = self.table.verticalHeader()

        # Görünürlük ve boyut ayarları
        header.setVisible(True)
        header.setMinimumHeight(40)
        header.setDefaultSectionSize(150)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStretchLastSection(True)

        vertical_header.setVisible(True)
        vertical_header.setMinimumWidth(50)
        vertical_header.setDefaultSectionSize(35)
        vertical_header.setFont(QFont("Arial", 10))

        # Tablo genel ayarları
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Sütun genişlikleri
        column_widths = {
            0: 120,  # Tarih
            1: 300,  # Başlık
            2: 180,  # Kasa Sahibi
            3: 180,  # İnşaat Grubu
            4: 180,  # Firma
            5: 250,  # Açıklama
            6: 150,  # Yapılan Ödeme
            7: 150,  # Alınan Ödeme
            8: 150,  # Alınan Çek
            9: 150,  # Verilen Çek
            10: 150, # Daire Satış
            11: 150, # Fatura Tutarı
            12: 120, # Miktar
            13: 150, # Birim Fiyatı
            14: 150  # Toplam Tutar
        }
        
        for col, width in column_widths.items():
            self.table.setColumnWidth(col, width)

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
        start_date = self.start_date.date().toString("yyyy-MM-dd")  # SQLite formatı
        end_date = self.end_date.date().toString("yyyy-MM-dd")  # SQLite formatı
        filters['date_range'] = (start_date, end_date)

        # Başlık filtresi
        if self.filter_title.currentData():
            filters['title_id'] = self.filter_title.currentData()

        # Kasa sahibi filtresi
        if self.filter_cash_owner.currentData():
            filters['cash_owner_id'] = self.filter_cash_owner.currentData()

        self.refresh_table(filters)

    def clear_filters(self):
        # Tarih seçicileri bugüne ayarla
        current_date = QDate.currentDate()
        self.start_date.setDate(current_date)
        self.end_date.setDate(current_date)
        
        # Comboboxları sıfırla
        self.filter_title.setCurrentIndex(0)
        self.filter_cash_owner.setCurrentIndex(0)
        
        # Tüm verileri göster
        self.refresh_table()

    def refresh_table(self, filters=None):
        self.table.setSortingEnabled(False)  # Sıralamayı geçici olarak devre dışı bırak
        
        if filters is None:
            filters = {}
            
        transactions = self.database.get_transactions(filters)
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # İlk hücrede transaction ID'sini sakla
            date_item = QTableWidgetItem(trans['date'])
            date_item.setData(Qt.UserRole, trans['id'])
            self.table.setItem(row, 0, date_item)

            # Metin içeren hücreler
            text_columns = {
                1: trans['title_name'],
                2: trans['cash_owner_name'],
                3: trans['construction_group_name'],  # İnşaat grubu adı
                4: trans['company_name'],
                5: trans['description']
            }
            
            for col, text in text_columns.items():
                item = QTableWidgetItem(text or '')
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

            # Sayısal değerleri formatlı göster
            numeric_columns = {
                6: trans['expense'],          # Yapılan Ödeme
                7: trans['payment_received'], # Alınan Ödeme
                8: trans['check_received'],   # Alınan Çek
                9: trans['check_given'],      # Verilen Çek
                10: trans['apartment_sale'],   # Daire Satış
                11: trans['invoice_amount'],  # Fatura Tutarı
                12: trans['quantity'],        # Miktar
                13: trans['unit_price'],      # Birim Fiyatı
                14: trans['quantity'] * trans['unit_price'] if trans['quantity'] and trans['unit_price'] else 0  # Toplam Tutar
            }
            
            for col, value in numeric_columns.items():
                item = QTableWidgetItem()
                if value is not None:
                    formatted_value = f"{value:,.2f}"
                    item.setData(Qt.DisplayRole, formatted_value)
                else:
                    item.setData(Qt.DisplayRole, "0.00")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)  # Sıralamayı tekrar etkinleştir

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
        transaction_id = self.table.item(row, 0).data(Qt.UserRole)
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

    def refresh_table(self, filters=None):
        self.table.setSortingEnabled(False)  # Sıralamayı geçici olarak devre dışı bırak
        
        if filters is None:
            filters = {}
            
        transactions = self.database.get_transactions(filters)
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # İlk hücrede transaction ID'sini sakla
            date_item = QTableWidgetItem(trans['date'])
            date_item.setData(Qt.UserRole, trans['id'])
            self.table.setItem(row, 0, date_item)

            # Metin içeren hücreler
            text_columns = {
                1: trans['title_name'],
                2: trans['cash_owner_name'],
                3: trans['construction_group_name'],  # İnşaat grubu adı
                4: trans['company_name'],
                5: trans['description']
            }
            
            for col, text in text_columns.items():
                item = QTableWidgetItem(text or '')
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

            # Sayısal değerleri formatlı göster
            numeric_columns = {
                6: trans['expense'],          # Yapılan Ödeme
                7: trans['payment_received'], # Alınan Ödeme
                8: trans['check_received'],   # Alınan Çek
                9: trans['check_given'],      # Verilen Çek
                10: trans['apartment_sale'],   # Daire Satış
                11: trans['invoice_amount'],  # Fatura Tutarı
                12: trans['quantity'],        # Miktar
                13: trans['unit_price'],      # Birim Fiyatı
                14: trans['quantity'] * trans['unit_price'] if trans['quantity'] and trans['unit_price'] else 0  # Toplam Tutar
            }
            
            for col, value in numeric_columns.items():
                item = QTableWidgetItem()
                if value is not None:
                    formatted_value = f"{value:,.2f}"
                    item.setData(Qt.DisplayRole, formatted_value)
                else:
                    item.setData(Qt.DisplayRole, "0.00")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)  # Sıralamayı tekrar etkinleştir 

    def setup_styles(self):
        # Tüm stilleri kaldır
        self.setStyleSheet("")