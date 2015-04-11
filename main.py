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
            print 'TransitingFile mkdir:', directory
            os.makedirs(directory)
        shutil.copyfile(self.filename, newfilename)
        self.newfilename = newfilename
        print 'TransitingFile copyTo:', self.newfilename
    def write (self, filepath):
        shutil.copyfile(self.filename, filepath)
        print 'TransitingFile write:', filepath

class ImageFile:
    def __init__ (self, file):
        self.file = file
    def open (self):
        self.image = Image.open(self.file)
    def resize (self, basewidth):
        wpercent = (basewidth / float(self.image.size[0]))
        hsize = int((float(self.image.size[1]) * float(wpercent)))
        self.image = self.image.resize((basewidth, hsize), Image.ANTIALIAS)
    def write (self, path):
        exif = self.image.info['exif']
        self.image.save(path, exif=exif)
        print 'ImageFile writing:', path
    def close (self):
        del self.image

class ImageFilePair:
    def __init__ (self):
        self.left = None
        self.right = None
    def setLeft (self, key, file):
        self.left = key
        self.leftfile = file
    def setRight (self, key, file):
        self.right = key
        self.rightfile = file

def main():
    if raw_input('copy from sd card? y or n') == 'y':
        for file in os.listdir(_PATH1_):
            transitingFile = TransitingFile(os.path.join(_PATH1_, file))
            directory = os.path.join(_PATH1_, transitingFile.timestring[:-2])
            transitingFile.copyTo(directory)

    if raw_input('copy from photos_nikon to google drive? y or n') == 'y':
        for root, dirs, files in os.walk(_PATH2_):
            for file in files:
                if file[-3:] != 'JPG': # only do jpg files
                    continue
                YYYYMM = os.path.split(root)[-1][:6] # expecting YYYYMM
                YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
                directory = os.path.join(_PATH3_, YYYYMM) 
                if not (os.path.exists(directory)):
                    print 'main mkdir:', directory
                    os.makedirs(directory)
                # ImageFile should just open, resize & save as.
                existingImageFilePath = os.path.join(root, file)
                newImageFilePath = os.path.join(directory, YYYYMMDD+'_'+file)
                image = ImageFile(existingImageFilePath)
                image.open()
                image.resize(1200)
                image.write(newImageFilePath)
                image.close()
    if raw_input('sync from photos_nikon to google drive? y or n') == 'y':
        ImageFilePairs = []
        for root, dirs, files in os.walk(_PATH2_):
            for file in files:
                if file[-3:] != 'JPG': # only do jpg files
                    continue
                YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
                ifp = ImageFilePair()
                ifp.left = YYYYMMDD+'_'+file
                ifp.leftfile = os.path.join(root, file)
                ImageFilePairs.append(ifp)
        for root, dirs, files in os.walk(_PATH3_):
            for file in files:
                if file[-3:] != 'JPG': # only do jpg files
                    continue
                match = next((x for x in ImageFilePairs if x.left == file), None)
                if match:
                    match.right = file
                    match.rightfile = os.path.join(root, file)
        for ifp in ImageFilePairs:
            if ifp.left and ifp.right:
                if os.path.getmtime(ifp.leftfile) > os.path.getmtime(ifp.rightfile):
                    #TransitingFile(ifp.leftfile).write(ifp.rightfile)
                    image = ImageFile(ifp.leftfile)
                    image.open()
                    image.resize(1200)
                    image.write(ifp.rightfile)
                    image.close()
main()
