
# printer_manager.py
import os
import sys
import tempfile
import win32print
import win32api
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QCheckBox, QLabel, QPushButton,
                               QFileDialog, QLineEdit, QSpinBox, QListWidget,
                               QGroupBox, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QDateTime
from printer_config import PrinterConfig
from printer_panel import PrinterPanel

def read_printers_from_file(file_path: str) -> list:
    printers = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            printers = [line.strip() for line in f.readlines() if line.strip()]
    return printers

class PrinterManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.printer_config = PrinterConfig()
        self.config = self.printer_config.get_config()
        self.printer_panels = {}
        self.temp_dir = tempfile.mkdtemp()
        self.default_printer = win32print.GetDefaultPrinter()

        self.gs_path = self._find_ghostscript()
        if not self.gs_path:
            QMessageBox.warning(self, "警告", "未找到 Ghostscript，请确保正确安装了 Ghostscript 10.04.0")

        self._init_ui()

    def _find_ghostscript(self):
        possible_paths = [
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",  # 64位版本
            r"C:\Program Files (x86)\gs\gs10.04.0\bin\gswin32c.exe",  # 32位版本
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64.exe",
            r"C:\Program Files (x86)\gs\gs10.04.0\bin\gswin32.exe"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        try:
            result = subprocess.run(['where', 'gswin64c.exe'], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            try:
                result = subprocess.run(['where', 'gswin32c.exe'], capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except:
                pass

        return None

    def __del__(self):
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def _init_ui(self):
        self.setWindowTitle('打印管理系统')
        self.setGeometry(100, 100, 500, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 读取打印机列表
        printers = read_printers_from_file("print_set.txt")
        for printer in printers:
            self.create_printer_panel(printer)

    def create_printer_panel(self, printer_name: str):
        panel = PrinterPanel(printer_name, self, self.printer_config, self)
        self.printer_panels[printer_name] = panel
        self.centralWidget().layout().addWidget(panel.panel)
