
from PyQt6.QtWidgets import QLabel, QMainWindow, QWidget
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap, QImage, QFont, QFontMetrics
from pathlib import Path
from io import BytesIO
import qrcode




class imageBox(QLabel):
    clicksig = pyqtSignal(bool)

    def __init__(self, label: str, clickHandler):
        super().__init__()
        self.clickHandler = clickHandler
        self.label = QLabel(label)
        self.clicksig.connect(self.handleClick)
        self.qim = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(30)
        self.setMinimumHeight(20)
    
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
        self.setCentralWidget(self.label)

        self.pixmap = QPixmap(str(self.imagePath))
        self.label.setPixmap(self.pixmap)
        self.ratio = self.pixmap.width() / self.pixmap.height()

        set_dims(self, 0.9, 0.35)
        self.resize(self.minimumSize())
        
    def resizeEvent(self, a0):
        self.blockSignals(True)
        scaled_pixmap = self.pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        self.blockSignals(False)
        


class QRWindow(QMainWindow):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.label = QLabel("urmum")
        set_dims(self, 0.7, 0.4)
        self.setCentralWidget(self.label)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        image = QImage.fromData(buffer.read())
        self.pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(self.pixmap)
        self.ratio = self.pixmap.width() / self.pixmap.height()
        
        self.show()
        self.setFocus()
        
    def resizeEvent(self, a0):
        self.blockSignals(True)
        scaled_pixmap = self.pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        # self.resize(self.width(), int(self.width()//self.ratio))
        self.blockSignals(False)


class textWindow(QMainWindow):
    def __init__(self, text: str, bufferRatio: float=0.05, scaleStep: int=1):
        self.bufferRatio = bufferRatio
        self.scaleStep = scaleStep
        super().__init__()
        self.text = text
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        set_dims(self)
        self.setCentralWidget(self.label)
        
        labelfont = QFont()
        labelfont.setPixelSize(10)
        self.label.setFont(labelfont)
        
        self.show()
    
    def resizeEvent(self, a0):
        self.blockSignals(True)
        winWidth = a0.size().width()
        winHeight = a0.size().height()
        newFont = QFont()
        newFont.setPixelSize(self.label.font().pixelSize())
        newHeight = newFont.pixelSize()
        ratio = (winHeight-newHeight) / winHeight
        while ratio > self.bufferRatio or ratio < 0:
            if ratio > self.bufferRatio:
                newPxSize = newFont.pixelSize() + self.scaleStep
            else:
                newPxSize = newFont.pixelSize() - self.scaleStep
            newFont.setPixelSize(newPxSize)
            newHeight = newFont.pixelSize()
            ratio = (winHeight-newHeight) / winHeight

        newWidth = newFont.pixelSize() * len(self.label.text()) // 2
        if (winWidth-newWidth) / winWidth < self.bufferRatio:
            while (winWidth-newWidth) / winWidth < self.bufferRatio:
                newPxSize = newFont.pixelSize() - self.scaleStep
                newFont.setPixelSize(newPxSize)
                newWidth = newFont.pixelSize() * len(self.label.text()) // 2
            
        self.label.setFont(newFont)
        self.blockSignals(False)
        # print(f'FONT HEIGHT: {self.label.font().pixelSize()}')
        # print(f'WINDOW HEIGHT: {a0.size().height()}')


def set_dims(window: QMainWindow, minHRatio: float=0.5, minWRatio: float=0.5):
    geometry = window.screen().availableGeometry()
    window.setMaximumHeight(geometry.height())
    window.setMinimumHeight(int(geometry.height()*minHRatio))
    window.setMaximumWidth(geometry.width())
    window.setMinimumWidth(int(geometry.width()*minWRatio))

