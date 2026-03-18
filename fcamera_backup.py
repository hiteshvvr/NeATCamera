import numpy as np

import cv2


class Camera:
    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.frame = np.zeros((1,1))

    def initialize(self):
        self.cap = cv2.VideoCapture(self.cam_num)
        ret, self.first_frame = self.cap.read()
        self.first_shape = self.first_frame.shape

    def get_frame(self):
        ret, self.frame = self.cap.read()
        if self.frame is not None:
            self.shape = self.frame.shape
            if np.array_equal(self.shape,self.first_shape):
                return self.frame
        else:
            return self.first_frame

    def acquire_movie(self, num_frames=10):
        movie = []
        for _ in range(num_frames):
            movie.append(self.get_frame())
        return movie

    def set_exposure(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_gain(self, value):
        self.cap.set(cv2.CAP_PROP_GAIN, value)

    def get_exposure(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)

    def stopacquire(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)


if __name__ == '__main__':
    cam = Camera(0)
    cam.initialize()
    print(cam)
    frame = cam.get_frame()
    print(frame)
    cam.set_brightness(1)
    print(cam.get_brightness())
    cam.set_brightness(0.5)
    print(cam.get_brightness())
    cam.close_camera()