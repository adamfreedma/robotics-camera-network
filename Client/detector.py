import time
import cv2
import camera
import queue
import threading
import math
import numpy as np
from typing import Tuple


class Detector:

    CONFIG_THRESHOLD = 0.2
    NMS_THRESHOLD = 0.01
    OBJECT_HEIGHT = 0.12
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720

    def __init__(self, weights: str, config: str, show: bool, location: Tuple[Tuple[float, float, float],
                                                                             Tuple[float, float, float]], path=0, fov=60):
        """
        :param weights: path the the .weights file of the DNN
        :param config: path the the .cfg file of the DNN
        :param show: show the output image with bounding boxes over the detections
        :param location: camera location [[x, y, z], [yaw, pitch, roll]] in degrees
        :param path: camera path, defaults to 0
        """

        self.show = show

        self.net = cv2.dnn_DetectionModel(config, weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
        self.net.setInputSize(416,416)
        self.net.setInputScale(1 / 255)
        self.net.setInputSwapRB(True)
        self.results_queue = queue.Queue()
        self.locations_queue = queue.Queue()

        self.camera = camera.Camera(path)
        self.fov = math.radians(fov)
        self.pix_in_rad = self.FRAME_WIDTH / self.fov

        self.camera_location = location[0]
        self.camera_yaw = math.radians(location[1][0])
        self.camera_pitch = math.radians(location[1][1])
        self.camera_roll = math.radians(location[1][2])

        self.detector_thread = threading.Thread(target=self.detect)
        self.detector_thread.start()

        self.calc_locations_thread = threading.Thread(target=self.calc_locations)
        self.calc_locations_thread.start()

    @staticmethod
    def _project_between_planes(theta: float, angle_between_planes: float):
        """
        project's theta between 2 planes
        :param theta: the angle to project
        :param angle_between_planes: the angle between the planes to project with (positive to decrease theta, negative to increase)
        :return: the projected angle
        """
        if angle_between_planes >= 0:
            return math.atan(math.tan(theta)/ math.cos(angle_between_planes))
        if angle_between_planes < 0:
            return math.atan(math.tan(theta) / math.cos(angle_between_planes))

    @staticmethod
    def rotate(vector: Tuple[float, float], yaw: float, degrees=False) -> list:
        # converting angle units

        if degrees:
            yaw = math.radians(yaw)

        rotation_matrix = [[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]]
        return np.dot(vector, rotation_matrix)

    def calc_locations(self):

        while True:
            if not self.results_queue.qsize():
                time.sleep(0.02)

                bounding_boxes = self.results_queue.get()

                locations = []

                for bounding_box in bounding_boxes:
                    class_id = bounding_box[0]
                    left, top, width, height = bounding_box[1:]

                    object_y = top + height / 2
                    object_x = left + width / 2

                    object_y_offset_pix = object_y - self.FRAME_HEIGHT / 2
                    object_x_offset_pix = object_x - self.FRAME_WIDTH / 2

                    object_y_offset_rad = object_y_offset_pix / self.pix_in_rad
                    object_x_offset_rad = object_x_offset_pix / self.pix_in_rad

                    pitch = self.camera_pitch + object_y_offset_rad
                    floor_yaw = self._project_between_planes(object_x_offset_rad, -abs(pitch))

                    height_diff = self.camera_location[2] - self.OBJECT_HEIGHT
                    distance = math.tan(pitch) * height_diff
                    x_position = distance * math.cos(floor_yaw)
                    y_position = distance * math.sin(floor_yaw)

                    # TODO - rotate by yaw and add camera location

                    x_position, y_position = self.rotate((x_position, y_position), self.camera_yaw)
                    x_position += self.camera_location[0]
                    y_position += self.camera_location[1]

                    locations.append((x_position, y_position))

                self.locations_queue.put(locations)

    def detect(self):
        """detecets objects in the given frame

            puts list(tuple(int, int, int, int, int)): (class id, left, top, width, height) into results queue
        """

        while True:
            if not self.camera.frames_queue.qsize():
                time.sleep(0.02)

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
