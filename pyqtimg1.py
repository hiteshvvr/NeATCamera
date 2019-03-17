# import pyqtgraph as pg
# imv = pg.ImageView()
# imv.show()
# # imv.setImage(data)
import sys
import cv2
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
app = QtGui.QApplication(sys.argv)
cam = cv2.VideoCapture(0)
ret_val, im = cam.read()
pg.image(im)
sys.exit(app.exec_())
