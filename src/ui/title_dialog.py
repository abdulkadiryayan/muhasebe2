from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                              QLineEdit, QDialogButtonBox)

class TitleDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Yeni Başlık/Kasa Sahibi")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        form.addRow("Başlık Adı:", self.title_edit)

        self.cash_owner_edit = QLineEdit()
        form.addRow("Kasa Sahibi Adı:", self.cash_owner_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        title_name = self.title_edit.text()
        cash_owner_name = self.cash_owner_edit.text()

        if title_name:
            self.database.add_title(title_name)
        if cash_owner_name:
            self.database.add_cash_owner(cash_owner_name)

        super().accept() 