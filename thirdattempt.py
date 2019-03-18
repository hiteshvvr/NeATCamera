import tkinter
import tkinter.messagebox
import cv2
import sys

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from numpy import *

import time


class MCamera:

    def __init__(self):
        self.roi = [0,0,0,0]
        self.cam = cv2.VideoCapture(0)
    def getimg(self):
        self.rval, self.img = self.cam.read()
        return(self.img)

mcamera = MCamera()

def show_webcam(mirror=False):
    while True:
        img = mcamera.getimg()
        cv2.imshow('my webcam', img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()


def getroi():
    showCrosshair = False
    fromCenter = False
    img = mcamera.getimg()
    r = cv2.selectROI("Image", img, fromCenter, showCrosshair)
    # Crop image
    imCrop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    # Display cropped image
    cv2.imshow("Cropped Image", imCrop)
    cv2.waitKey(0)
    mcamera.roi = [int(r[1]),int(r[1]+r[3]),int(r[0]),int(r[0]+r[2])]
    print(mcamera.roi)


app = QtGui.QApplication(sys.argv)
win = pg.GraphicsWindow(title="Sum Signal") # creates a window
p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
curve = p.plot()                        # create an empty "plot" (a curve to plot)

windowWidth = 500                       # width of the window displaying the curve
Xm = linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
ptr = -windowWidth                      # set first x position

def update():
    global curve, ptr, Xm    
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    # value = np.sum(array)
    value = 7 
    Xm[-1] = float(value)                 # vector containing the instantaneous values      
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr,0)                   # set x position in the graph to 0
    QtGui.QApplication.processEvents()    # you MUST process the plot now

def plotcontinues():
    while True:
        time.sleep(0.1)
        update()
    sys.exit(app.exec_())




top = tkinter.Tk()
def helloCallBack():
   tkinter.messagebox.showinfo( "Hello Python", "Hello World")



c = tkinter.Button(top, text ="Start Camera", command = show_webcam)

B = tkinter.Button(top, text ="Get ROI", command = getroi)

a = tkinter.Button(top, text ="Continuous Plot", command = plotcontinues)

B.pack()
c.pack()
a.pack()
top.mainloop()


# cv2.destroyAllWindows()

