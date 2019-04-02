from PyQt5.QtWidgets import QApplication

from fcamera import Camera
from fprocess import StartWindow

camera = Camera(0)
camera.initialize()

app = QApplication([])
start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())


############### FOR TEST##########
# while(True):

#     frame = camera.get_frame()
#     frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5)
    
#     #...and finally display it
#     cv2.imshow("SimpleLive_Python_uEye_OpenCV", frame)

#     # Press q if you want to end the loop
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
