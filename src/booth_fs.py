from pathlib import Path
import shutil
import time
from datetime import datetime, timezone, timedelta


# writes files into paths provided
def write_file(targetPath: Path, data, overwrite: bool=False):
    if targetPath.parent.exists() == False:
        raise Exception("TRIED TO WRITE FILE IN DIRECTORY THAT DOES NOT EXIST")
    if overwrite == False and targetPath.exists() == False:
        raise Exception("TRIED TO OVERWRITE FILE WITH FLAG SET TO FALSE")
    dataType = type(data)
    if dataType == 'bytes':
        targetPath.write_bytes(data)
    elif dataType == 'str':
        targetPath.write_text(data)
    else:
        raise Exception(f'TRIED TO WRITE DATA OF UNAPPROVED TYPE {dataType}')
    
# creates directory, use flag fill to populate missing parent directories
def create_directory(targetPath: Path, fill: bool =True): 
    try:
        targetPath.mkdir(mode=0o777, parents=fill, exist_ok=True)
        print(f'log: created directory {targetPath}')
    except ValueError:
        print("TRIED TO CREATE DIRECTORY WITH PARENTS THAT DOES NOT EXIST")

# fetches paths of children of target
def get_children(targetPath: Path) -> list[Path]:
    if not targetPath.exists() or not targetPath.is_dir():
        return []
    out =  [ x for x in targetPath.iterdir() ]
    return out

# readable toggles between pretty and path-compatible
def get_time(readable: bool):
    if readable:
        display = time.strftime(r'%d/%m/%Y %H:%M:%S')
    else:
        display = time.strftime(r'%y%m%d_%H%M%S')
    return display

# gets RFC 3339 date-time
def get_rfc3339(addTime: int =0):
    dtime = datetime.now(timezone.utc) + timedelta(days=addTime)
    return dtime.astimezone().isoformat()

# deletes a target file
def rm_file(targetPath: Path):
    try:
        targetPath.unlink()
    except FileNotFoundError:
        print("TRIED TO DELETE FILE THAT DOES NOT EXIST")

# moves files from source to target, creates intermediate dirs
def move_contents(sourcePath: Path, destPath: Path) -> list[Path]:
    shutil.copytree(sourcePath, destPath)
    return get_children(destPath)

# clear target and/or descendants 
def clear_target(targetPath: Path):
    if not targetPath.exists():
        raise Exception("No such path to remove!")
    if targetPath.is_dir():
        shutil.rmtree(targetPath)
    else:
        rm_file(targetPath)

def empty_target(targetPath: Path):
    clear_target(targetPath)
    targetPath.mkdir(mode=0o777)
