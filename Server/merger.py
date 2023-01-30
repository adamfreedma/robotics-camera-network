import socket
import time
import numpy as np
import math
import threading
from typing import List, Dict, Tuple


class Merger(object):

    MAX_DISTANCE_TO_MERGE = 0.15
    TIME_TO_DELETE = 10

    def __init__(self):
        # the tuple contains a [float, float, float] [x, y, time]
        self.client_object_list:  Dict[socket.socket, List[Tuple[float, float, float]]] = {}
        self.merged_object_list: List[Tuple[float, float]] = []
        # starting a thread
        self.run_thread = threading.Thread(target=self._run, daemon=True)
        self.run_thread.start()

    def insert_client_object(self, client_socket: socket.socket, x: float, y: float):
        if client_socket in self.client_object_list.keys():
            self.client_object_list[client_socket].append((x, y, time.time()))
        else:
            self.client_object_list[client_socket] = [(x, y, time.time())]

    def _delete_old(self):

        for client_socket in list(self.client_object_list):
            np_object_list = np.array(self.client_object_list[client_socket])
            if len(np_object_list):
                self.client_object_list[client_socket] = np_object_list[np.where((time.time() - np_object_list[0][2]) < self.TIME_TO_DELETE)]

    def _run(self):
        while True:
            self._delete_old()
            merge_list = []

            for object_list in self.client_object_list.values():
                for new_object in object_list:
                    is_object_new = True

                    for existing_object in merge_list:
                        if is_object_new and _distance(existing_object, new_object) < self.MAX_DISTANCE_TO_MERGE:
                            is_object_new = False

                    if is_object_new:
                        merge_list.append(new_object)

            self.merged_object_list = merge_list


def _distance(list1, list2):
    return math.sqrt((list2[0] - list1[0]) ** 2 + (list2[1] - list1[1]) ** 2)