import sys
from PySide6.QtWidgets import QApplication
from database import Database
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Veritabanı bağlantısını oluştur
    db = Database()
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow(db)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 