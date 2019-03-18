import numpy as np

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QApplication, QSlider
from pyqtgraph import ImageView
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import cv2


class StartWindow(QMainWindow):
    def __init__(self, camera = None):
        super().__init__()
        self.camera = camera
        self.frame = self.camera.get_frame()
        self.roi_img = self.frame
        pg.setConfigOption('background', 'w')
        self.central_widget = QWidget()
        self.aimwig = QWidget()
        self.aimwig.setFixedHeight(300)
        self.button_frame = QPushButton('Acquire Frame')
        self.button_movie = QPushButton('Start Movie')
        self.button_roi = QPushButton('Show ROI')
        self.image_view = ImageView(self.aimwig)
        self.gwin = pg.GraphicsWindow()
        self.roi_view = ImageView()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,10)
        self.roi = pg.CircleROI([80, 50], [20, 20], pen=(4,9))
        self.rplt = self.gwin.addPlot()
        self.pen1 = pg.mkPen('r', width=2)          ## Make a dashed yellow line 2px wide
        self.pen2 = pg.mkPen(color=(000, 000, 255), style=QtCore.Qt.DotLine)  ## Dotted pale-blue line
        self.curve = self.rplt.plot(pen=self.pen1)
        self.data = []
        self.count = 0  

        # self.image_view.addItem(self.roi)
        self.mlayout = QVBoxLayout(self.central_widget)
        self.blayout = QHBoxLayout()
        self.ilayout = QHBoxLayout()

        self.blayout.addWidget(self.button_frame)
        self.blayout.addWidget(self.button_movie)
        self.blayout.addWidget(self.button_roi)

        self.ilayout.addWidget(self.image_view)
        self.ilayout.addWidget(self.roi_view)

        self.mlayout.addLayout(self.blayout)
        self.mlayout.addLayout(self.ilayout)

        self.mlayout.addWidget(self.gwin)
        self.mlayout.addWidget(self.slider)
        self.setCentralWidget(self.central_widget)

        self.button_frame.clicked.connect(self.update_image)
        self.button_roi.clicked.connect(self.update_image)
        self.button_movie.clicked.connect(self.start_movie)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.update_timer.timeout.connect(self.update_roi)
        self.update_timer.timeout.connect(self.update_plot)

    def update_image(self):
        self.frame = self.camera.get_frame()
        self.image_view.setImage(self.frame.T)

    def update_movie(self):
        self.image_view.setImage(self.camera.last_frame.T)

    def update_roi(self):
        self.frame = self.camera.get_frame()
        r = [45, 96, 155, 113]
        r = np.array(r)
        self.roi_img = self.frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        # self.roi_img = self.frame[20:30, 30:40]
        self.roi_view.setImage(self.roi_img.T)
        # pass
        # im = cv2.imshow(self.frame)
        # self.roi_view.setImage(self.roi.getArrayRegion(self.frame, self.image_view))

    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def start_movie(self):
        self.movie_thread = MovieThread(self.camera)
        self.movie_thread.start()
        self.update_timer.start(30)

    def update_plot(self):
        # global data, curve, count
        self.data.append(np.sum(self.roi_img))
        if len(self.data)>300:
            self.data.pop(0)
        self.curve.setData(np.hstack(self.data))
        self.count += 1


class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        self.camera.acquire_movie(1)

if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())