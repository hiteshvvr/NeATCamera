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
        # Camera
        self.camera = camera
        self.frame = self.camera.get_frame()
        self.roi_img = self.frame
        # First Horizon row Widgets
        self.button_start = QPushButton("Start/Stop")
        self.button_start.setCheckable(True)
        self.button_reset= QPushButton('Reset')
        self.button_save= QPushButton('SaveData')
        # Second Horizontal row Widgets
        self.button_update = QPushButton("Update")
        self.label_framerate = QLabel("FRate\n(in millisec)")
        self.label_movingpt = QLabel("MovingPoints")
        self.label_roi = QLabel("ROI")
        self.label_datalen = QLabel("Length")
        self.cbox_raw= QCheckBox("ShowRawData")


        self.value_framerate = QLineEdit("100")
        self.value_movingpt = QLineEdit("10")
        self.value_roi = QLineEdit("195, 148, 224, 216")
        self.value_datalen = QLineEdit("100")
        self.cbox_raw.setChecked(True)


        # parameters
        self.framerate = 100
        self.roi = [195, 148, 224, 216]
        self.datalen = 100
        self.movingpt = 10

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

        # Slider Widget // Not used now
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 10)

        # Layouts
        self.mlayout = QVBoxLayout(self.central_widget)
        self.blayout = QHBoxLayout()
        self.dlayout = QHBoxLayout()
        self.ilayout = QHBoxLayout()

        self.blayout.addWidget(self.button_start)
        self.blayout.addWidget(self.button_reset)
        self.blayout.addWidget(self.button_save)
        self.dlayout.addWidget(self.button_update)
        self.dlayout.addWidget(self.label_framerate)
        self.dlayout.addWidget(self.value_framerate)
        self.dlayout.addWidget(self.label_datalen)
        self.dlayout.addWidget(self.value_datalen)
        self.dlayout.addWidget(self.label_movingpt)
        self.dlayout.addWidget(self.value_movingpt)
        self.dlayout.addWidget(self.label_roi)
        self.dlayout.addWidget(self.value_roi)
        self.dlayout.addWidget(self.cbox_raw)

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
        self.button_reset.clicked.connect(self.reset_run)
        self.button_update.clicked.connect(self.update_parameters)
        self.button_save.clicked.connect(self.save_parameters)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.update_timer.timeout.connect(self.update_roi)
        self.update_timer.timeout.connect(self.update_plot)

    def update_image(self):
        self.frame = self.camera.get_frame()
        self.image_view.setImage(self.frame.T)
        if self.button_start.isChecked():
            self.update_timer.start(self.framerate)
        if self.button_start.isChecked() is False:
            self.update_timer.stop()


    def reset_run(self):
        self.data=[]
        self.avg_data=[]
        # self.rplt.clear()
        self.curve.clear()
        self.curve2.clear()

    def update_roi(self):
        self.frame = self.camera.get_frame()
        # r = [195, 148, 224, 216]
        r = self.roi
        r = np.array(r)
        self.roi_img = self.frame[int(r[1]):int(
            r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        self.roi_view.setImage(self.roi_img.T)

    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def moving_average(self):
        a = np.array(self.data)
        tsum = np.cumsum(a, dtype=float)
        tsum[self.movingpt:] = tsum[self.movingpt:] - tsum[:-self.movingpt]
        tsum = tsum[self.movingpt - 1:] / self.movingpt
        # e=len(a)-len(tsum)
        # tsum = np.insert(tsum, 0, tsum[:e])
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

    def update_parameters(self):
        if self.value_framerate.text().isdigit():
            self.framerate = int(self.value_framerate.text())
        if self.value_datalen.text().isdigit():
            self.datalen = int(self.value_datalen.text())
        if self.value_movingpt.text().isdigit():
            self.movingpt= int(self.value_movingpt.text())
        temproi = self.value_roi.text().split(sep=",")
        self.roi = list(map(int,temproi))
        del temproi

    def save_parameters(self):
        tfile = open("./log.txt", "a+")
        tfile.write("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        tfile.write("\nDateTime:: ")
        tfile.write(str(datetime.now()))
        tfile.write("\nROI:: ")
        tfile.write(str(self.roi))
        tfile.write("\n")
        options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Enter Image Name","./ImageFiles/","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)
            cv2.imwrite(fileName,self.frame)
            tfile.write("ImageFile:: ")
            tfile.write(str(fileName))
            tfile.write("\n")
            tfile.close()

if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())
