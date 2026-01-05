class CameraManager:
    def __init__(self):
        self.capture = None
        self.recording_enabled = False
        self._frame_ready = threading.Condition()
        self._last_frame = None
        self._camera_thread = None
    def close(self):
        raise NotImplementedError("close method not implemented")

import cv2
import threading
class CV2CameraManager(CameraManager):
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index

    def record_frame(self, frame):
        # Placeholder for recording logic
        pass

    def start_camera(self):
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            raise RuntimeError(f"Cannot open camera with index {self.camera_index}")

    def get_frame(self):
        if self.capture is None:
            raise RuntimeError("Camera has not been started.")
        ret, frame = self.capture.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera.")
        # Notify any waiting thread that a new frame is ready
        with self._frame_ready:
            self._last_frame = frame.copy()
            self._frame_ready.notify_all()
        return frame

    def stop_camera(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
    
    # have a thread which runs the camera and saves frames when recording is enabled
    def camera_thread(self):
        while self.capture is not None:
            self.get_frame()
            if self.recording_enabled:
                self.record_frame(self._last_frame)
            # fix to a framerate of 30 fps
            cv2.waitKey(33)
    
    def start_capturing(self):
        self.start_camera()
        # self.recording_enabled = True
        self._camera_thread = threading.Thread(target=self.camera_thread)
        self._camera_thread.start()
    
    def stop_capturing(self):
        # self.recording_enabled = False
        self.stop_camera()
        if self._camera_thread is not None:
            self._camera_thread.join()

    def close(self):
        self.stop_capturing()
