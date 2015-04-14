# STANDARD PYTHON MODULES
import os, time
import shutil
import datetime
# PILLOW MODULES
from PIL import Image
import PySide
import sys

#from __future__ import (print_function, division, unicode_literals,
#                        absolute_import)

from PySide.QtCore import Slot, QMetaObject
from PySide.QtUiTools import QUiLoader
from PySide.QtGui import QApplication, QMainWindow, QMessageBox

SCRIPT_DIRECTORY = 'd:\\photospy' #os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(SCRIPT_DIRECTORY, 'photospy.ui')
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

def main2():
    query1 = False #raw_input('copy from sd card? y or n') == 'y'
    query2 = True #raw_input('copy from photos_nikon to google drive? y or n') == 'y'
    query3 = True #raw_input('sync edits from photos_nikon to google drive? y or n') == 'y'

    if query1:
        for file in os.listdir(_PATH1_):
            transitingFile = TransitingFile(os.path.join(_PATH1_, file))
            directory = os.path.join(_PATH2_, transitingFile.timestring[:8])
            transitingFile.copyTo(directory)
    if query2:
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
                newImageFilePath = os.path.join(directory, YYYYMMDD+'_'+file)
                if not (os.path.exists(newImageFilePath)):
                    # ImageFile should just open, resize & save as.
                    existingImageFilePath = os.path.join(root, file)
                    image = ImageFile(existingImageFilePath)
                    image.open()
                    image.resize(1200)
                    image.write(newImageFilePath)
                    image.close()
    if query3:
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


class UiLoader(QUiLoader):
    def __init__(self, baseinstance):
        QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.baseinstance:
            return self.baseinstance
        else:
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            if self.baseinstance:
                setattr(self.baseinstance, name, widget)
            return widget


class MainWindow(QMainWindow):
    def __init__(self, uifile, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = self.loadUi(uifile, self)
    def loadUi(self, uifile, baseinstance=None):
        loader = UiLoader(baseinstance)
        widget = loader.load(uifile)
        QMetaObject.connectSlotsByName(widget)
        return widget

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow(UI_FILE)
        self.ui = self.window.ui
        self.output = self.ui.findChild(PySide.QtGui.QPlainTextEdit, 'output')
        self.window.show()
    def outputText(self, text):
        self.output.appendPlainText(text)

def main():
    app = App()
    app.outputText('Started')
    app.app.exec_()

if __name__ == '__main__':
    main()
