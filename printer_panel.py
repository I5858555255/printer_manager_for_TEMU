import win32print
import os
import fitz  # PyMuPDF
from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                               QFileDialog, QSpinBox, QListWidget, QLabel, QMessageBox, QWidget)
from PySide6.QtCore import Qt, QDateTime, QEvent
from typing import Optional
from pathlib import Path
import subprocess
from print_logger import log_print_job



from PySide6.QtGui import QDragEnterEvent, QDropEvent

class DragDropLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            if file_path.endswith('.pdf'):
                self.setText(file_path)
                event.acceptProposedAction()



class CustomSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()


class PrinterPanel:
    def __init__(self, printer_name: str, parent_widget: QWidget,
                 printer_config: 'PrinterConfig', parent_manager: 'PrinterManager'):
        self.printer_name = printer_name
        self.parent_widget = parent_widget
        self.printer_config = printer_config
        self.config = printer_config.get_config()
        self.manager = parent_manager
        self.panel = self._create_panel()
        self.is_active = False
        self.current_pdf_size = None

    def _create_panel(self) -> QGroupBox:
        panel = QGroupBox(f"打印机: {self.printer_name}")
        layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.file_path = DragDropLineEdit()  # 使用自定义的 DragDropLineEdit
        self.file_path.setPlaceholderText("请输入SKU")
        self.file_path.returnPressed.connect(self._set_file)
        file_layout.addWidget(self.file_path)
        layout.addLayout(file_layout)

        copies_layout = QHBoxLayout()
        copies_label = QLabel("打印数量:")
        self.copies_spinbox = CustomSpinBox()
        self.copies_spinbox.setMinimum(1)
        self.copies_spinbox.setMaximum(9999)
        self.copies_spinbox.setValue(1)
        self.copies_spinbox.setFocusPolicy(Qt.StrongFocus)
        self.copies_spinbox.keyPressEvent = self._handle_spinbox_key_press
        copies_layout.addWidget(copies_label)
        copies_layout.addWidget(self.copies_spinbox)
        layout.addLayout(copies_layout)

        print_btn = QPushButton("打印")
        print_btn.clicked.connect(self._print_file)
        layout.addWidget(print_btn)

        queue_label = QLabel("打印队列:")
        layout.addWidget(queue_label)
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)

        # 常用打印文件区域
        common_files_label = QLabel("常用打印文件:")
        layout.addWidget(common_files_label)
        self.common_files_list = QListWidget()
        self.common_files_list.itemDoubleClicked.connect(self._print_common_file)
        self._load_common_files()
        layout.addWidget(self.common_files_list)

        panel.setLayout(layout)
        return panel


    def _set_file(self):
        file_name = self.file_path.text().strip()
        if not file_name.endswith('.pdf'):
            file_name += '.pdf'
        folder_path = Path(self.manager.temuskupdf_folder) # Use configured path
        full_path = os.path.join(folder_path, file_name)
        if os.path.exists(full_path):
            self.file_path.setText(full_path)
            self.copies_spinbox.setValue(0)  # 将打印数量清空
            self.copies_spinbox.setFocus()
        else:
            QMessageBox.warning(self.parent_widget, "警告", f"文件不存在: {full_path}")

    def _handle_spinbox_key_press(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._print_file()
        else:
            QSpinBox.keyPressEvent(self.copies_spinbox, event)

    def _print_file(self):
        file_path = self.file_path.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.parent_widget, "警告", "请先选择有效的PDF文件")
            return

        try:
            self.parent_widget.activateWindow()
            self.parent_widget.raise_()

            # 设置打印机
            win32print.SetDefaultPrinter(self.printer_name)

            # 分析 PDF 尺寸
            size = self._analyze_and_update_size(file_path)
            if not size:
                QMessageBox.warning(self.parent_widget, "警告", "无法获取 PDF 尺寸")
                return

            width_cm, height_cm = size
            width_mm = int(width_cm * 10)
            height_mm = int(height_cm * 10)

            # 获取ghostscript路径
            gs_path = self.manager.gs_path
            if not gs_path:
                QMessageBox.warning(self.parent_widget, "警告", "未找到ghostscript，请确保正确安装了Ghostscript 10.04.0")
                return

            command = [
                gs_path,
                "-dNOPAUSE",
                "-dBATCH",
                "-dSAFER",
                "-sDEVICE=mswinpr2",
                f"-sOutputFile=%printer%{self.printer_name}",
                "-dNumCopies=" + str(self.copies_spinbox.value()),
                f"-dDEVICEWIDTHPOINTS={width_mm * 2.834645669291339}",
                f"-dDEVICEHEIGHTPOINTS={height_mm * 2.834645669291339}",
                "-dORIENT1=" + ("1" if hasattr(self, 'is_landscape') and self.is_landscape else "0"),
                "-c",
                "<< /Policies << /PageSize 3 >> >> setpagedevice",
                f"<< /PageOffset [{2.8 * 2.834645669291339} -{1 * 2.834645669291339}] /BeginPage {{ {0.982} dup scale }}  >> setpagedevice",
                "-f",
                file_path
            ]

            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if result.returncode == 0:
                filename = os.path.basename(file_path)
                current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                copies = self.copies_spinbox.value()

                # Log the print job
                log_print_job(
                    timestamp=current_time,
                    sku_or_filename=filename,
                    quantity=copies,
                    printer_name=self.printer_name,
                    status="Printed"
                )

                new_item = f"{current_time} - 打印文件: {filename} (份数: {copies}) - 已打印"
                self.queue_list.insertItem(0, new_item)
                self.file_path.clear()
                self.copies_spinbox.setValue(1)
                self.file_path.setFocus()  # 将焦点设置回文件路径输入框
            else:
                raise Exception(f"打印失败: {result.stderr}")

        except Exception as e:
            QMessageBox.warning(self.parent_widget, "打印错误", str(e))

    def _analyze_and_update_size(self, pdf_path: str) -> Optional[tuple]:
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            width = page.rect.width * 0.352778
            height = page.rect.height * 0.352778

            is_landscape = width > height
            if is_landscape:
                width, height = height, width

            size = (round(width, 1), round(height, 1))
            self.config['last_sizes'][self.printer_name] = size
            self.current_pdf_size = size
            self.is_landscape = is_landscape
            doc.close()
            return size
        except Exception as e:
            print(f"PDF 尺寸分析错误: {str(e)}")
            return None

    def _load_common_files(self):
        common_files_folder = Path(self.manager.other_folder) # Use configured path
        if common_files_folder.exists():
            for file in common_files_folder.glob("*.pdf"):
                self.common_files_list.addItem(file.name)
                print(f"Added common file: {file.name}")  # 调试输出
        else:
            print(f"Folder {common_files_folder} does not exist")  # 调试输出

    def _print_common_file(self, item):
        file_name = item.text()
        folder_path = Path(self.manager.other_folder) # Use configured path
        full_path = os.path.join(folder_path, file_name)
        if os.path.exists(full_path):
            self.file_path.setText(full_path)
            self.copies_spinbox.setValue(1)
            self._print_file()
        else:
            QMessageBox.warning(self.parent_widget, "警告", f"文件不存在: {full_path}")
