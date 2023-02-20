import client_connection
import gui
import camera
import time

connection = client_connection.Connection("127.0.0.1", 3333)
gui_object = gui.GUI()
gui_object.start()
# cam = camera.Camera(0)

objects = []

objects = [[50, 50]]
while True:

    time.sleep(0.02)
    for obj in objects:
        connection.send(obj)

    for msg in gui_object.clickQueue:
        objects[0] = [int(msg) * 10, int(msg) * 10]
    gui_object.clickQueue = []
