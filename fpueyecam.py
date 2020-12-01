from pyueye import ueye
import numpy as np


class Camera:

    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.frame = np.zeros((1, 1))

    def initialize(self):
        self.hcam = ueye.HIDS(self.cam_num)
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(24)  # 8 bit for monochrome 24 for color
        self.channels = 1  # 3: for color mode(RGB); 1 channel for monochrome
        self.m_nColorMode = ueye.INT(8)      # Y8/RGB16/RGB24/REG32
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)

        self.ret = ueye.is_InitCamera(self.hcam, None)
        if self.ret != ueye.IS_SUCCESS:
            print("is_InitCamera ERROR")

        self.setAOI()
        self.setmemory()
        self.acquireimage()

        # self.setAOI(0,0, 1280, 1024)

    # def setAOI(self, x, y, width, height):
    def setAOI(self):
        self.ret = ueye.is_AOI(
            self.hcam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        if self.ret != ueye.IS_SUCCESS:
            print("is_AOI ERROR")
        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height

    def setmemory(self):
        self.ret = ueye.is_AllocImageMem(
            self.hcam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        if self.ret != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            self.ret = ueye.is_SetImageMem(
                self.hcam, self.pcImageMemory, self.MemID)
            if self.ret != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")
            else:
                # Set the desired color mode
                self.ret = ueye.is_SetColorMode(self.hcam, self.m_nColorMode)

    def acquireimage(self):
        self.ret = ueye.is_CaptureVideo(self.hcam, ueye.IS_DONT_WAIT)
        if self.ret != ueye.IS_SUCCESS:
            print("is Error")
        self.ret = ueye.is_InquireImageMem(
            self.hcam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.ret != ueye.IS_SUCCESS:
            print("is_InquireImageMem ERROR")
        else:
            print("Press q to leave the programm")

    def stopacquire(self):
        ueye.is_StopLiveVideo(self.hcam, ueye.IS_FORCE_VIDEO_STOP)


    def get_data(self):
        array = ueye.get_data(self.pcImageMemory, self.width,
                              self.height, self.nBitsPerPixel, self.pitch, copy=False)
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
        # ...reshape it in an numpy array...
        self.data = np.reshape(
            array, (self.height.value, self.width.value, self.bytes_per_pixel))
        return self.data

    def get_frame(self):
        self.frame = self.get_data()
        while(np.sum(self.frame) < 10):
            self.frame = self.get_data()
        return self.frame

    def acquire_movie(self, num_frames=10):
        pass

    def set_exposure(self, value):
        self.stopacquire()
        # range is 0 to 33 ms
        value = value*33/100
        self.brig = ueye.double(value)
        print(self.brig)
        self.ret = ueye.is_Exposure(self.hcam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, self.brig, 8)
        if self.ret == ueye.IS_SUCCESS:
            print(' aa tried to changed exposure time to      %8.3f ms' % self.brig)
        self.acquireimage()
        
    def get_exposure(self):
        self.ret = ueye.is_Exposure(self.hcam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, self.brig, 8)
        if self.ret == ueye.IS_SUCCESS:
            print('  currently set exposure time            %8.3f ms' % self.brig)
        return self.brig

    def set_gain(self,value):
        value = int(value)
        ueye.is_SetHardwareGain(self.hcam, value, 1,1,1)


    def close_camera(self):
        pass

    def __str__(self):
        # pass
        return 'OpenCV Camera {}'.format(self.cam_num)
