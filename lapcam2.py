import cv2
import numpy as np
 
if __name__ == '__main__' :

    cam = cv2.VideoCapture(0)
    ret_val, im = cam.read()


 
    # Read image
    # im = cv2.imread("image.jpg")
     
    # Select ROI

    showCrosshair = False
    fromCenter = False
    r = cv2.selectROI("Image", im, fromCenter, showCrosshair)
    # Crop image
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
 
    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey(0)