from PyQt5.QtWidgets import QApplication
#from fpueyecam import Camera
from fcamera import Camera
from fprocess import StartWindow

camera = Camera(0)
camera.initialize()
camera.get_frame()

app = QApplication([])
start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())
camera.stopacquire()
