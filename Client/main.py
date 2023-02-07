import client_connection
import camera
import time

connection = client_connection.Connection("127.0.0.1", 3333)
# cam = camera.Camera(0)

objects = []

while True:
    objects = [[200, 300]]

    time.sleep(0.02)
    for obj in objects:
        connection.send(obj)
