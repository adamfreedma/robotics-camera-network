import client_connection
import gui
import camera
import time
import detector

connection = client_connection.Connection("127.0.0.1", 3333)
gui_object = gui.GUI()
gui_object.start()
detector = detector.Detector("detector.weights", "detector.cfg", True, ((100, 0, 1), (0, 45, 0)), "vid.mp4")


objects = [[50, 50]]
while True:

    time.sleep(0.02)
    for obj in objects:
        connection.send(obj)

    if detector.locations_queue.qsize():
        result = detector.locations_queue.get()[0]
        print(result)
        objects[0] = result
    detector.results_queue.empty()
