
from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
import PIL.Image as img

class imageBox(QLabel):
    clicksig = pyqtSignal(bool)

    def __init__(self, imagePath: Path, updateLUTBox):
        super().__init__()
        self.qim = QPixmap(str(imagePath))
        self.loadQIM()
        self.updateLUTBox = updateLUTBox

    def __init__(self, image: img.Image, updateLUTBox):
        super().__init__()
        self.qim = QPixmap.fromImage(img.ImageQt.ImageQt(image))
        self.loadQIM()
        self.updateLUTBox = updateLUTBox
        
    def __init__(self, updateLUTBox):
        super().__init__()
        self.updateLUTBox = updateLUTBox
    
    def loadQIM(self, image: img.Image):
        self.setPixmap(self.qim)
        self.setMaximumHeight(200)
        self.setMaximumWidth(200)

        self.clicksig.connect(self.handleClick)

    def mousePressEvent(self, ev):
        self.clicksig.emit(True)
        
    @pyqtSlot(bool)
    def handleClick(self, v: bool):
        self.updateLUTBox()
        self.toggleBorder(True)
        
    def toggleBorder(self, On: bool):
        if On:
            self.setStyleSheet("border: 5px solid grey")
        else:
            self.setStyleSheet()

        


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