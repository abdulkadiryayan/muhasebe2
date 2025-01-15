from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                              QPushButton, QDialogButtonBox, QMessageBox)

class TitleDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Yeni Başlık")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        form.addRow("Başlık:", self.title_edit)

        self.cash_owner_edit = QLineEdit()
        form.addRow("Kasa Sahibi:", self.cash_owner_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        title = self.title_edit.text().strip()
        cash_owner = self.cash_owner_edit.text().strip()

        if not title and not cash_owner:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir alan doldurun!")
            return

        try:
            if title:
                self.database.add_title(title)
            if cash_owner:
                self.database.add_cash_owner(cash_owner)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e)) 