#!/usr/bin/python -i
# -*- coding: utf-8 -*-
## Add path to library (just for examples; you do not need this)
# import initExample


from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import cv2



class Camera:
    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.last_frame = np.zeros((1,1))

    def initialize(self):
        self.cap = cv2.VideoCapture(self.cam_num)

    def get_frame(self):
        ret, self.last_frame = self.cap.read()
        return self.last_frame

    def acquire_movie(self, num_frames):
        movie = []
        for _ in range(num_frames):
            movie.append(self.get_frame())
        return movie

    def set_brightness(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def get_brightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)

    def close_camera(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)

pg.setConfigOptions(imageAxisOrder='row-major')
pg.setConfigOption('background', 'w')

## create GUI
app = QtGui.QApplication([])

w = pg.GraphicsWindow(size=(800,800), border=True)
v = w.addViewBox(colspan=2)
v.invertY(True)  ## Images usually have their Y-axis pointing downward
v.setAspectLocked(True)



cam = Camera(0)
cam.initialize()
frame = cam.get_frame()
## Create image items, add to scene and set position 
im1 = pg.ImageItem(frame)
v.addItem(im1)

# v.addItem(im2)
# im2.moveBy(110, 20)
v.setRange(QtCore.QRectF(0, 0, 200, 120))
im1.scale(0.8, 0.5)

im3 = pg.ImageItem()
v2 = w.addViewBox(1,0)
v2.addItem(im3)
v2.setRange(QtCore.QRectF(0, 0, 60, 60))
v2.invertY(True)
v2.setAspectLocked(True)
#im3.moveBy(0, 130)
im3.setZValue(10)

im4 = pg.ImageItem()
v3 = w.addViewBox(1,1)
v3.addItem(im4)
v3.setRange(QtCore.QRectF(0, 0, 60, 60))
v3.invertY(True)
v3.setAspectLocked(True)
#im4.moveBy(110, 130)
im4.setZValue(10)

## create the plot
pi1 = w.addPlot(2,0, colspan=2)
#pi1 = pg.PlotItem()
#s.addItem(pi1)
#pi1.scale(0.5, 0.5)
#pi1.setGeometry(0, 170, 300, 100)

lastRoi = None

def updateRoi(roi):
    global im1, im2, im3, im4, lastRoi
    if roi is None:
        return
    lastRoi = roi
    arr1 = roi.getArrayRegion(im1.image, img=im1)
    im3.setImage(arr1)
    # arr2 = roi.getArrayRegion(im2.image, img=im2)
    # im4.setImage(arr2)
    updateRoiPlot(roi, arr1)
    
def updateRoiPlot(roi, data=None):
    if data is None:
        data = roi.getArrayRegion(im1.image, img=im1)
    if data is not None:
        roi.curve.setData(data.mean(axis=1))


## Create a variety of different ROI types
rois = []
# rois.append(pg.TestROI([0,  0], [20, 20], maxBounds=QtCore.QRectF(-10, -10, 230, 140), pen=(0,9)))
# rois.append(pg.LineROI([0,  0], [20, 20], width=5, pen=(1,9)))
# rois.append(pg.MultiLineROI([[0, 50], [50, 60], [60, 30]], width=5, pen=(2,9)))
# rois.append(pg.EllipseROI([110, 10], [30, 20], pen=(3,9)))
rois.append(pg.CircleROI([110, 50], [20, 20], pen=(4,9)))
# rois.append(pg.PolygonROI([[2,0], [2.1,0], [2,.1]], pen=(5,9)))
#rois.append(SpiralROI([20,30], [1,1], pen=mkPen(0)))

## Add each ROI to the scene and link its data to a plot curve with the same color
for r in rois:
    v.addItem(r)
    c = pi1.plot(pen=r.pen)
    r.curve = c
    r.sigRegionChanged.connect(updateRoi)

def updateImage():
    global im1, lastRoi
    frame = cam.get_frame()
    # r = abs(np.random.normal(loc=0, scale=(arr.max()-arr.min())*0.1, size=arr.shape))
    im1.updateImage(frame)
    updateRoi(lastRoi)
    for r in rois:
        updateRoiPlot(r)
    
## Rapidly update one of the images with random noise    
t = QtCore.QTimer()
t.timeout.connect(updateImage)
t.start(50)



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
