from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                              QLineEdit, QDateEdit, QPushButton, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate

class TransactionDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Yeni İşlem")
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

        self.description_edit = QLineEdit()
        form.addRow("Açıklama:", self.description_edit)

        self.expense_edit = QLineEdit()
        form.addRow("Harcama:", self.expense_edit)

        self.payment_received_edit = QLineEdit()
        form.addRow("Alınan Ödeme:", self.payment_received_edit)

        self.check_received_edit = QLineEdit()
        form.addRow("Alınan Çek:", self.check_received_edit)

        self.check_given_edit = QLineEdit()
        form.addRow("Verilen Çek:", self.check_given_edit)

        layout.addLayout(form)

        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        data = {
            'title_id': self.title_combo.currentData(),
            'cash_owner_id': self.cash_owner_combo.currentData(),
            'date': self.date_edit.date().toString(Qt.ISODate),
            'company_name': self.company_edit.text(),
            'construction_group_id': None,  # Bu alanı daha sonra ekleyeceğiz
            'description': self.description_edit.text(),
            'expense': float(self.expense_edit.text() or 0),
            'payment_received': float(self.payment_received_edit.text() or 0),
            'check_received': float(self.check_received_edit.text() or 0),
            'check_given': float(self.check_given_edit.text() or 0),
            'apartment_sale': 0,  # Bu alanı daha sonra ekleyeceğiz
            'invoice_amount': 0,  # Bu alanı daha sonra ekleyeceğiz
            'quantity': 0,  # Bu alanı daha sonra ekleyeceğiz
            'unit_price': 0  # Bu alanı daha sonra ekleyeceğiz
        }
        
        self.database.add_transaction(data)
        super().accept() 