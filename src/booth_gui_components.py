
from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path

class imageBox(QLabel):
    clicksig = pyqtSignal(bool)

    def __init__(self, label: str, clickHandler):
        super().__init__()
        self.clickHandler = clickHandler
        self.label = QLabel(label)
        self.clicksig.connect(self.handleClick)
        self.qim = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
    
    def loadQIM(self, imagePath: Path):
        self.qim = QPixmap(str(imagePath))
        self.setPixmap(self.qim.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def mousePressEvent(self, ev):
        self.clicksig.emit(True)
        
    @pyqtSlot(bool)
    def handleClick(self, v: bool):
        self.clickHandler(self.label.text())
        
    def toggleBorder(self, On: bool):
        if On:
            self.setStyleSheet("border: 5px solid gray; border-style: inset")
        else:
            self.setStyleSheet("border: 5px transparent gray; border-style: inset")

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if (self.qim is not None):
            self.blockSignals(True)
            self.setPixmap(self.qim.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.blockSignals(False)


        


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
        super().resizeEvent(a0)
        scaled_pixmap = self.pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        self.blockSignals(True)
        self.resize(self.width(), int(self.width()//self.ratio))
        self.blockSignals(False)