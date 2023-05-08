import client_connection
import camera
import time
import detector

connection = client_connection.Connection("192.168.4.91", 3333)
while not connection.accepted:
    time.sleep(0.05)
detector = detector.Detector("detector.weights", "detector.cfg", True, connection.location, 0)

objects = []
while True:

    time.sleep(0.02)

    # adds detected objects to the queue
    if detector.locations_queue.qsize():
        for result in detector.locations_queue.get():
            objects.append(result)
    else:
        objects = []
    detector.results_queue.empty()

    # sends detected objects
    for obj in objects:
        connection.send(obj)

