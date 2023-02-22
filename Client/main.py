import client_connection
import gui
import camera
import time
import detector

connection = client_connection.Connection("127.0.0.1", 3333)
gui_object = gui.GUI()
gui_object.start()
detector = detector.Detector("detector.weights", "detector.cfg", True, "vid.mp4")

objects = []

objects = [[50, 50]]
while True:

    time.sleep(0.02)
    for obj in objects:
        connection.send(obj)

    if detector.results_queue.qsize():
        result = detector.results_queue.get()[0]
        print(result)
        left = result[1] / 4
        top = result[2] / 4
        objects[0] = [left, top]
    detector.results_queue.empty()
