import booth_config as config


settingsPath = config.configPath.parent / 'styling' / 'settings.css'
with open(settingsPath, 'r') as f:
    SETTINGS = f.read()

mainPath = config.configPath.parent / 'styling' / 'main.css'
with open(mainPath, 'r') as f:
    MAIN = f.read()