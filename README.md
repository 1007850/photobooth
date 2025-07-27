# photobooth

Photobooth app written in Python.


## Requirements

| OS | Requirements |
| --- | --- |
| MacOS | Python |
| Linux | Python |
| Windows (Sony Cameras Only) | Python, Sony Imaging Edge |


## Installation

Windows
1. `pip install -r requirements_win32.txt` in root directory
2. Install [Sony Imaging Edge Desktop](https://creatorscloud.sony.net/catalog/en-us/ie-desktop/index.html)
3. Open `config.json` and modify. Details is configuration section below.

MacOS/Linux
1. `pip install -r requirements_posix.txt` in root directory
2. Open `config.json` and modify. Details in configuration section below.

## Setup

LUTS
1. Open a sample image in Photoshop
2. Create desired look using only adjustment layers
3. Export as .CUBE lut, with 64 grid size
4. Repeat for as many designs as needed and place in configured lutsPath folder

Overlays
1. Create design with appropriate aspect ratio for print paper
2. Set transparency in areas where photos are meant to be placed to 0%
3. Export as .png image with alpha layer enabled
4. Repeat for as many overlays as needed and place in configured overlaysPath folder


## Configuration
Configuraiton is done in `config.json`. The property names are self-explanatory, see below for details.

| Property | Description |
| --- | --- |
| printerName | Name of printer as enumarated by system. App will still start if printer is not available, but an error message will log in output. If you don't know your printer's name, run app and check output for enumerated printers. |
| collagePath | Path to directory for exporting collages. Can be relative path such as `./relative/path` |
| lutsPath | Path to directory for available luts. Can be relative path such as `./relative/path` | 
| overlaysPath | Path to directory for available overlays. Can be relative path such as `./relative/path` | 


## Running

Imaging Edge Setup(_Windows and Sony cameras only_)
1. Launch Sony Imaging Edge, and start Remote app
2. Ensure shortcut for triggering capture is  the `1` key
3. Ensure save location is `tmp/` directory in project folder, please create if needed
4. Ensure save type is jpeg, no raw
5. Ensure autofocus is disabled, adjust delay in `booth_camera.py` if autofocus is needed

\
Running App
1. Run booth_gui.py


## Issues
Feel free to fork :)