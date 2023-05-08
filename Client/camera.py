import cv2
import threading
import queue
import time


class Camera(object):

    # capping the queue size to avoid the image processing not keeping up with the grabbing causing delay
    MAX_QUEUE_SIZE = 5

    def __init__(self, camera_port: int):
        self.camera_port = camera_port
        self.frames_queue = queue.Queue()  # queue of frames taken by the camera
        self.running = True  # should the camera capture
        self._initialize_camera()

        # starting the grabbing thread
        self.grab_thread = threading.Thread(target=self.grab_frames, daemon=True)
        self.grab_thread.start()

    def _initialize_camera(self):
        self.capture = cv2.VideoCapture(self.camera_port)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FPS, 30)

    def get_frames(self):
        """
        :return: returns the reference to the frames queue
        """
        return self.frames_queue

    def grab_frames(self):
        """
        a thread that captures frames
        :return: puts new frames into frames_queue
        """
        while self.running:
            time.sleep(0.033)
            # reading frame
            ret, frame = self.capture.read()

            if ret == 0:
                print("Error when capturing frame")
            else:
                self.frames_queue.put(frame)
            # popping frames if the queue is too big
            while self.frames_queue.qsize() > self.MAX_QUEUE_SIZE:
                self.frames_queue.get()


if __name__ == '__main__':
    # camera test
    cam = Camera(0)
    frames_queue = cam.get_frames()
    while True:
        if frames_queue.qsize():
            cv2.imshow("frame", frames_queue.get())

        cv2.waitKey(1)
