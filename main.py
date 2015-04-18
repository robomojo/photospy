# STANDARD PYTHON MODULES
import os, time
import shutil
import datetime
import sys
# PILLOW MODULES
from PIL import Image
# PYSIDE MODULES
from PySide import QtGui
from PySide import QtCore
from PySide import QtUiTools

# determine if application is ascript file or frozen exe
if getattr(sys, 'frozen', False):
    SCRIPT_DIRECTORY = os.path.dirname(sys.executable)
elif __file__:
    SCRIPT_DIRECTORY = os.path.dirname(__file__)

UI_FILE = os.path.join(SCRIPT_DIRECTORY, 'photospy.ui')

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

class UiLoader(QtUiTools.QUiLoader):
    def __init__(self, baseinstance):
        QtUiTools.QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.baseinstance:
            return self.baseinstance
        else:
            widget = QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            if self.baseinstance:
                setattr(self.baseinstance, name, widget)
            return widget

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, **kwargs):
        QtGui.QMainWindow.__init__(self, parent)
        self.myWidget = self.loadUi(kwargs['uifile'], self)
    def loadUi(self, uifile, baseinstance=None):
        loader = UiLoader(baseinstance)
        widget = loader.load(uifile)
        QtCore.QMetaObject.connectSlotsByName(widget)
        return widget

class App:
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        self.window = MainWindow(uifile=UI_FILE)
        self.ui = self.window.myWidget
        self.ui.start.clicked.connect(lambda: self.start())
        self.window.show()
    def onButtonPress(self):
        sender = self.sender()
        print sender.text()
    def outputText(self, text):
        self.ui.output.appendPlainText(text)

    def start(self):
        self.outputText('starting.')
        _PATH1_ = self.ui.cameradir.text()
        _PATH2_ = self.ui.harddrivedir.text()
        _PATH3_ = self.ui.websyncdir.text()
        self.outputText(_PATH1_)
        self.outputText(_PATH2_)
        self.outputText(_PATH3_)
        if self.ui.copy_camera_to_hdd.isChecked():
            self.outputText('starting copy from camera to hard drive')
            for file in os.listdir(_PATH1_):
                transitingFile = TransitingFile(os.path.join(_PATH1_, file))
                directory = os.path.join(_PATH2_, transitingFile.timestring[:8])
                transitingFile.copyTo(directory)
        if self.ui.copy_hdd_to_websync.isChecked():
            self.outputText('starting copy from hard drive to web sync')
            for root, dirs, files in os.walk(_PATH2_):
                for file in files:
                    if file[-3:] != 'JPG': # only do jpg files
                        continue
                    YYYYMM = os.path.split(root)[-1][:6] # expecting YYYYMM
                    YYYYMMDD = os.path.split(root)[-1][:8] # expecting YYYYMMDD
                    directory = os.path.join(_PATH3_, YYYYMM) 
                    if not (os.path.exists(directory)):
                        self.outputText('main mkdir:'+directory)
                        os.makedirs(directory)
                    newImageFilePath = os.path.join(directory, YYYYMMDD+'_'+file)
                    if not (os.path.exists(newImageFilePath)):
                        self.outputText('copying: '+newImageFilePath)
                        existingImageFilePath = os.path.join(root, file)
                        image = ImageFile(existingImageFilePath)
                        image.open()
                        image.resize(1200)
                        image.write(newImageFilePath)
                        image.close()
        if self.ui.sync_hdd_to_websync.isChecked():
            self.outputText('starting sync hard drive to web sync')
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
                    self.outputText(file)
                    match = next((x for x in ImageFilePairs if x.left == file), None)
                    if match:
                        match.right = file
                        match.rightfile = os.path.join(root, file)
            for ifp in ImageFilePairs:
                if ifp.left and ifp.right:
                    if os.path.getmtime(ifp.leftfile) > os.path.getmtime(ifp.rightfile):
                        self.outputText('syncing: '+ifp.rightfile)
                        image = ImageFile(ifp.leftfile)
                        image.open()
                        if self.ui.do_resize_for_web_sync.isChecked():
                            image.resize(self.ui.web_sync_size.value())
                        image.write(ifp.rightfile)
                        image.close()

def main():
    app = App()
    app.outputText('Started')
    app.app.exec_()

if __name__ == '__main__':
    main()
