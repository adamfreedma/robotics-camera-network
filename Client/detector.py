import time
import cv2
import camera
import queue
import threading


class Detector:

    def __init__(self, weights, config, show, path=0):
        """init the detector

        Args:
            weights (str): the path to the .weights file
            config (str): the path to the .cfg file
        """
        self.CONFIG_THRESHOLD = 0.2
        self.NMS_THRESHOLD = 0.01
        self.show = show

        self.net = cv2.dnn_DetectionModel(config, weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
        self.net.setInputSize(416,416)
        self.net.setInputScale(1 / 255)
        self.net.setInputSwapRB(True)
        self.results_queue = queue.Queue()

        self.camera = camera.Camera(path)

        self.detector_thread = threading.Thread(target=self.detect)
        self.detector_thread.start()

    def detect(self):
        """detecets objects in the given frame

        Args:
            frame: the tested image

        Returns:
            list(tuple(int, int, int, int, int)): (class id, left, top, width, height)
        """

        while True:
            if not self.camera.frames_queue.qsize():
                time.sleep(0.05)

            frame = self.camera.frames_queue.get()

            classes, confidences, boxes = self.net.detect(frame, confThreshold=self.CONFIG_THRESHOLD, nmsThreshold=self.NMS_THRESHOLD)

            results = []

            if len(classes):
                # appends the detection to the list
                for classID, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                    if confidence > 0.5:
                        left, top, width, height = box
                        results.append((classID, left, top, width, height))

                # showing the results in a seperate window
                if self.show:
                    for classID, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                        if confidence > 0.5:
                            label = '%.2f' % confidence
                            label = '%s: %s' % (classID, label)
                            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                            left, top, width, height = box
                            top = max(top, label_size[1])
                            cv2.rectangle(frame, box, color=(0,255,0), thickness=3)
                            cv2.rectangle(frame, (left, top - label_size[1]), (left + label_size[0], top + baseline), (255,255,255), cv2.FILLED)
                            cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))
            if self.show:
                cv2.imshow("show", frame)

                cv2.waitKey(1)
            if len(results):
                self.results_queue.put(results)
