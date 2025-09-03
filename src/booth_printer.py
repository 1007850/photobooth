from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt
from pathlib import Path

import booth_config as config

class prn:
    def __init__(self):
        # initialise printer
        print("available printers: " + ", ".join(QPrinterInfo.availablePrinterNames()))
        if (config.printerName not in QPrinterInfo.availablePrinterNames()):
            print("ERROR: printer defined in config.json not available")
        self.printerName = config.printerName
        self.printer = QPrinter()
        self.setDefaults()

        
        # store image here
        self.image: QPixmap = None

    # trigger completely manual print
    def manualPrint(self, filePath: Path):
        print_dialog = QPrintDialog(self.printer)
        if print_dialog.exec():
            self.print()
        self.printer = QPrinter()
        self.setDefaults()
        
    
    # trigger print
    def print(self):
        # get canvas
        painter = QPainter(self.printer)
        # get bound of page
        rect = painter.viewport()
        pagerect = self.printer.pageRect(QPrinter.Unit.DevicePixel)
        # resize QPixmap for page
        scaled = self.image.scaled(pagerect.size(), aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio)
        # print
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        print("log: sent to printer")
    
    # set image to print
    def setImage(self, filePath: Path):
        if filePath.exists() and not filePath.is_dir():
            self.image = QPixmap(str(filePath))
        else:
            raise Exception("ERROR: tried load for printing file that does not exist")
    
    # set image to print interactively
    def interactiveSetImage(self):
        file_name, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.image = QPixmap(file_name)
    
    # set defaults
    def setDefaults(self):
        # set custom default values
        self.printer.setColorMode(QPrinter.ColorMode.Color)
        self.printer.setCopyCount(1)
        self.printer.setDuplex(QPrinter.DuplexMode.DuplexNone)
        self.printer.setFullPage(True)
        self.printer.setPageOrder(QPrinter.PageOrder.FirstPageFirst)
        self.printer.setPageSize(config.pageSize)
        self.printer.setPrintRange(QPrinter.PrintRange.AllPages)
        self.printer.setPrinterName(self.printerName)
        self.printer.setResolution(300)
        print(self.printer.supportedResolutions())
        # self.printer.setResolution(max(self.printer.supportedResolutions()))
        
    def setNumPrints(self, n: int):
        self.printer.setCopyCount(n)
        print(f"log: num prints set to {n}")
        
    # set print settings interactively using dialog
    def setPrintSettings(self):
        print_dialog = QPrintDialog(self.printer)
        if print_dialog.exec():
            print("log: updated printer settings")
        else:
            print("log: did not updated printer settings")
