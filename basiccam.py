import cv2
from time import sleep

def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    ret_val, img = cam.read()
    print(img.shape)
    while True:
        sleep(0.1)
        ret_val, img = cam.read()
        # if mirror:
        #     img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    show_webcam(mirror=False)


if __name__ == '__main__':
    main()