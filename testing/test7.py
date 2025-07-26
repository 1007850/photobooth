from pathlib import Path
import booth_config as config

p = config.overlaysPath
print(p)
print(str(p))
if (not p.exists()):
    print("no exist")
if (not p.is_dir()):
    print("not dir")