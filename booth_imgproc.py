import cv2 as cv
import numpy as np
import typing

from pillow_lut import load_cube_file
import PIL.Image as img
from pathlib import Path

import time

class bound:
    offset = 5
    def __init__(self, contour: typing.Sequence[cv.typing.MatLike]):
        rect = cv.boundingRect(contour)
        self.xmin = rect[0] - bound.offset
        self.xmax = rect[0] + rect[2] + bound.offset
        self.ymin = rect[1] - bound.offset
        self.ymax = rect[1] + rect[3] + bound.offset
        self.topleft = (self.xmin, self.ymin)
        self.topright = (self.xmax, self.ymin)
        self.botleft = (self.xmin, self.ymax)
        self.botright = (self.xmax, self.ymax)
        toff = bound.offset + bound.offset
        self.width = rect[2] + toff
        self.height = rect[3] + toff
        self.size = (self.width, self.height)

stime = time.time()
# open overlay
overlay: cv.typing.MatLike = cv.imread("overlay.png", cv.IMREAD_UNCHANGED)
overlayShape = overlay.shape[1], overlay.shape[0]
# identify positioning for image(s)
alphamask = (overlay[:, :, 3] > 100).astype(np.uint8) * 255
del overlay
contours, heirarchy = cv.findContours(alphamask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
# store images' bounds
bounds: list[bound] = []
if len(contours)==0:
    raise Exception("Could not locate bounds for overlay image")
elif len(contours)==1:
    bounds.append(bound(contours[0]))
else:
    for c in contours[:-1]:
        bounds.append(bound(c))

# state management for posters
nbounds = len(bounds)


# open lut
# selectedlut = load_cube_file(r"C:\Users\yourmum\OneDrive - Singapore University of Technology and Design\Photobooths\photobooth_v3\sepia.CUBE")
selectedlut = load_cube_file(r"newspaper.CUBE")


print(f"IMPROC LOAD TIME: {time.time()-stime}")


def resize(inImage: img.Image, tb: bound) -> img.Image:

    # crop image
    predHeight = inImage.width/tb.width*tb.height
    if (predHeight < inImage.height):
        cropOffset = (inImage.height - predHeight) // 2
        left = 0
        top = cropOffset
        right = inImage.width
        bottom = inImage.height - cropOffset
    else:
        cropOffset = (inImage.width - inImage.height/tb.height*tb.width) // 2
        left = cropOffset
        top = 0
        right = inImage.width - cropOffset
        bottom = inImage.height
    inImage = inImage.crop((left, top, right, bottom))

    # scale image
    inImage = inImage.resize(tb.size, img.Resampling.LANCZOS)
    
    return inImage


# composites and exports posters
def create_collage(images: list[img.Image], targetPath: Path=None):

    print("compositing images...")
    # instantiate blank image
    collage = img.new(mode='RGB', size=overlayShape)

    # add images
    for i in range(nbounds):
        # crop and resize image
        im: img.Image = resize(images[i], bounds[i])
        # apply lut
        # im = im.filter(selectedlut)
        # paste resized images at respective bounds
        collage.paste(im, bounds[i].topleft)
    
    # add overlay
    selectedOverlay = img.open("overlay.png")
    if not selectedOverlay:
        raise Exception("ERROR LOADING SELECTED OVERLAY")
    collage.paste(selectedOverlay, (0,0), selectedOverlay)

    # apply lut to entire image
    collage = collage.filter(selectedlut)

    print(f"writing collage {targetPath.stem} to disk...")
    # save to disk
    if targetPath!=None:
        collage.save(targetPath, format='JPEG', quality=95)
    print("disk write complete")
    return collage