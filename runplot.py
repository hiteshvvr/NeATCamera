# -*- coding: utf-8 -*-
"""
Shows use of PlotWidget to display panning data

"""
# import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

pg.setConfigOption('background', 'w')


win = pg.GraphicsWindow()
win.setWindowTitle('pyqtgraph example: PanningPlot')

plt = win.addPlot()
#plt.setAutoVisibleOnly(y=True)
pen1 = pg.mkPen('g', width=2, style=QtCore.Qt.DashLine)          ## Make a dashed yellow line 2px wide
pen2 = pg.mkPen(color=(000, 000, 255), style=QtCore.Qt.DotLine)  ## Dotted pale-blue line
curve = plt.plot(pen=pen1)


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
