import cv2 as cv
from numpy import uint8, array
import typing

import PIL.Image as img
import PIL.ImageFilter as filter
from pillow_lut import load_cube_file
from pathlib import Path

import booth_config as config


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
    
    def print(self):
        print(f'xmin: {self.xmin}')
        print(f'xmax: {self.xmax}')
        print(f'ymin: {self.ymin}')
        print(f'ymax: {self.ymax}')
        

class overlayItem:
    def __init__(self, overlayPath: Path):
        self.path = overlayPath
        # open overlay
        overlay: cv.typing.MatLike = cv.imread(str(overlayPath), cv.IMREAD_UNCHANGED)
        self.overlayShape: tuple[int, int] = overlay.shape[1], overlay.shape[0] # w,h

        overlayImage: img.Image = img.open(str(overlayPath))
        # modify overlay if strip is detected
        if self.overlayShape[0] * 2 < self.overlayShape[1]:
            self.overlay = img.new(mode="RGBA", size=(self.overlayShape[0]*2,self.overlayShape[1]))
            self.overlay.paste(overlayImage, (0,0))
            self.overlay.paste(overlayImage, (self.overlayShape[0],0))
            # update overlayShape
            self.overlayShape = (self.overlay.width,self.overlay.height)
            overlay = cv.cvtColor(array(self.overlay, dtype=uint8), cv.COLOR_RGBA2BGRA)
        else:
            self.overlay = overlayImage

        # store name of overlay
        self.name = overlayPath.stem

        # identify positioning for image
        alphamask = overlay[:, :, 3]
        contours, heirarchy = cv.findContours(cv.copyMakeBorder(alphamask, 1, 1, 1, 1, cv.BORDER_CONSTANT, value=255), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

        # store images' bounds
        self.bounds: list[bound] = []
        minArea = self.overlayShape[0] * self.overlayShape[1] * config.zoneTolerance
        if len(contours)==0 or len(contours)==1:
            raise Exception("Could not locate bounds for overlay image")
        else:
            for c in contours:
                cbound = bound(c)
                if (cbound.width*cbound.height > minArea and (cbound.width<self.overlayShape[0] or cbound.height<self.overlayShape[1])):
                    self.bounds.append(cbound)


        # determine strip or no strip overlay
        self.bounds.sort(key=lambda x: x.xmin)
        self.mirror = False
        if len(self.bounds)%2==0 and len(self.bounds)>2:
            # check horizontal alignment
            colThreshold = self.overlayShape[0] * config.zoneTolerance
            colMid = self.overlayShape[0] // 2
            leftCol: list[bound] = self.bounds[:len(self.bounds)//2]
            leftDev = max(leftCol, key=lambda x: x.xmin).xmin - min(leftCol, key=lambda x: x.xmin).xmin
            righCol: list[bound] = self.bounds[len(self.bounds)//2:]
            rightDev = max(righCol, key=lambda x: x.xmin).xmin - min(righCol, key=lambda x: x.xmin).xmin
            if leftCol[0].xmax<colMid and righCol[0].xmin>colMid and leftDev<colThreshold and rightDev<colThreshold:
                # check vertical alignment
                self.mirror = True
                rowThreshold = self.overlayShape[1] * config.zoneTolerance
                leftCol.sort(key=lambda x: x.ymin)
                righCol.sort(key=lambda x: x.ymin)
                for i in range(len(leftCol)):
                    if abs(leftCol[i].ymin-righCol[i].ymin) > rowThreshold:
                        self.mirror = False

        # set nbounds for number of photos to take, half for mirrored
        # resort or reform list of bounds so that images are overlayed in chonological order
        if self.mirror:
            self.nbounds = len(leftCol)
            self.bounds = leftCol + righCol
        else:
            self.nbounds = len(self.bounds)
            self.bounds.sort(key=lambda x: x.ymin)
        
        # self.display_with_bounds(overlay.copy())
        
    # bounds verification
    def display_with_bounds(self, overlay_image: cv.typing.MatLike = None):
        if overlay_image is None:
            overlay_image = cv.cvtColor(array(self.overlay, dtype=uint8), cv.COLOR_RGBA2BGRA)
        # Convert to BGR if image has alpha
        if overlay_image.shape[2] == 4:
            overlay_bgr = cv.cvtColor(overlay_image, cv.COLOR_BGRA2BGR)
        else:
            overlay_bgr = overlay_image

        # Draw rectangles for each bound
        for b in self.bounds:
            cv.rectangle(overlay_bgr, b.topleft, b.botright, color=(0, 255, 0), thickness=2)

        # Display the image
        overlay_bgr = cv.resize(overlay_bgr, (1200, 1800))
        cv.imshow(f"Overlay with bounds - {self.name}", overlay_bgr)
        cv.waitKey(0)
        cv.destroyAllWindows()
        

class lutItem:
    def __init__(self, lutPath: Path):
        # store lut name and object itself
        self.lut: filter.Filter = load_cube_file(str(lutPath))
        self.name = lutPath.stem




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
def create_collage(images: list[img.Image], targetPath: Path, overlay: overlayItem, lut: lutItem):

    print("compositing images...")
    # instantiate blank image
    collage = img.new(mode='RGB', size=overlay.overlayShape)

    # add images
    for i in range(overlay.nbounds):
        # crop and resize image
        im: img.Image = resize(images[i], overlay.bounds[i])
        # paste resized images at respective bounds
        collage.paste(im, overlay.bounds[i].topleft)
        if overlay.mirror:
            collage.paste(im, overlay.bounds[i+overlay.nbounds].topleft)
            

    # apply lut to entire image
    collage = collage.filter(lut.lut)
    
    # add overlay
    collage.paste(overlay.overlay, (0,0), overlay.overlay)

    print(f"writing collage {targetPath.stem} to disk...")
    # save to disk
    collage.save(targetPath, format='JPEG', quality=95)
    print("disk write complete")
    return collage


def genLUTPreview(image: img.Image, lut: lutItem):
    return image.filter(lut.lut)
    
def resizeForPreview(inp, ispath: bool):
    return resizeForPreviewPath(inp) if ispath else resizeForPreviewImage(inp)

def resizeForPreviewImage(image: img.Image):
    return image.resize((720,int(720/image.width*image.height)))

def resizeForPreviewPath(imagePath: Path):
    image = img.open(str(imagePath))
    return image.resize((720,int(720/image.width*image.height)))

def setBGGrey(image: img.Image):
    out: img.Image = img.new(mode='RGB', size=image.size, color='grey')
    out.paste(image, (0,0), image)
    return out