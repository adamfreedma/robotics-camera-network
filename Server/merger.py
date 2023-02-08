import time
import math
import threading
from typing import List


class Merger(object):

    MAX_DISTANCE_TO_MERGE = 0.15
    TIME_TO_DELETE = 1
    MAX_OBJECT_LIST_SIZE = 10

    def __init__(self):
        # the tuple contains a [float, float, float] [x, y, time]
        self.client_object_list:  List[List[float, float, float]] = []
        self.merged_object_list: List[List[float, float, float]] = []
        # starting a thread
        self.lock = threading.Lock()
        self.run_thread = threading.Thread(target=self._run, daemon=True)
        self.run_thread.start()

    def insert_client_object(self, x: float, y: float):
        self.lock.acquire()
        self.client_object_list.append([x, y, time.time()])

        self.lock.release()

    def _run(self):
        while True:
            # self._delete_old()
            merge_list: List[List[float, float, float]] = []

            self.lock.acquire()
            self.client_object_list.extend(self.merged_object_list)

            for new_object in self.client_object_list:
                merge_with = []

                for existing_object in merge_list:
                    if _distance(existing_object, new_object) < self.MAX_DISTANCE_TO_MERGE:
                        merge_with.append(existing_object)

                if not merge_with and time.time() - new_object[2] < self.TIME_TO_DELETE:
                    # there is no one to merge with, add to the list
                    merge_list.append(new_object)
                else:
                    for existing_object in merge_with:
                        merge_list.remove(existing_object)

                    new_x = new_object[0]
                    new_y = new_object[1]
                    new_time = new_object[2]

                    for existing_object in merge_with:
                        new_x += existing_object[0]
                        new_y += existing_object[1]
                        new_time = max(new_time, new_object[2])

                    merge_count = len(merge_with) + 1
                    new_x /= merge_count
                    new_y /= merge_count
                    if time.time() - new_time < self.TIME_TO_DELETE:
                        merge_list.append([new_x, new_y, new_time])

            self.lock.release()
            self.merged_object_list = merge_list
            self.client_object_list = []


def _distance(list1, list2):
    return math.sqrt((list2[0] - list1[0]) ** 2 + (list2[1] - list1[1]) ** 2)
