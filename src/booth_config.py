import json
from pathlib import Path
from PyQt6.QtGui import QPageSize
from PyQt6.QtCore import QSizeF
import booth_fs as ffs
import sys
from pathlib import Path

from booth_logging import logger, loglevels


if getattr(sys, 'frozen', False):
    prepend = Path(sys.executable).parent
else:
    prepend = Path("./")

with open(prepend/'config.json', 'r') as file:
    data = json.load(file)
    file.close()


printerName: str = data['printerName']
collagePath: Path = prepend / Path(data['collagePath']).resolve()
overlaysPath: Path = prepend / Path(data['overlaysPath']).resolve()
lutsPath: Path = prepend / Path(data['lutsPath']).resolve()
tmpPath: Path = prepend / Path(data['tmpPath']).resolve()
previewImagePath: Path = prepend / Path(data['previewImagePath']).resolve()
previewsPath: Path = prepend / Path(data['previewsPath']).resolve()

# if (not overlaysPath.exists()): raise Exception(f"ERROR: path for overlays {overlaysPath} specified in config.json does not exist")
# if (not lutsPath.exists()): raise Exception(f"ERROR: path for LUTs {lutsPath} specified in config.json does not exist")
if not overlaysPath.exists():
    logger.post(f"ERROR: path for overlays {overlaysPath} specified in config.json does not exist", loglevels.ERROR)
if not lutsPath.exists():
    logger.post(f"ERROR: path for LUTs {lutsPath} specified in config.json does not exist", loglevels.ERROR)

try:
    pageSize = QPageSize(eval(r"QPageSize.PageSizeId." + data['paperSize']))
except:
    logger.post('WARNING: falling back to custom paper dimensions', loglevels.WARNING)
    # print("log: falling back to custom paper dimensions")
    pageSize = QPageSize(QSizeF(data['customPageWidth'],data['customPageHeight']), QPageSize.Unit.Millimeter, name=data['customPageName'])

captureDelay: int = data['captureDelay']
zoneTolerance: float = data['zoneTolerance']

# if zoneTolerance<0 or zoneTolerance>1: raise Exception("ERROR: zone tolarance specified in config.json needs to be between 0 and 1")
if zoneTolerance<0 or zoneTolerance>1:
    logger.post("ERROR: zone tolarance specified in config.json needs to be between 0 and 1", loglevels.ERROR)

mockCamera: bool = data['mockCamera']
standaloneMode: bool = data['standaloneMode']
print: bool = data['print']
upload: bool = data['upload']


# print(f'''
#       printer name: {printerName}
#       folder to save exports: {collagePath}
#       folder with overlays: {overlaysPath}
#       folder with LUTs: {lutsPath}
#       folder for temporary files: {tmpPath}
#       path to preview image: {previewImagePath if previewImagePath.exists() else "NO IMAGE, DEFAULTING TO TRIGGER CAMERA - see readme for info"}
#       path to save preview samples with LUTs applied: {previewsPath}
#       page dimensions: {pageSize.definitionSize().width()} by {pageSize.definitionSize().height()}
#       delay for capture: {captureDelay}s
#       tolerance for zone detection: {zoneTolerance}
# ''')
configinfo = f'''printer name: {printerName}
folder to save exports: {collagePath}
folder with overlays: {overlaysPath}
folder with LUTs: {lutsPath}
folder for temporary files: {tmpPath}
path to preview image: {previewImagePath if previewImagePath.exists() else "NO IMAGE, DEFAULTING TO TRIGGER CAMERA - see readme for info"}
path to save preview samples with LUTs applied: {previewsPath}
page dimensions: {pageSize.definitionSize().width()} by {pageSize.definitionSize().height()}
delay for capture: {captureDelay}s
tolerance for zone detection: {zoneTolerance}'''
for line in configinfo.split('\n'):
    logger.post(line, loglevels.INFO)


def generatePaths():
    # generate collagePath if necessary
    if (not collagePath.exists()):
        ffs.create_directory(collagePath)

    # generate tmpPath if necessary, enforce that directory needs to be empty
    if (not tmpPath.exists()):
        ffs.create_directory(tmpPath)
    if ffs.get_children(tmpPath)!=[]:
        # raise Exception(f"ERROR: please clear tmp directory {tmpPath}")
        for child in ffs.get_children(tmpPath):
            child.unlink()

    # generate previewImagePath if necessary
    if (not previewsPath.exists()):
        ffs.create_directory(previewsPath)