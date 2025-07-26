from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPixmap, QPainter, QPageSize
from PyQt6.QtCore import Qt

class PrintImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Print Image Example")

        self.image = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        load_button = QPushButton("Load Image")
        load_button.clicked.connect(self.load_image)
        self.layout.addWidget(load_button)

        print_button = QPushButton("Print Image")
        print_button.clicked.connect(self.print_image)
        self.layout.addWidget(print_button)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.image = QPixmap(file_name)

    def print_image(self):
        if not self.image:
            return

        printer = QPrinter()
        
        printer.setColorMode(QPrinter.ColorMode.GrayScale)
        printer.setCopyCount(2)
        printer.setDuplex(QPrinter.DuplexMode.DuplexNone)
        printer.setFullPage(True)
        printer.setPageOrder(QPrinter.PageOrder.FirstPageFirst)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPrintRange(QPrinter.PrintRange.AllPages)
        printer.setPrinterName("Canon TS5300 series")
        printer.setResolution(300)
        
        painter = QPainter(printer)
        rect = painter.viewport()
        scaled = self.image.scaled(rect.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)  # Keep aspect ratio
        painter.drawPixmap(rect.topLeft(), scaled)
        painter.end()

if __name__ == "__main__":
    app = QApplication([])
    window = PrintImageApp()
    window.show()
    app.exec()