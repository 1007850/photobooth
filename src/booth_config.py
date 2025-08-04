import json
from pathlib import Path
from PyQt6.QtGui import QPageSize
from PyQt6.QtCore import QSizeF

with open('config.json', 'r') as file:
    data = json.load(file)
    file.close()

printerName: str = data['printerName']
collagePath: Path = Path(data['collagePath']).resolve()
overlaysPath: Path = Path(data['overlaysPath']).resolve()
lutsPath: Path = Path(data['lutsPath']).resolve()
tmpPath: Path = Path(data['tmpPath']).resolve()
previewsPath: Path = Path(data['previewsPath']).resolve()

if (not collagePath.exists()): raise Exception(f"ERROR: path for collages {collagePath} specified in config.json does not exist")
if (not overlaysPath.exists()): raise Exception(f"ERROR: path for collages {overlaysPath} specified in config.json does not exist")

try:
    pageSize = QPageSize(eval(QPageSize.PageSizeId + "." + data['paperSize']))
except:
    print("log: falling back to custom paper dimensions")
    pageSize = QPageSize(QSizeF(data['customPageWidth'],data['customPageHeight']), QPageSize.Unit.Millimeter, name=data['customPageName'])

captureDelay: int = data['captureDelay']