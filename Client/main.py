import client_connection
import gui
import camera
import time
import detector

connection = client_connection.Connection("127.0.0.1", 3333)
detector = detector.Detector("detector.weights", "detector.cfg", True, ((0, 0, 1.5), (0, 30, 0)), 0)

objects = [[50, 50]]
while True:

    time.sleep(0.02)
    for obj in objects:
        connection.send(obj)

    if detector.locations_queue.qsize():
        result = detector.locations_queue.get()[0]
        if len(objects):
            objects[0] = result
        else:
            objects.append(result)
    else:
        objects = []
    detector.results_queue.empty()
