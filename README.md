# photospy
PhotosPy is designed to speed up one particular method of copying photos from an camera's SD card to both a storage folder and a web folder. 

The storage folder is expected to contain the originals and RAW files while the web folder is intended to be synced by some other program like google drive. PhotosPy should also perform manual syncing, so that edits made in the storage folder (such as brightness and orientation) can easily be copied to the web folder.

PhotosPy is written in python 2.7, using PySide and Pillow libraries
# dependencies
using pip we can grab the following dependancies:
```
pip install cx_freeze
pip install PySide
pip install Pillow
```
# build
using cx_freeze
```
python.exe setup.py build
```
then manually copy ui file to build folder
