import numpy as np

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QApplication, QSlider
from PyQt5.QtWidgets import QLineEdit, QInputDialog, QLabel, QStyleFactory
from pyqtgraph import ImageView
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import cv2


class StartWindow(QMainWindow):
    def __init__(self, camera = None):
        super().__init__()
        # Main Window Widget
        pg.setConfigOption('background', 'w')
        self.central_widget = QWidget()
        self.aimwig = QWidget() 
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        # self.changePalette()
        # Camera
        self.camera = camera
        self.frame = self.camera.get_frame()
        self.roi_img = self.frame
        # First Horizon row Widgets
        self.button_start = QPushButton('Start')
        self.button_stop = QPushButton('Stop')
        # Second Horizontal row Widgets
        self.button_update = QPushButton("Update")
        self.rate = QLabel("Rate")
        self.Dalen = QLabel("Length")
        self.roi1 = QLabel("ROI1")
        self.roi2 = QLabel("ROI2")
        self.roi3 = QLabel("ROI3")
        self.roi4 = QLabel("ROI4")
        self.uprate = QLineEdit("100")
        self.dlen = QLineEdit()
        self.r1 = QLineEdit()
        self.r2 = QLineEdit()
        self.r3 = QLineEdit()
        self.r4 = QLineEdit()

        #parameters
        self.framerate = 100
        self.roi=[195, 148, 224, 216]
        self.datalen = 100
        self.n = 10


        # Image View Widgets
        self.image_view = ImageView(self.aimwig)
        self.roi_view = ImageView()
        # self.roi = pg.CircleROI([80, 50], [20, 20], pen=(4,9))
            # self.image_view.addItem(self.roi)
        # Intensity Graph Widget
        self.gwin = pg.GraphicsWindow()
        self.rplt = self.gwin.addPlot()
        self.pen1 = pg.mkPen('r', width=2)          ## Make a dashed yellow line 2px wide
        self.pen3 = pg.mkPen('g', width=2)          ## Make a dashed yellow line 2px wide
        self.pen2 = pg.mkPen(color=(000, 000, 255), style=QtCore.Qt.DotLine)  ## Dotted pale-blue line
        self.curve = self.rplt.plot(pen=self.pen1)
        self.curve2 = self.rplt.plot(pen=self.pen3)
        self.rplt.showGrid(x=True,y=True)
        self.data = []
        self.avg_data = []
        self.count = 0  

        # Slider Widget // Not used now
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,10)

        # Layouts
        self.mlayout = QVBoxLayout(self.central_widget)
        self.blayout = QHBoxLayout()
        self.dlayout = QHBoxLayout()
        self.ilayout = QHBoxLayout()

        self.blayout.addWidget(self.button_start)
        self.blayout.addWidget(self.button_stop)
        self.dlayout.addWidget(self.button_update)
        self.dlayout.addWidget(self.rate)
        self.dlayout.addWidget(self.uprate)
        self.dlayout.addWidget(self.Dalen)
        self.dlayout.addWidget(self.dlen)
        self.dlayout.addWidget(self.roi1)
        self.dlayout.addWidget(self.r1)
        self.dlayout.addWidget(self.roi2)
        self.dlayout.addWidget(self.r2)
        self.dlayout.addWidget(self.roi3)
        self.dlayout.addWidget(self.r3)
        self.dlayout.addWidget(self.roi4)
        self.dlayout.addWidget(self.r4)

        self.ilayout.addWidget(self.image_view)
        self.ilayout.addWidget(self.roi_view)

        self.mlayout.addLayout(self.blayout)
        self.mlayout.addLayout(self.dlayout)
        self.mlayout.addLayout(self.ilayout)

        self.mlayout.addWidget(self.gwin)
        self.mlayout.addWidget(self.slider)
        self.setCentralWidget(self.central_widget)

        # Functionality
        self.button_start.clicked.connect(self.update_image)
        self.button_stop.clicked.connect(self.stop_run)
        self.button_update.clicked.connect(self.update_parameters)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.update_timer.timeout.connect(self.update_roi)
        self.update_timer.timeout.connect(self.update_plot)

    def update_image(self):
        self.frame = self.camera.get_frame()
        self.image_view.setImage(self.frame.T)
        self.update_timer.start(self.framerate)

    def stop_run(self):
        self.update_timer.stop()


    def update_roi(self):
        self.frame = self.camera.get_frame()
        # r = [195, 148, 224, 216]
        r = self.roi
        r = np.array(r)
        self.roi_img = self.frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        self.roi_view.setImage(self.roi_img.T)

    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def moving_average(self):
        a=np.array(self.data)
        ret = np.cumsum(a, dtype=float)
        ret[self.n:] = ret[self.n:] - ret[:-self.n]
        return ret[self.n - 1:] / self.n


    def update_plot(self):
        # global data, curve, count
        self.data.append(np.sum(self.roi_img))
        if len(self.data)>self.datalen:
            self.data.pop(0)
        if len(self.data)>20:
            self.avg_data = list(self.moving_average())
            self.curve2.setData(np.hstack(self.avg_data))
        self.curve.setData(np.hstack(self.data))
        self.count += 1

    def update_parameters(self):
        if self.uprate.text().isdigit():
            self.framerate = int(self.uprate.text())
            print(int(self.uprate.text()))
        if self.r1.text().isdigit():
            self.roi[0]= int(self.r1.text())
        if self.r2.text().isdigit():
            self.roi[1]= int(self.r2.text())
        if self.r3.text().isdigit():
            self.roi[2]= int(self.r3.text())
        if self.r4.text().isdigit():
            self.roi[3]= int(self.r4.text())
        if self.dlen.text().isdigit():
            self.datalen= int(self.dlen.text())
        
        # if self.uprate.text().isdigit():
        #     self.framerate = int(self.uprate.text())
        # if self.uprate.text().isdigit():
        #     self.framerate = int(self.uprate.text())


if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())
