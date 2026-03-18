from pathlib import Path


src = Path(r'C:\Users\yourmum\Downloads\photobooth\src')
root = Path(r'C:\Users\yourmum\Downloads\photobooth')
x = Path('./requirements_posix.txt')
print(f'{x.is_absolute()}')
print(f'{root.is_absolute()}')
print(root/src)
print(src/root)
print(src/x)
print(x/src)
print((src/x).is_absolute())