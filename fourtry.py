# -*- coding: utf-8 -*-
"""
Shows use of PlotWidget to display panning data

"""
# import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import cv2

pg.setConfigOption('background', 'w')
cam = cv2.VideoCapture(0)
ret, frame = cam.read()

win = pg.GraphicsWindow()
win.setWindowTitle('Intensity')
plt = win.addPlot()


iwin = pg.ImageWindow()
iwin.setWindowTitle('Image')
iwin.resize(800,800)
img = pg.ImageItem()
img.setImage(frame)

# win.show()


#plt.setAutoVisibleOnly(y=True)
pen1 = pg.mkPen('r', width=2, style=QtCore.Qt.DashLine)          ## Make a dashed yellow line 2px wide
pen2 = pg.mkPen(color=(000, 000, 255), style=QtCore.Qt.DotLine)  ## Dotted pale-blue line
curve = plt.plot(pen=pen1)
icurve = plt.plot()




data = []
count = 0
def update():
    global data, curve, count
    
    data.append(np.random.normal(size=10) + np.sin(count * 0.1) * 5)
    if len(data) > 100:
        data.pop(0)
    curve.setData(np.hstack(data))
    count += 1

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
