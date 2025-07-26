import json

with open('config.json', 'r') as file:
    data = json.load(file)
    file.close()

printerName = data['printerName']