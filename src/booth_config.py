import json
from pathlib import Path
from PyQt6.QtGui import QPageSize
from PyQt6.QtCore import QSizeF
import booth_fs as ffs
import sys
from pathlib import Path

from booth_logging import logger, loglevels




def getConfigPath():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / 'config.json'
    return Path(__file__).parent.resolve() / 'config.json'

with open(getConfigPath(), 'r') as file:
    data = json.load(file)
    file.close()

printerName: str = data['printerName']

workingPath: Path = Path(data['workingPath'])
if not workingPath.exists():
    from booth_gui_components import textWindow
    warning = textWindow("workingPath in config is not set or does not exist\nplease set the working directory then restart")
    logger.post("workingPath in config is not set or does not exist\nplease set the working directory then restart", loglevels.ERROR)

collagePath: Path = workingPath / Path(data['collagePath'])
overlaysPath: Path = workingPath / Path(data['overlaysPath'])
lutsPath: Path = workingPath / Path(data['lutsPath'])
tmpPath: Path = workingPath / Path(data['tmpPath'])
previewImagePath: Path = workingPath / Path(data['previewImagePath'])
previewsPath: Path = workingPath / Path(data['previewsPath'])

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
        logger.post(f"INFO: created path {collagePath} as collagePath", loglevels.WARNING)

    # generate tmpPath if necessary, clear directory if not empty
    if (not tmpPath.exists()):
        ffs.create_directory(tmpPath)
    else:
        for child in ffs.get_children(tmpPath):
            child.unlink()
            logger.post(f"INFO: removed {child.name} from tmp path", loglevels.WARNING)

    # generate previewImagePath if necessary
    if (not previewsPath.exists()):
        ffs.create_directory(previewsPath)
        logger.post(f"INFO: created path {previewsPath} as previewsPath", loglevels.WARNING)