from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QWidget

def button_pressed():
    print('Button Pressed')

app = QApplication([])
win = QMainWindow()
central_widget = QWidget()
button2 = QPushButton('Second Test', central_widget)
button = QPushButton('Test', central_widget)
button.setGeometry(0,50,120,40)
button.clicked.connect(button_pressed)
button2.clicked.connect(button_pressed)
win.setCentralWidget(central_widget)
win.show()
app.exit(app.exec_())