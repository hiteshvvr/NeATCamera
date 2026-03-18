import cv2

for i in range(5):
    cam = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
    if cam.isOpened():
        print(f"Camera {i} opened successfully.")
        cam.release()
    else:
        print(f"Camera {i} not available.")
