from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                              QLineEdit, QDateEdit, QPushButton, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt, QDate

class TransactionDialog(QDialog):
    def __init__(self, database, transaction_id=None):
        super().__init__()
        self.database = database
        self.transaction_id = transaction_id
        self.transaction = None
        if transaction_id:
            self.transaction = database.get_transaction(transaction_id)
        self.setup_ui()

    def load_transaction_data(self):
        if not self.transaction:
            return

        # Başlık ve kasa sahibini seç
        title_index = self.title_combo.findData(self.transaction['title_id'])
        self.title_combo.setCurrentIndex(title_index)

        cash_owner_index = self.cash_owner_combo.findData(self.transaction['cash_owner_id'])
        self.cash_owner_combo.setCurrentIndex(cash_owner_index)

        # Diğer alanları doldur
        self.date_edit.setDate(QDate.fromString(self.transaction['date'], Qt.ISODate))
        self.company_edit.setText(self.transaction['company_name'] or '')
        self.description_edit.setText(self.transaction['description'] or '')
        
        # İnşaat grubu adını yükle - get yerine doğrudan erişim kullan
        construction_group_name = self.transaction['construction_group_name'] if 'construction_group_name' in self.transaction.keys() else ''
        self.construction_group_edit.setText(construction_group_name)
        
        # Sayısal alanları doldur
        self.expense_edit.setText(str(self.transaction['expense'] or ''))
        self.payment_received_edit.setText(str(self.transaction['payment_received'] or ''))
        self.check_received_edit.setText(str(self.transaction['check_received'] or ''))
        self.check_given_edit.setText(str(self.transaction['check_given'] or ''))
        self.apartment_sale_edit.setText(str(self.transaction['apartment_sale'] or ''))
        self.invoice_amount_edit.setText(str(self.transaction['invoice_amount'] or ''))
        self.quantity_edit.setText(str(self.transaction['quantity'] or ''))
        self.unit_price_edit.setText(str(self.transaction['unit_price'] or ''))

    def setup_ui(self):
        self.setWindowTitle("Yeni İşlem" if not self.transaction else "İşlem Düzenle")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Başlık seçimi
        self.title_combo = QComboBox()
        self.refresh_titles()
        form.addRow("Başlık:", self.title_combo)

        # Kasa sahibi seçimi
        self.cash_owner_combo = QComboBox()
        self.refresh_cash_owners()
        form.addRow("Kasa Sahibi:", self.cash_owner_combo)

        # Diğer alanlar
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Tarih:", self.date_edit)

        self.company_edit = QLineEdit()
        form.addRow("Firma:", self.company_edit)

        # İnşaat grubu metin alanı - Firmanın altına taşındı
        self.construction_group_edit = QLineEdit()
        form.addRow("İnşaat Grubu:", self.construction_group_edit)

        self.description_edit = QLineEdit()
        form.addRow("Açıklama:", self.description_edit)

        self.expense_edit = QLineEdit()
        form.addRow("Yapılan Ödeme:", self.expense_edit)

        self.payment_received_edit = QLineEdit()
        form.addRow("Alınan Ödeme:", self.payment_received_edit)

        self.check_received_edit = QLineEdit()
        form.addRow("Alınan Çek:", self.check_received_edit)

        self.check_given_edit = QLineEdit()
        form.addRow("Verilen Çek:", self.check_given_edit)

        self.apartment_sale_edit = QLineEdit()
        form.addRow("Daire Satış:", self.apartment_sale_edit)

        self.invoice_amount_edit = QLineEdit()
        form.addRow("Fatura Tutarı:", self.invoice_amount_edit)

        self.quantity_edit = QLineEdit()
        form.addRow("Miktar:", self.quantity_edit)

        self.unit_price_edit = QLineEdit()
        form.addRow("Birim Fiyatı:", self.unit_price_edit)

        layout.addLayout(form)

        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # UI kurulumu tamamlandıktan sonra verileri yükle
        if self.transaction:
            self.load_transaction_data()

    def refresh_titles(self):
        self.title_combo.clear()
        titles = self.database.get_titles()
        for title in titles:
            self.title_combo.addItem(title['name'], title['id'])

    def refresh_cash_owners(self):
        self.cash_owner_combo.clear()
        cash_owners = self.database.get_cash_owners()
        for owner in cash_owners:
            self.cash_owner_combo.addItem(owner['name'], owner['id'])

    def accept(self):
        try:
            data = {
                'title_id': self.title_combo.currentData(),
                'cash_owner_id': self.cash_owner_combo.currentData(),
                'construction_group': self.construction_group_edit.text(),  # İnşaat grubu adı
                'date': self.date_edit.date().toString(Qt.ISODate),
                'company_name': self.company_edit.text(),
                'description': self.description_edit.text()
            }
            
            # Sayısal değerlerin kontrolü
            numeric_fields = {
                'Yapılan Ödeme': self.expense_edit.text(),
                'Alınan Ödeme': self.payment_received_edit.text(),
                'Alınan Çek': self.check_received_edit.text(),
                'Verilen Çek': self.check_given_edit.text(),
                'Daire Satış': self.apartment_sale_edit.text(),
                'Fatura Tutarı': self.invoice_amount_edit.text(),
                'Miktar': self.quantity_edit.text(),
                'Birim Fiyatı': self.unit_price_edit.text()
            }
            
            # Sayısal alanları kontrol et ve dönüştür
            for field_name, value in numeric_fields.items():
                try:
                    if value.strip() == '':
                        numeric_fields[field_name] = 0
                    else:
                        numeric_fields[field_name] = float(value)
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Hatalı Değer",
                        f"{field_name} alanına geçerli bir sayısal değer giriniz.\n"
                        f"Girilen değer: {value}"
                    )
                    return
            
            # Doğrulanmış sayısal değerleri data sözlüğüne ekle
            data.update({
                'expense': numeric_fields['Yapılan Ödeme'],
                'payment_received': numeric_fields['Alınan Ödeme'],
                'check_received': numeric_fields['Alınan Çek'],
                'check_given': numeric_fields['Verilen Çek'],
                'apartment_sale': numeric_fields['Daire Satış'],
                'invoice_amount': numeric_fields['Fatura Tutarı'],
                'quantity': numeric_fields['Miktar'],
                'unit_price': numeric_fields['Birim Fiyatı']
            })
            
            if self.transaction_id:
                self.database.update_transaction(self.transaction_id, data)
            else:
                self.database.add_transaction(data)
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"İşlem kaydedilirken bir hata oluştu:\n{str(e)}"
            ) 