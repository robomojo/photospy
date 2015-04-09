# STANDARD PYTHON MODULES
import os, time
import shutil
import datetime
# PILLOW MODULES
from PIL import Image

_PATH1_ = 'F:\\DCIM\\100D5300'
_PATH2_ = 'd:\\photos_nikon'
_PATH3_ = 'd:\\google drive\\photos_nikon'

class TransitingFile:
    def __init__ (self, file):
        self.file = os.path.basename(file) 
        self.filename = file 
        self.timestring = time.strftime('%Y%m%d', time.gmtime(os.path.getctime(self.filename))) # YYYYMMDD

    def copyTo (self, directory, pre=None):
        file = self.file if pre == None else pre + self.file
        newfilename = os.path.join(directory, file)
        if not (os.path.exists(directory)):
            print 'making directory:', directory
            os.makedirs(directory)
        shutil.copyfile(self.filename, newfilename)
        self.newfilename = newfilename
        print 'copying to:', self.newfilename

class ImageFile:
    def __init__ (self, file, writefile = None):
        self.file = file
        self.writefile = file if writefile == None else writefile # TODO: writefile is new filename
        pass
    def resize (self, basewidth):
        image = Image.open(self.file)
        wpercent = (basewidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((basewidth, hsize), Image.ANTIALIAS)
        image.save(self.writefile)

if raw_input('copy from sd card? y or n') == 'y':
    for file in os.listdir(_PATH1_):
        transitingFile = TransitingFile(os.path.join(_PATH1_, file))
        directory = os.path.join(_PATH1_, transitingFile.timestring[:-2])
        transitingFile.copyTo(directory)

if raw_input('copy from photos_nikon to google drive? y or n') == 'y':
    for root, dirs, files in os.walk(_PATH2_):
        for file in files:
            print file
            if file[-3:] != 'JPG': # only do jpg files
                continue
            transitingFile = TransitingFile(os.path.join(root, file))
            YYYYMM = os.path.split(root)[-1][:6] # expecting YYYYMM
            YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
            directory = os.path.join(_PATH3_, YYYYMM) 
            # TODO: we shouldn't be copying, instead ImageFile should just open, resize & save as.
            transitingFile.copyTo(directory, YYYYMMDD+'_')
            image = ImageFile(os.path.join(directory, transitingFile.newfilename))
            image.resize(1200)
