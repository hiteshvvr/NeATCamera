import sys
from PyQt4 import QtGui, QtCore
import cv2
import time


class MCamera:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)

    def getimg(self):
        self.rval, self.img = self.cam.read()
        return(self.img)
                # time.sleep(0.1)



class ControlWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.capture = None

        self.start_button = QtGui.QPushButton('Start Camera')
        self.start_button.clicked.connect(self.startCapture)
        self.quit_button = QtGui.QPushButton('End Camera')
        self.quit_button.clicked.connect(self.endCapture)
        self.end_button = QtGui.QPushButton('Stop')

        # ------ Modification ------ #
        self.capture_button = QtGui.QPushButton('Capture')
        self.capture_button.clicked.connect(self.saveCapture)
        # ------ Modification ------ #

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)

        # ------ Modification ------ #
        vbox.addWidget(self.capture_button)
        # ------ Modification ------ #

        self.setLayout(vbox)
        self.setWindowTitle('Control Panel')
        self.setGeometry(100,100,200,200)
        self.show()

    def startCapture(self):
        self.mcamera = MCamera()
        # print(self.img)
        while True:
            self.img = self.mcamera.getimg()
            cv2.imshow('Live Image', self.img)
        # if not self.capture:
        #     self.capture = QtCapture(0)
        #     self.end_button.clicked.connect(self.capture.stop)
        #     # self.capture.setFPS(1)
        #     self.capture.setParent(self)
        #     self.capture.setWindowFlags(QtCore.Qt.Tool)
        # self.capture.start()
        # self.capture.show()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

    # ------ Modification ------ #
    def saveCapture(self):
        if self.capture:
            self.capture.capture()
    # ------ Modification ------ #



if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = ControlWindow()
    sys.exit(app.exec_())