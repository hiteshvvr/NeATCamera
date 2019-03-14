#Libraries
from pyueye import ueye
import numpy as np
import cv2
import sys
import sys
from PyQt4 import QtGui, QtCore
import cv2

from numpy import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import time

class QtCapture(QtGui.QWidget):
    def __init__(self, *args):
        super(QtGui.QWidget, self).__init__()

        self.fps = 24
        self.cap = cv2.VideoCapture(*args)

        self.video_frame = QtGui.QLabel()
        lay = QtGui.QVBoxLayout()
        lay.setMargin(0)
        lay.addWidget(self.video_frame)
        self.setLayout(lay)

        # ------ Modification ------ #
        self.isCapturing = False
        self.ith_frame = 1
        # ------ Modification ------ #

    def setFPS(self, fps):
        self.fps = fps

    def nextFrameSlot(self):
        ret, frame = self.cap.read()

        # ------ Modification ------ #
        # Save images if isCapturing
        if self.isCapturing:
            cv2.imwrite('img_%05d.jpg'%self.ith_frame, frame)
            self.ith_frame += 1
        # ------ Modification ------ #
        array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
        # bytes_per_pixel = int(nBitsPerPixel / 8)
        # ...reshape it in an numpy array...
        frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
        # ...resize the image by a half
        # frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5)

        # My webcam yields frames in BGR format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

    def stop(self):
        self.timer.stop()
        ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
        ueye.is_ExitCamera(hCam)

    # ------ Modification ------ #
    def capture(self):
        if not self.isCapturing:
            self.isCapturing = True
        else:
            self.isCapturing = False
    # ------ Modification ------ #

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()


class ControlWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.capture = None

        self.start_button = QtGui.QPushButton('Start')
        self.start_button.clicked.connect(self.startCapture)
        self.quit_button = QtGui.QPushButton('End')
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
        if not self.capture:
            self.capture = QtCapture(0)
            self.end_button.clicked.connect(self.capture.stop)
            # self.capture.setFPS(1)
            self.capture.setParent(self)
            self.capture.setWindowFlags(QtCore.Qt.Tool)
        self.capture.start()
        self.capture.show()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

    # ------ Modification ------ #
    def saveCapture(self):
        if self.capture:
            self.capture.capture()
    # ------ Modification ------ #

if __name__ == '__main__':
    #Variables
    hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
    sInfo = ueye.SENSORINFO()
    cInfo = ueye.CAMINFO()
    pcImageMemory = ueye.c_mem_p()
    MemID = ueye.int()
    rectAOI = ueye.IS_RECT()
    pitch = ueye.INT()
    nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
    channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
    m_nColorMode = ueye.INT()       # Y8/RGB16/RGB24/REG32
    bytes_per_pixel = int(nBitsPerPixel / 8)
    #---------------------------------------------------------------------------------------------------------------------------------------
    print("START")
    print()
    
    
    # Starts the driver and establishes the connection to the camera
    nRet = ueye.is_InitCamera(hCam, None)
    if nRet != ueye.IS_SUCCESS:
        print("is_InitCamera ERROR")
    
    # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
    nRet = ueye.is_GetCameraInfo(hCam, cInfo)
    if nRet != ueye.IS_SUCCESS:
        print("is_GetCameraInfo ERROR")
    
    # You can query additional information about the sensor type used in the camera
    nRet = ueye.is_GetSensorInfo(hCam, sInfo)
    if nRet != ueye.IS_SUCCESS:
        print("is_GetSensorInfo ERROR")
    
    nRet = ueye.is_ResetToDefault( hCam)
    if nRet != ueye.IS_SUCCESS:
        print("is_ResetToDefault ERROR")
    
    # Set display mode to DIB
    nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)
    
    # Set the right color mode
    if int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
        # setup the color depth to the current windows setting
        ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_BAYER: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()
    
    elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
        # for color camera models use RGB32 mode
        m_nColorMode = ueye.IS_CM_BGRA8_PACKED
        nBitsPerPixel = ueye.INT(32)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_CBYCRY: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()
    
    elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
        # for color camera models use RGB32 mode
        m_nColorMode = ueye.IS_CM_MONO8
        nBitsPerPixel = ueye.INT(8)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_MONOCHROME: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()
    
    else:
        # for monochrome camera models use Y8 mode
        m_nColorMode = ueye.IS_CM_MONO8
        nBitsPerPixel = ueye.INT(8)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("else")
    
    # Can be used to set the size and position of an "area of interest"(AOI) within an image
    nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
    if nRet != ueye.IS_SUCCESS:
        print("is_AOI ERROR")
    
    width = rectAOI.s32Width
    height = rectAOI.s32Height
    
    # Prints out some information about the camera and the sensor
    print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
    print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
    print("Maximum image width:\t", width)
    print("Maximum image height:\t", height)
    print()
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
    nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
    if nRet != ueye.IS_SUCCESS:
        print("is_AllocImageMem ERROR")
    else:
        # Makes the specified image memory the active memory
        nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
        if nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            nRet = ueye.is_SetColorMode(hCam, m_nColorMode)
    
    
    
    # Activates the camera's live video mode (free run mode)
    nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
    if nRet != ueye.IS_SUCCESS:
        print("is_CaptureVideo ERROR")
    
    # Enables the queue mode for existing image memory sequences
    nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
    if nRet != ueye.IS_SUCCESS:
        print("is_InquireImageMem ERROR")
    else:
        print("Press q to leave the programm")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    # Continuous image display
    # while(nRet == ueye.IS_SUCCESS):
    
    #     # In order to display the image in an OpenCV window we need to...
    #     # ...extract the data of our image memory
    #     array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
    
    #     # bytes_per_pixel = int(nBitsPerPixel / 8)
    
    #     # ...reshape it in an numpy array...
    #     frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
    
    #     # ...resize the image by a half
    #     frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5)
        
    # #---------------------------------------------------------------------------------------------------------------------------------------
    #     #Include image data processing here
    
    # #---------------------------------------------------------------------------------------------------------------------------------------
    
    #     #...and finally display it
    #     cv2.imshow("SimpleLive_Python_uEye_OpenCV", frame)
    
    #     # Press q if you want to end the loop
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    # Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management

    
    # Disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera

    
    print()
    print("END")

    app = QtGui.QApplication(sys.argv)
    window = ControlWindow()
    win = pg.GraphicsWindow(title="Sum Signal") # creates a window
    p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
    curve = p.plot()                        # create an empty "plot" (a curve to plot)

    windowWidth = 500                       # width of the window displaying the curve
    Xm = linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
    ptr = -windowWidth                      # set first x position

    # Realtime data plot. Each time this function is called, the data display is updated
    def update():
        global curve, ptr, Xm    
        Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
        # value = ser.readline()                # read line (single value) from the serial port
        # value = random.randint(1,101)                # read line (single value) from the serial port
        array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
        value = np.sum(array)
        Xm[-1] = float(value)                 # vector containing the instantaneous values      
        ptr += 1                              # update x position for displaying the curve
        curve.setData(Xm)                     # set the curve with this data
        curve.setPos(ptr,0)                   # set x position in the graph to 0
        QtGui.QApplication.processEvents()    # you MUST process the plot now

    ### MAIN PROGRAM #####    
    # this is a brutal infinite loop calling your realtime data plot
    while True: 
        # time.sleep(0.1)
        update()



    sys.exit(app.exec_())
    ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
    ueye.is_ExitCamera(hCam)
    
    # Destroys the OpenCv windows
    cv2.destroyAllWindows()




