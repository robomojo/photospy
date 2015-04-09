# STANDARD PYTHON MODULES
import os.path, time
import shutil
import datetime
# PILLOW MODULES
from PIL import Image

_PATH1_ = 'F:\\DCIM\\100D5300'
_PATH2_ = 'd:\\photos_nikon'
_PATH3_ = 'd:\\google drive\\photos_nikon'

class TransitingFile:
    def __init__ (self, file, src, dest):
        self.file = file 
        self.filename = os.path.join(src, file)
        self.timestring = time.strftime('%Y%m%d', time.gmtime(os.path.getctime(self.filename)))
        self.destination = os.path.join(dest, self.timestring)
        self.newfilename = os.path.join(self.destination, self.file)
        pass

    def copyTo_PATH2_(self):
        if not (os.path.exists(self.destination)):
            print 'making directory:', self.destination
            os.makedirs(self.destination)
        shutil.copyfile(self.filename, self.newfilename)
        print 'copying to:', self.newfilename

    def copyTo_PATH3_(self):
        
        pass

for file in os.listdir(_PATH1_):
    transitingFile = TransitingFile(file, _PATH1_,_PATH2_)
    #transitingFile.copyTo_PATH2_()
    transitingFile.copyTo_PATH3_()
