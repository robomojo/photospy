# STANDARD PYTHON MODULES
import os, time
import shutil
import datetime
import sys
import ConfigParser
# PILLOW MODULES
from PIL import Image

# determine if application is ascript file or frozen exe
if getattr(sys, 'frozen', False):
    SCRIPT_DIRECTORY = os.path.dirname(sys.executable)
elif __file__:
    SCRIPT_DIRECTORY = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(SCRIPT_DIRECTORY, 'example.ini')

class TransitingFile:
    def __init__ (self, file):
        self.file = os.path.basename(file)
        self.filename = file
        self.timestring = time.strftime('%Y%m%d', time.gmtime(os.path.getctime(self.filename))) # YYYYMMDD
    def copyTo (self, directory, pre=None):
        file = self.file if pre == None else pre + self.file
        newfilename = os.path.join(directory, file)
        if not (os.path.exists(directory)):
            os.makedirs(directory)
        shutil.copyfile(self.filename, newfilename)
        self.newfilename = newfilename
        return 'TransitingFile copyTo: '+self.newfilename
    def write (self, filepath):
        shutil.copyfile(self.filename, filepath)
        return 'TransitingFile write: '+filepath

class ImageFile:
    def __init__ (self, file):
        self.file = file
    def open (self):
        self.image = Image.open(self.file)
        return 'ImageFile open'
    def resize (self, basewidth):
        wpercent = (basewidth / float(self.image.size[0]))
        hsize = int((float(self.image.size[1]) * float(wpercent)))
        self.image = self.image.resize((basewidth, hsize), Image.ANTIALIAS)
        return 'ImageFile resized'
    def write (self, path):
        exif = self.image.info['exif']
        self.image.save(path, exif=exif)
        return 'ImageFile writing: '+path
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

class App:
    def __init__(self, args):
        self.args = args
        self.start()
    def start(self):
        print('starting.')
        if self.args.bool_copyFromCameraToHdd:
            print('starting copy from camera to hard drive')
            for file in os.listdir(self.args.directoryCamera):
                transitingFile = TransitingFile(os.path.join(self.args.directoryCamera, file))
                directory = os.path.join(self.args.directoryHdd, transitingFile.timestring[:8])
                print transitingFile.copyTo(directory)
        if self.args.bool_copyFromHddToWebsync:
            print('starting copy from hard drive to web sync')
            for root, dirs, files in os.walk(self.args.directoryHdd):
                for file in files:
                    if file[-3:] != 'JPG': # only do jpg files
                        continue
                    YYYYMM = os.path.split(root)[-1][:6] # expecting YYYYMM
                    YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
                    directory = os.path.join(self.args.directoryWebSync, YYYYMM)
                    if not (os.path.exists(directory)):
                        print('main mkdir:'+directory)
                        os.makedirs(directory)
                    newImageFilePath = os.path.join(directory, YYYYMMDD+'_'+file)
                    if not (os.path.exists(newImageFilePath)):
                        print('copying: '+newImageFilePath)
                        existingImageFilePath = os.path.join(root, file)
                        image = ImageFile(existingImageFilePath)
                        image.open()
                        if self.args.bool_resizeWebsyncImage:
                            print image.resize(self.args.int_resize)
                        print image.write(newImageFilePath)
                        image.close()
        if self.args.bool_syncUpdatesFromHddToWebsync:
            print('starting sync hard drive to web sync')
            ImageFilePairs = []
            for root, dirs, files in os.walk(self.args.directoryHdd):
                for file in files:
                    if file[-3:] != 'JPG': # only do jpg files
                        continue
                    YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
                    ifp = ImageFilePair()
                    ifp.left = YYYYMMDD+'_'+file
                    ifp.leftfile = os.path.join(root, file)
                    ImageFilePairs.append(ifp)
            for root, dirs, files in os.walk(self.args.directoryWebSync):
                for file in files:
                    if file[-3:] != 'JPG': # only do jpg files
                        continue
                    print(file)
                    match = next((x for x in ImageFilePairs if x.left == file), None)
                    if match:
                        match.right = file
                        match.rightfile = os.path.join(root, file)
            for ifp in ImageFilePairs:
                if ifp.left and ifp.right:
                    if os.path.getmtime(ifp.leftfile) > os.path.getmtime(ifp.rightfile):
                        print('syncing: '+ifp.rightfile)
                        image = ImageFile(ifp.leftfile)
                        image.open()
                        if self.args.bool_resizeWebsyncImage:
                            print image.resize(self.args.int_resize)
                        print image.write(ifp.rightfile)
                        image.close()

class Args:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(CONFIG_FILE)
        self.directoryCamera = self.config.get('folders', 'camera')
        self.directoryHdd = self.config.get('folders', 'hdd')
        self.directoryWebSync = self.config.get('folders', 'websync')
        self.bool_copyFromCameraToHdd = self.config.getboolean('jobs','copy_camera_to_hdd')
        self.bool_copyFromHddToWebsync = self.config.getboolean('jobs','copy_hdd_to_websync')
        self.bool_syncUpdatesFromHddToWebsync = self.config.getboolean('jobs','sync_hdd_to_websync')
        self.bool_resizeWebsyncImage = self.config.getboolean('jobs','resize_websync')
        self.int_resize = self.config.getint('options','resize')

def main():
    app = App(Args())

if __name__ == '__main__':
    main()
