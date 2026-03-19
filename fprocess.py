import sys
import numpy as np
import cv2
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QLabel,
    QSlider,
    QStyleFactory,
)
import pyqtgraph as pg
from pyqtgraph import ImageView


class StartWindow(QMainWindow):
    def __init__(self, camera=None):
        super().__init__()
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        pg.setConfigOption("background", "w")

        # Parameters
        self.framerate = 50
        self.roi = [195, 148, 224, 216]
        self.datalen = 150
        self.movingpt = 50
        self.exp = 50
        self.gain = 50
        self.level = None
        self.lock = True
        self.avgval = 44
        self.roi_flag = False

        # Camera
        self.camera = camera

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.mainlayout = QVBoxLayout(self.central_widget)

        # --- UI Setup ---
        self._setup_buttons()
        self._setup_controls()
        self._setup_image_views()
        self._setup_sliders()
        self._setup_plot()

        # --- Functionality ---
        self._connect_signals()

        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.update_timer.timeout.connect(self.update_plot)

        # Initial image setup
        if self.camera:
            self.first_frame = self.camera.get_frame()
            self.update_image()
            self.first_roi = self.getroiimage()

    # ---------------- UI Setup Methods ----------------
    def _setup_buttons(self):
        self.button_start = QPushButton("Start/Stop")
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")
        self.button_start.setCheckable(True)

        self.button_reset = QPushButton("Reset/Update")
        self.button_save = QPushButton("SaveData")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.button_start)
        btn_layout.addWidget(self.button_reset)
        btn_layout.addWidget(self.button_save)
        self.mainlayout.addLayout(btn_layout)

    def _setup_controls(self):
        self.button_locklevel = QPushButton("LockLevel")
        self.button_locklevel.setCheckable(True)

        self.value_locklevel = QLineEdit(str(self.level))
        self.value_locklevel.textChanged.connect(self.update_parameters)

        self.label_framerate = QLabel("FRate (ms)")
        self.value_framerate = QLineEdit(str(self.framerate))
        self.value_framerate.textChanged.connect(self.update_parameters)

        self.label_movingpt = QLabel("MovingPoints")
        self.value_movingpt = QLineEdit(str(self.movingpt))
        self.value_movingpt.textChanged.connect(self.update_parameters)

        self.label_roi = QLabel("ROI")
        self.value_roi = QLineEdit(str(self.roi)[1:-1])
        self.value_roi.setFixedWidth(200)
        self.value_roi.textChanged.connect(self.change_reset_col)

        self.label_datalen = QLabel("Length")
        self.value_datalen = QLineEdit(str(self.datalen))
        self.value_datalen.textChanged.connect(self.update_parameters)

        self.cbox_raw = QCheckBox("RawCurve")
        self.cbox_raw.setChecked(True)

        self.label_avgval = QLabel(f"AvgVal: {int(self.avgval):010d}")
        self.label_avgval.setStyleSheet("border: 1px solid black")

        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(self.button_locklevel)
        ctrl_layout.addWidget(self.value_locklevel)
        ctrl_layout.addWidget(self.label_framerate)
        ctrl_layout.addWidget(self.value_framerate)
        ctrl_layout.addWidget(self.label_datalen)
        ctrl_layout.addWidget(self.value_datalen)
        ctrl_layout.addWidget(self.label_movingpt)
        ctrl_layout.addWidget(self.value_movingpt)
        ctrl_layout.addWidget(self.label_roi)
        ctrl_layout.addWidget(self.value_roi)
        ctrl_layout.addWidget(self.cbox_raw)
        ctrl_layout.addWidget(self.label_avgval)

        self.mainlayout.addLayout(ctrl_layout)

    def _setup_image_views(self):
        self.image_view = ImageView()
        self.roi_view = ImageView()

        img_layout = QHBoxLayout()
        img_layout.addWidget(self.image_view)
        img_layout.addWidget(self.roi_view)
        self.mainlayout.addLayout(img_layout)

    def _setup_sliders(self):
        self.label_eslider = QLabel(f"Exposure: {self.exp}")
        self.slider_eslider = QSlider(Qt.Orientation.Horizontal)
        self.slider_eslider.setRange(0, 100)
        self.slider_eslider.setValue(self.exp)
        if self.camera:
            self.camera.set_exposure(self.exp)

        self.label_gslider = QLabel(f"Gain: {self.gain}")
        self.slider_gslider = QSlider(Qt.Orientation.Horizontal)
        self.slider_gslider.setRange(0, 100)
        self.slider_gslider.setValue(self.gain)

        sld_layout = QHBoxLayout()
        sld_layout.addWidget(self.label_eslider)
        sld_layout.addWidget(self.slider_eslider)
        sld_layout.addWidget(self.label_gslider)
        sld_layout.addWidget(self.slider_gslider)
        self.mainlayout.addLayout(sld_layout)

    def _setup_plot(self):
        self.gwin = pg.GraphicsLayoutWidget()
        self.rplt = self.gwin.addPlot()
        self.rplt.showGrid(x=True, y=True)

        self.pen1 = pg.mkPen("r", width=2)
        self.pen2 = pg.mkPen(color=(255, 15, 15), width=2)
        self.pen3 = pg.mkPen(color=(0, 155, 115), style=Qt.PenStyle.DotLine)

        self.curve = self.rplt.plot(pen=self.pen3)
        self.curve2 = self.rplt.plot(pen=self.pen2)

        self.data = []
        self.avg_data = []
        self.count = 0

        self.mainlayout.addWidget(self.gwin)

    # ---------------- Signal Connections ----------------
    def _connect_signals(self):
        self.button_start.clicked.connect(self.update_image)
        self.button_start.clicked.connect(self.change_start_col)
        self.button_reset.clicked.connect(self.reset_run)
        self.button_locklevel.clicked.connect(self.locklevel)
        self.button_save.clicked.connect(self.save_parameters)
        self.slider_eslider.valueChanged.connect(self.update_exposure)
        self.slider_gslider.valueChanged.connect(self.update_gain)

    # ---------------- Placeholder Methods ----------------
    def update_image(self) -> None:
        """
        Capture a new frame from the camera, update ROI and display images.
        Also controls the update timer based on the Start/Stop button state.
        """
        if not self.camera:
            print("No camera available to capture frames.")
            return

        # Acquire latest frame and ROI
        self.frame = self.camera.get_frame()
        self.roi_img = self.getroiimage()

        # self.image_view.setImage( self.frame.T, autoLevels=self.lock, levels=self.level)
        # Display ROI and full frame if valid
        if self.roi_img is not None and np.sum(self.roi_img) > 100:
            self.roi_view.setImage(
                self.roi_img.T,
                autoLevels=self.lock,
                levels=self.level
            )
            self.image_view.setImage( self.frame.T, autoLevels=self.lock, levels=self.level)

        # Control timer based on button state
        if self.button_start.isChecked():
            self.update_timer.start(self.framerate)
        else:
            self.update_timer.stop()


    def reset_run(self):
        pass

    def locklevel(self):
        pass

    def save_parameters(self):
        pass
    
    def moving_average(self) -> np.ndarray:
        """
        Compute moving average of collected data.

        Returns
        -------
        np.ndarray
            Array of averaged values.
        """
        a = np.array(self.data, dtype=float)
        tsum = np.cumsum(a)
        tsum[self.movingpt:] = tsum[self.movingpt:] - tsum[:-self.movingpt]
        return tsum[self.movingpt - 1:] / self.movingpt
    
    
    def update_plot(self) -> None:
        """
        Update the intensity plot with raw and averaged data.
        """
        mlen = self.datalen
        if self.roi_img is not None:
            self.data.append(np.sum(self.roi_img))
    
        if len(self.data) > self.datalen:
            self.data.pop(0)
    
        if len(self.data) > self.movingpt + 5:
            mdata = self.moving_average()
            mlen = len(mdata)
            self.curve2.setData(mdata)
    
        if self.cbox_raw.isChecked():
            self.curve.setData(np.hstack(self.data[-mlen:]))
        else:
            self.curve.clear()
    
        if len(self.data) > 21:
            self.avgval = np.average(self.data[-20:])
            self.label_avgval.setText(f"AvgVal: {int(self.avgval):010d}")
        

    def update_parameters(self):
        """Update parameters from the text fields when they change."""
        try:
            self.framerate = int(self.value_framerate.text())
        except ValueError:
            pass

        try:
            self.datalen = int(self.value_datalen.text())
        except ValueError:
            pass

        try:
            self.movingpt = int(self.value_movingpt.text())
        except ValueError:
            pass

        try:
            # ROI is expected as comma-separated values
            roi_text = self.value_roi.text()
            self.roi = [int(x.strip()) for x in roi_text.split(",")]
        except Exception:
            pass

        try:
            self.level = int(self.value_locklevel.text())
        except ValueError:
            self.level = None

    def change_reset_col(self) -> None:
        """
        Highlight the reset button and mark ROI flag as active.
        """
        self.button_reset.setStyleSheet("background-color:rgb(252,42,71)")
        self.roi_flag = True
    
    def change_start_col(self) -> None:
        """
        Update the Start button color depending on its checked state.
        """
        if self.button_start.isChecked():
            self.button_start.setStyleSheet("")  # default style
        else:
            self.button_start.setStyleSheet("background-color:rgb(252,42,71)")

    def locklevel(self) -> None:
        """
        Lock or unlock image intensity levels based on button state.
        """
        if self.button_locklevel.isChecked():
            if self.frame is not None:
                self.level = self.image_view.quickMinMax(self.frame)
            self.lock = False
        else:
            self.level = None
            self.lock = True
   
    def reset_run(self) -> None:
        """
        Reset or update the run depending on ROI flag.
        """
        if not self.roi_flag:
            self.data.clear()
            self.avg_data.clear()
            self.curve.clear()
            self.curve2.clear()
        else:
            self.update_parameters()
            self.roi_flag = False 
    
    def update_exposure(self, value: int) -> None:
        """
        Update camera exposure and refresh UI.
        """
        self.exp = value
        self.button_start.setChecked(False)
        if self.camera:
            self.camera.set_exposure(self.exp)
        self.label_eslider.setText(f"Exposure: {self.exp}")
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")


    def update_gain(self, value: int) -> None:
        """
        Update camera gain and refresh UI.
        """
        self.gain = value
        self.button_start.setChecked(False)
        if self.camera:
            self.camera.set_gain(self.gain)
        self.label_gslider.setText(f"Gain: {self.gain}")
        self.button_start.setStyleSheet("background-color:rgb(252,42,71)")

    def getroiimage(self) -> np.ndarray | None:
        """
        Extract the Region of Interest (ROI) from the current frame.

        Returns
        -------
        np.ndarray | None
            The ROI image if extraction is successful, otherwise None.
        """
        if self.frame is None:
            return None

        try:
            # ROI format: [x, y, width, height]
            x, y, w, h = map(int, self.roi)
            roi_img = self.frame[y:y + h, x:x + w]

            # Ensure ROI is not empty
            if roi_img.size == 0:
                return None

            self.roi_img = roi_img
            return self.roi_img

        except Exception as e:
            # Optional: log error if using logging module
            print(f"Error extracting ROI: {e}")
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec())
