
from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path

class imageBox(QLabel):
    clicksig = pyqtSignal(bool)

    def __init__(self, imagePath: Path):
        super().__init__()
        self.im = QPixmap(str(imagePath))
        self.setPixmap(self.im)
        self.setMaximumHeight(200)
        self.setMaximumWidth(200)

        self.clicksig.connect(self.handleClick)

    def mousePressEvent(self, ev):
        self.clicksig.emit(True)
        
    @pyqtSlot(bool)
    def handleClick(self, v: bool):
        print("image clicked")


class imagePreview(QMainWindow):
    def __init__(self, imagePath: Path):
        super().__init__()
        self.imagePath = imagePath
        self.initWindow()
        self.show()
    
    def initWindow(self):
        self.setWindowTitle("Image Preview")
        
        self.label = QLabel("urmum")
        self.label.setMinimumHeight(200)
        self.label.setMinimumWidth(200)
        self.setCentralWidget(self.label)

        self.pixmap = QPixmap(str(self.imagePath))
        self.label.setPixmap(self.pixmap)
        self.ratio = self.pixmap.width() / self.pixmap.height()
        
    def resizeEvent(self, a0):
        self.blockSignals(True)
        scaled_pixmap = self.pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        
        new_width = self.width()
        new_height = int(new_width // self.ratio)
        self.resize(new_width, new_height)
        self.blockSignals(False)