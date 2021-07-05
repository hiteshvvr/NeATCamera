# from PyQt5.QtWidgets import QApplication
from fpueyecam import Camera
# from fcamera import Camera
# from fprocess import StartWindow
import cv2

camera = Camera(0)

camera.initialize()
camera.get_frame()
camera.set_exposure(90)
# camera.set_gain(60)

frame = camera.get_frame()


def show_webcam(mirror=False):
    # cam = cv2.VideoCapture(0)
    # ret_val, img = cam.read()
    img = camera.get_frame()
    print(img.shape)
    while True:
        # ret_val, img = cam.read()
        img = camera.get_frame()
        if mirror: 
            img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        if cv2.waitKey(1) == 27:
            camera.stopacquire() 
            break  # esc to quit
    cv2.destroyAllWindows()



def main():
    show_webcam(mirror=False)


if __name__ == '__main__':
    main()