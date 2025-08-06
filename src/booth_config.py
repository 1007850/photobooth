import json
from pathlib import Path
from PyQt6.QtGui import QPageSize
from PyQt6.QtCore import QSizeF
import booth_fs as ffs

with open('config.json', 'r') as file:
    data = json.load(file)
    file.close()

printerName: str = data['printerName']
collagePath: Path = Path(data['collagePath']).resolve()
overlaysPath: Path = Path(data['overlaysPath']).resolve()
lutsPath: Path = Path(data['lutsPath']).resolve()
tmpPath: Path = Path(data['tmpPath']).resolve()
previewImagePath: Path = Path(data['previewImagePath']).resolve()
previewsPath: Path = Path(data['previewsPath']).resolve()

if (not overlaysPath.exists()): raise Exception(f"ERROR: path for overlays {overlaysPath} specified in config.json does not exist")
if (not lutsPath.exists()): raise Exception(f"ERROR: path for LUTs {lutsPath} specified in config.json does not exist")

try:
    pageSize = QPageSize(eval(r"QPageSize.PageSizeId." + data['paperSize']))
except:
    print("log: falling back to custom paper dimensions")
    pageSize = QPageSize(QSizeF(data['customPageWidth'],data['customPageHeight']), QPageSize.Unit.Millimeter, name=data['customPageName'])

captureDelay: int = data['captureDelay']



print(f'''
      printer name: {printerName}
      folder to save exports: {collagePath}
      folder with overlays: {overlaysPath}
      folder with LUTs: {lutsPath}
      folder for temporary files: {tmpPath}
      path to preview image: {previewImagePath if previewImagePath.exists() else "NO IMAGE, DEFAULTING TO TRIGGER CAMERA - see readme for info"}
      path to save preview samples with LUTs applied: {previewsPath}
''')


def generatePaths():
    # generate collagePath if necessary
    if (not collagePath.exists()):
        ffs.create_directory(collagePath)

    # generate tmpPath if necessary, enforce that directory needs to be empty
    if (not tmpPath.exists()):
        ffs.create_directory(tmpPath)
    if ffs.get_children(tmpPath)!=[]:
        raise Exception(f"ERROR: please clear tmp directory {tmpPath}")

    # generate previewImagePath if necessary
    if (not previewsPath.exists()):
        ffs.create_directory(previewsPath)