from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                              QPushButton, QMessageBox)
from pathlib import Path
import openpyxl
from openpyxl.styles import Font
from datetime import datetime

class ReportDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Rapor Oluştur")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Başlık seçimi
        self.title_combo = QComboBox()
        self.title_combo.addItem("Tümü", None)
        self.refresh_titles()
        form.addRow("Başlık:", self.title_combo)

        # Kasa sahibi seçimi
        self.cash_owner_combo = QComboBox()
        self.cash_owner_combo.addItem("Tümü", None)
        self.refresh_cash_owners()
        form.addRow("Kasa Sahibi:", self.cash_owner_combo)

        layout.addLayout(form)

        # Rapor oluştur butonu
        btn_create = QPushButton("Excel Raporu Oluştur")
        btn_create.clicked.connect(self.create_report)
        layout.addWidget(btn_create)

    def refresh_titles(self):
        titles = self.database.get_titles()
        for title in titles:
            self.title_combo.addItem(title['name'], title['id'])

    def refresh_cash_owners(self):
        cash_owners = self.database.get_cash_owners()
        for owner in cash_owners:
            self.cash_owner_combo.addItem(owner['name'], owner['id'])

    def create_report(self):
        filters = {}
        
        if self.title_combo.currentData():
            filters['title_id'] = self.title_combo.currentData()
        
        if self.cash_owner_combo.currentData():
            filters['cash_owner_id'] = self.cash_owner_combo.currentData()

        transactions = self.database.get_transactions(filters)
        
        if not transactions:
            QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere uygun kayıt bulunamadı!")
            return

        # Excel dosyası oluştur
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Muhasebe Raporu"

        # Başlıkları ekle
        headers = ["Tarih", "Başlık", "Kasa Sahibi", "Firma", "Açıklama",
                  "Yapılan Ödeme", "Alınan Ödeme", "Alınan Çek", "Verilen Çek",
                  "Daire Satış", "Fatura Tutarı", "Miktar", "Birim Fiyat",
                  "Toplam Tutar"]

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)

        # Verileri ekle
        for row, trans in enumerate(transactions, 2):
            ws.cell(row=row, column=1).value = trans['date']
            ws.cell(row=row, column=2).value = trans['title_name']
            ws.cell(row=row, column=3).value = trans['cash_owner_name']
            ws.cell(row=row, column=4).value = trans['company_name']
            ws.cell(row=row, column=5).value = trans['description']
            ws.cell(row=row, column=6).value = trans['expense']
            ws.cell(row=row, column=7).value = trans['payment_received']
            ws.cell(row=row, column=8).value = trans['check_received']
            ws.cell(row=row, column=9).value = trans['check_given']
            ws.cell(row=row, column=10).value = trans['apartment_sale']
            ws.cell(row=row, column=11).value = trans['invoice_amount']
            ws.cell(row=row, column=12).value = trans['quantity']
            ws.cell(row=row, column=13).value = trans['unit_price']
            ws.cell(row=row, column=14).value = f"=L{row}*M{row}"  # Toplam Tutar formülü

        # Sütun genişliklerini ayarla
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

        # Masaüstüne kaydet
        desktop_path = str(Path.home() / "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"{desktop_path}/muhasebe_raporu_{timestamp}.xlsx"
        
        wb.save(excel_path)
        QMessageBox.information(self, "Başarılı", f"Rapor başarıyla oluşturuldu:\n{excel_path}") 