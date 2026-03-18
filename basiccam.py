"""
Webcam Viewer Script
--------------------
Displays video from the default webcam.
Press ESC to exit.
"""

import cv2


def show_webcam(mirror: bool = False) -> None:
    """
    Display webcam feed in a window.

    Parameters
    ----------
    mirror : bool, optional
        If True, the webcam feed will be mirrored horizontally.
    """
    # cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW for Windows, improves stability
    # cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        raise RuntimeError("Could not open webcam.")

    try:
        while True:
            ret_val, frame = cam.read()
            if not ret_val or frame is None:
                print("Failed to capture frame.")
                break

            if mirror:
                frame = cv2.flip(frame, 1)

            cv2.imshow("Webcam Feed", frame)

            # ESC key to quit
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()


def main() -> None:
    """Main entry point of the script."""
    show_webcam(mirror=False)


if __name__ == "__main__":
    main()
