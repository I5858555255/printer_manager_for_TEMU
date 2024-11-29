# main.py
import sys
from PySide6.QtWidgets import QApplication
from printer_manager import PrinterManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = PrinterManager()
    manager.show()
    sys.exit(app.exec())
