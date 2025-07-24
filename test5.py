from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPixmap, QPainter
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
        print_dialog = QPrintDialog(printer, self)

        if print_dialog.exec():
            print(f"""
            collatedCopies = {printer.collateCopies()}
            colorMode = {printer.colorMode()}
            copyCount = {printer.colorCount()}
            creator = {printer.creator()}
            docName = {printer.docName()}
            duplex = {printer.duplex()}
            fontEmbeddingEnabled = {printer.fontEmbeddingEnabled()}
            fromPage = {printer.fromPage()}
            fullPage = {printer.fullPage()}
            isValid = {printer.isValid()}
            outputFileName = {printer.outputFileName()}
            outputFormat = {printer.outputFormat()}
            pageOrder = {printer.pageOrder()}
            pageRect = {printer.pageRect(QPrinter.Unit.Inch)}
            paperRect = {printer.paperRect(QPrinter.Unit.Inch)}
            paperSource = {printer.paperSource()}
            pdfVersion = {printer.pdfVersion()}
            printengine = {printer.printEngine()}
            printProgram = {printer.printProgram()}
            printRange = {printer.printRange()}
            printerName = {printer.printerName()}
            printerSelectionOption = Not available
            printerState = {printer.printerState()}
            resolution = {printer.resolution()}
                  """)
        
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