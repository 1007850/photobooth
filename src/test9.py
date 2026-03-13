import booth_imgproc as proc
from pathlib import Path

grad = Path(r"C:\Users\yourmum\Downloads\grad.png")
nograd = Path(r"C:\Users\yourmum\Downloads\no_grad.png")
strip = Path(r"C:\Users\yourmum\Downloads\strip.png")
sheet = Path(r"C:\Users\yourmum\Downloads\sheet.png")

grad = proc.overlayItem(grad)
for item in grad.bounds:
    print('\ngrad:')
    item.print()

nograd = proc.overlayItem(nograd)
for item in nograd.bounds:
    print('\nno grad')
    item.print()

strip = proc.overlayItem(strip)
for item in strip.bounds:
    print('\nstrip:')
    item.print()
    
strip.display_with_bounds()

sheet = proc.overlayItem(sheet)
for item in sheet.bounds:
    print('\nsheet:')
    item.print()
    
sheet.display_with_bounds()