import json
from pathlib import Path

with open('config.json', 'r') as file:
    data = json.load(file)
    file.close()

printerName: str = data['printerName']
collagePath: Path = Path(data['collagePath']).resolve()
overlaysPath: Path = Path(data['overlaysPath']).resolve()
lutsPath: Path = Path(data['lutsPath']).resolve()

if (not collagePath.exists()): raise Exception(f"ERROR: path for collages {collagePath} specified in config.json does not exist")
if (not overlaysPath.exists()): raise Exception(f"ERROR: path for collages {overlaysPath} specified in config.json does not exist")
if (not lutsPath.exists()): raise Exception(f"ERROR: path for collages {lutsPath} specified in config.json does not exist")