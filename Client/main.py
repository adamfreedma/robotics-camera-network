import client_connection
import gui
import camera
import time

connection = client_connection.Connection("127.0.0.1", 3333)
gui_object = gui.GUI()
gui_object.start()
# cam = camera.Camera(0)

objects = []

while True:
    objects = [[200, 300]]

    time.sleep(0.02)
    # for obj in objects:
    #     connection.send(obj)

    # for msg in gui_object.clickQueue:
    #     connection.send(msg)
    gui_object.clickQueue = []
