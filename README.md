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
All Paths can be relative path such as `./relative/path`.

| Property | Description |
| --- | --- |
| printerName | Name of printer as enumarated by system. App will still start if printer is not available, but an error message will log in output. If you don't know your printer's name, run app and check output for enumerated printers. |
| collagePath | Path to directory for exporting collages. |
| lutsPath | Path to directory for app to find available luts. Needs to be pre-populated with LUTs before running. | 
| overlaysPath | Path to directory for app to find available overlays. Needs to be pre-populated with overlays before running. | 
| tmpPath | Path for temporarily saving images from camera - only used in Windows. |
| previewImagePath | Path to image file used to preview LUTs in app gui. If file does not exist, will default to triggering camera to get photo |
| previewsPath | Path to store generated preview images |
| paperSize | Page/paper size for printer. If value does not match known paper size, will instead use custom page settings. |
| customPageWidth | Custom page width for printing. Only used if no match for paperSize can be found |
| customPageHeight | Custom page height for printing. Only used if no match for paperSize can be found |
| customPageName | Custom page name for printing, probably doesn't affect print. Only used if no match for paperSize can be found |


## Recommended Camera Configurations
1. Manual everything, focus, exposure, white balance. This will reduce the latency and reduce mishaps.
2. For windows, set to export jpeg only, the app might crash otherwise.


## Running

Before starting, plug camera into system

\
Imaging Edge Setup(_Windows and Sony cameras only_)
1. Launch Sony Imaging Edge, and start Remote app
2. Ensure shortcut for triggering capture is  the `1` key
3. Ensure save location is `tmp/` directory in project folder, please create if needed
4. Ensure save type is jpeg, no raw
5. Ensure autofocus is disabled, adjust delay in `booth_camera.py` if autofocus is needed

\
Running App
1. Run booth_gui.py


## Usage

Buttons are self-explanatory, below are some additional points.

| Button | Detail |
| --- | --- |
| Capture | Triggers camera to capture enough images in the selected collage. The delay between shots is specified in config. |
| Export | Exports the last captured images with the frame selected to path specified in config. |
| Preview Last | Opens window showing the last exported collage. Don't click without having clicked export. |
| Print Last | Prints the last exported collage, using the current print settings. |
| Manual Print | Opens dialogs to select file to print and set print settings. |
| Print Settings | Opens dialog to set print settings. |


## Issues
Feel free to fork :)
