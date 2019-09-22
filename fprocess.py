import numpy as np

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QCheckBox
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QApplication, QSlider
from PyQt5.QtWidgets import QLineEdit, QInputDialog, QLabel, QStyleFactory
from PyQt5 import *
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

from pyqtgraph import ImageView
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore, QtGui
import cv2
from datetime import datetime


class StartWindow(QMainWindow):

    def __init__(self, camera=None):
        super().__init__()
        # Main Window Widget
        pg.setConfigOption('background', 'w')
        self.central_widget = QWidget()
        self.aimwig = QWidget()
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        # self.changePalette()
        
        # parameters
        self.framerate = 50
        self.roi = [195, 148, 224, 216]
        self.datalen = 150
        self.movingpt = 50
        self.exp = 50
        self.gain = 50
        self.level = None
        self.lock = True
        self.avgval = 44
        self.roi_flag = False

        # Camera
        self.camera = camera

        # First Horizon row Widgets
        self.button_start = QPushButton("Start/Stop")
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")
        self.button_start.setCheckable(True)
        self.button_reset= QPushButton('Reset/Update')
        self.button_save= QPushButton('SaveData')
        # Second Horizontal row Widgets
        self.button_locklevel= QPushButton("LockLevel")
        self.button_locklevel.setCheckable(True)

        self.value_locklevel= QLineEdit(str(self.level))
        self.value_locklevel.textChanged.connect(self.update_parameters)

        self.label_framerate = QLabel("FRate(millisec)")
        self.value_framerate = QLineEdit(str(self.framerate))
        self.value_framerate.textChanged.connect(self.update_parameters)

        self.label_movingpt = QLabel("MovingPoints")
        self.value_movingpt = QLineEdit(str(self.movingpt))
        self.value_movingpt.textChanged.connect(self.update_parameters)

        self.label_roi = QLabel("ROI")
        self.value_roi = QLineEdit(str(self.roi)[1:-1])
        self.value_roi.setFixedWidth(200)
        self.value_roi.textChanged.connect(self.change_reset_col)

        self.label_datalen = QLabel("Length")
        self.value_datalen = QLineEdit(str(self.datalen))
        self.value_datalen.textChanged.connect(self.update_parameters)

        self.cbox_raw= QCheckBox("RawCurve")
        self.cbox_raw.setChecked(True)

        self.label_avgval = QLabel("AvgVal: " + str(format(int(self.avgval),"010d")))
        self.label_avgval.setStyleSheet("border: 1px solid black");

        # Bottom slider Widgets
        self.label_eslider= QLabel("Exposure: " + str(self.exp))
        self.slider_eslider = QSlider(Qt.Horizontal)
        self.slider_eslider.setRange(0, 100)
        self.camera.set_exposure(self.exp)
        self.slider_eslider.setValue(self.exp)
        self.label_gslider= QLabel("Gain" + str(self.gain) )
        self.slider_gslider = QSlider(Qt.Horizontal)
        self.slider_gslider.setRange(0, 100)
        self.slider_gslider.setValue(self.gain)


        # Image View Widgets
        self.image_view = ImageView(self.aimwig)
        self.roi_view = ImageView()
        # self.roi = pg.CircleROI([80, 50], [20, 20], pen=(4,9))
        # self.image_view.addItem(self.roi)
        # Intensity Graph Widget
        self.gwin = pg.GraphicsWindow()
        self.rplt = self.gwin.addPlot()

        self.pen1 = pg.mkPen('r', width=2)
        self.pen2 = pg.mkPen(color=(255, 15, 15),width=2)
        self.pen3 = pg.mkPen(color=(000, 155, 115), style=QtCore.Qt.DotLine)
        self.curve = self.rplt.plot(pen=self.pen3)
        self.curve2 = self.rplt.plot(pen=self.pen2)
        self.rplt.showGrid(x=True, y=True)
        self.data = []
        self.avg_data = []
        self.count = 0

        # Layouts
        self.mainlayout = QVBoxLayout(self.central_widget)
        self.btn1layout = QHBoxLayout()
        self.btn2layout = QHBoxLayout()
        self.img1layout = QHBoxLayout()
        self.sld1layout = QHBoxLayout()


        self.btn1layout.addWidget(self.button_start)
        self.btn1layout.addWidget(self.button_reset)
        self.btn1layout.addWidget(self.button_save)
        self.btn2layout.addWidget(self.button_locklevel)
        self.btn2layout.addWidget(self.value_locklevel)
        self.btn2layout.addWidget(self.label_framerate)
        self.btn2layout.addWidget(self.value_framerate)
        self.btn2layout.addWidget(self.label_datalen)
        self.btn2layout.addWidget(self.value_datalen)
        self.btn2layout.addWidget(self.label_movingpt)
        self.btn2layout.addWidget(self.value_movingpt)
        self.btn2layout.addWidget(self.label_roi)
        self.btn2layout.addWidget(self.value_roi)
        self.btn2layout.addWidget(self.cbox_raw)
        self.btn2layout.addWidget(self.label_avgval)

        self.img1layout.addWidget(self.image_view)
        self.img1layout.addWidget(self.roi_view)

        self.sld1layout.addWidget(self.label_eslider)
        self.sld1layout.addWidget(self.slider_eslider)
        self.sld1layout.addWidget(self.label_gslider)
        self.sld1layout.addWidget(self.slider_gslider)

        self.mainlayout.addLayout(self.btn1layout)
        self.mainlayout.addLayout(self.btn2layout)
        self.mainlayout.addLayout(self.img1layout)
        self.mainlayout.addLayout(self.sld1layout)

        self.mainlayout.addWidget(self.gwin)
        self.setCentralWidget(self.central_widget)

        # Functionality
        self.button_start.clicked.connect(self.update_image)
        self.button_start.clicked.connect(self.change_start_col)
        self.button_reset.clicked.connect(self.reset_run)
        self.button_locklevel.clicked.connect(self.locklevel)
        self.button_save.clicked.connect(self.save_parameters)
        self.slider_eslider.valueChanged.connect(self.update_exposure)
        self.slider_gslider.valueChanged.connect(self.update_gain)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.update_timer.timeout.connect(self.update_plot)

        ## SETTING UP FIRST IMAGE
        self.first_frame = self.camera.get_frame()
        self.update_image()
        self.first_roi = self.getroiimage()

    def change_reset_col(self):
        self.button_reset.setStyleSheet("background-color:rgb(252,42,71)")
        self.roi_flag = True

    def change_start_col(self):
        if self.button_start.isChecked():
            self.button_start.setStyleSheet("default")
        if self.button_start.isChecked() is False:
            self.button_start.setStyleSheet("background-color:rgb(252,42,71)")

    def update_image(self):
        self.frame = self.camera.get_frame()
        self.roi_img = self.getroiimage()
        if(np.sum(self.roi_img)>100):
            self.roi_view.setImage(self.roi_img.T, autoLevels=self.lock, levels=self.level)
            self.image_view.setImage(self.frame.T, autoLevels=self.lock, levels=self.level)
        if self.button_start.isChecked():
            self.update_timer.start(self.framerate)
        if self.button_start.isChecked() is False:
            self.update_timer.stop()

    def locklevel(self):
        if self.button_locklevel.isChecked():
            self.level = self.image_view.quickMinMax(self.frame)
            self.lock = False
        if self.button_locklevel.isChecked() is False:
            self.level = None
            self.lock = True 

    def reset_run(self):
        if self.roi_flag == False:
            self.data=[]
            self.avg_data=[]
            self.curve.clear()
            self.curve2.clear()
        if self.roi_flag == True:
            self.update_parameters()
            self.roi_flag = False

    def getroiimage(self):
        # r = [195, 148, 224, 216]
        r = self.roi
        r = np.array(r)
        self.roi_img = self.frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        return self.roi_img

    def update_exposure(self, value):
        self.exp = value
        self.button_start.setChecked(False)
        self.camera.set_exposure(self.exp)
        self.label_eslider.setText("Exposure:  "+str(self.exp))
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")

    def update_gain(self, value):
        self.gain = value
        self.button_start.setChecked(False)
        self.camera.set_gain(self.gain)
        self.label_gslider.setText("Gain:  "+str(self.gain))
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")

    def moving_average(self):
        a = np.array(self.data)
        tsum = np.cumsum(a, dtype=float)
        tsum[self.movingpt:] = tsum[self.movingpt:] - tsum[:-self.movingpt]
        tsum = tsum[self.movingpt - 1:] / self.movingpt
        return tsum

    def update_plot(self):
        mlen = self.datalen
        self.data.append(np.sum(self.roi_img))
        if len(self.data) > self.datalen:
            self.data.pop(0)
        if len(self.data) > self.movingpt + 5:
            mdata = self.moving_average()
            mlen = len(mdata)
            self.curve2.setData(mdata)
        if self.cbox_raw.isChecked():
            self.curve.setData(np.hstack(self.data[-mlen:]))
        else:
            self.curve.clear()
        if len(self.data) > 21:
            self.avgval = np.average(self.data[-20:])
            self.label_avgval.setText("AvgVal: " + str(format(int(self.avgval),"010d")))


    def update_parameters(self):
        if self.value_framerate.text().isdigit():
            self.framerate = int(self.value_framerate.text())
        if self.value_datalen.text().isdigit():
            self.datalen = int(self.value_datalen.text())
            if(self.datalen < len(self.data)):
                self.reset_run()
        if self.value_movingpt.text().isdigit():
            self.movingpt= int(self.value_movingpt.text())
        templevel = self.value_locklevel.text().split(sep=",")
        if (len(templevel) == 2):
            self.level= tuple([int(float(i)) for i in templevel])
            print(self.level)
        del templevel
        temproi = self.value_roi.text().split(sep=",")
        if (len(temproi) == 4):
            self.roi = [int(float(i)) for i in temproi]
        del temproi
        print("hitesh")
        self.button_reset.setStyleSheet("default")

    # def save_parameters(self):
    #     tfile = open("./log.txt", "a+")
    #     tfile.write("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    #     tfile.write("\nDateTime:: ")
    #     tfile.write(str(datetime.now()))
    #     tfile.write("\nROI:: ")
    #     tfile.write(str(self.roi))
    #     tfile.write("\nExposure:: ")
    #     tfile.write(str(self.exp))
    #     tfile.write("\nGain:: ")
    #     tfile.write(str(self.gain))
    #     tfile.write("\n")
    #     tfile.write("Intensity:: ")
    #     tfile.write(str(np.sum(self.roi_img)))
    #     tfile.write("\n")
    #     tfile.write("\nLevel:: ")
    #     tfile.write(str(self.level))
    #     tfile.write("\n")
    #     np.sum(self.roi_img)
    #     timestamp = datetime.timestamp(datetime.now()) 
    #     filename = "camimg" + str(timestamp) + ".png"
    #     tfile.write("ImageFile:: ")
    #     tfile.write(str(filename))
    #     tfile.write("\n")
    #     cv2.imwrite(filename,self.frame[:,:,0])
    #     tfile.close()

    def save_parameters(self):
        tfile = open("./log.txt", "a+")


        timestamp = datetime.timestamp(datetime.now()) 
        filename = "camimg" + str(timestamp) + ".png"
        tfile.write("\n")
        cv2.imwrite(filename,self.frame[:,:,0])

        tfile.write("DateTime,\t\t\t\t\tROI,\t\t\t\t\tExposure,\tGain,\tIntensity(Total),\tIntensity(ROI),\tLevel,\tImagefile,\n")
        tfile.write(str(datetime.now()) + ",\t" + str(self.roi) + ",\t" + str(self.exp) + ",\t\t\t" + str(self.gain) + ",\t\t" + str(np.sum(self.frame)) + ",\t\t\t" + str(np.sum(self.roi_img)) +",\t\t\t" + str(self.image_view.quickMinMax(self.frame)) + ",\t" + str(filename))

        tfile.close()

if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())
