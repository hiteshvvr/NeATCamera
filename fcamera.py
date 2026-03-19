import cv2
import numpy as np


class Camera:
    """
    A simple wrapper around OpenCV's VideoCapture for camera operations.
    Provides methods for initialization, frame acquisition, exposure/gain control,
    and resource cleanup.
    """

    def __init__(self, cam_num: int = 0):
        """
        Initialize the Camera object.

        Parameters
        ----------
        cam_num : int
            Index of the camera device (default is 0).
        """
        self.cam_num = cam_num
        self.cap = None
        self.frame = np.zeros((1, 1), dtype=np.uint8)
        self.first_frame = None
        self.first_shape = None
        self.shape = None

    def initialize(self) -> bool:
        """
        Initialize the camera and capture the first frame.

        Returns
        -------
        bool
            True if initialization succeeded, False otherwise.
        """
        self.cap = cv2.VideoCapture(self.cam_num)
        if not self.cap.isOpened():
            raise RuntimeError(f"Unable to open camera {self.cam_num}")

        ret, self.first_frame = self.cap.read()
        if not ret or self.first_frame is None:
            raise RuntimeError("Failed to read initial frame from camera")

        self.first_shape = self.first_frame.shape
        # print(f"Camera {self.cam_num} initialized with frame shape: {self.first_shape}")
        return True

    def get_frame(self) -> np.ndarray:
        """
        Capture a single frame from the camera.

        Returns
        -------
        np.ndarray
            The captured frame.
        """
        if self.cap is None:
            raise RuntimeError("Camera not initialized. Call initialize() first.")

        ret, self.frame = self.cap.read()
        if ret and self.frame is not None:
            self.shape = self.frame.shape
            # Ensure frame shape matches the first frame
            if np.array_equal(self.shape, self.first_shape):
                return self.frame

        # Fallback to first frame if capture fails
        return self.first_frame

    def acquire_movie(self, num_frames: int = 10) -> list[np.ndarray]:
        """
        Capture a sequence of frames.

        Parameters
        ----------
        num_frames : int
            Number of frames to capture.

        Returns
        -------
        list[np.ndarray]
            List of captured frames.
        """
        return [self.get_frame() for _ in range(num_frames)]

    def set_exposure(self, value: float) -> None:
        """Set camera exposure (mapped to brightness in OpenCV)."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def get_exposure(self) -> float:
        """Get current camera exposure (mapped to brightness in OpenCV)."""
        if self.cap:
            return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        return -1.0

    def set_gain(self, value: float) -> None:
        """Set camera gain."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_GAIN, value)

    def get_gain(self) -> float:
        """Get current camera gain."""
        if self.cap:
            return self.cap.get(cv2.CAP_PROP_GAIN)
        return -1.0

    def release(self) -> None:
        """Release the camera resource."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def __str__(self) -> str:
        return f"OpenCV Camera {self.cam_num}"


if __name__ == "__main__":
    cam = Camera(0)
    try:
        print("Initializing camera...")
        cam.initialize()
        print(cam)

        frame = cam.get_frame()
        print("Captured frame shape:", frame.shape)

        cam.set_exposure(0.5)
        print("Exposure set to:", cam.get_exposure())

        cam.set_gain(1.0)
        print("Gain set to:", cam.get_gain())

        movie = cam.acquire_movie(5)
        print("Captured movie with", len(movie), "frames")

    finally:
        cam.release()
        print("Camera released.")
