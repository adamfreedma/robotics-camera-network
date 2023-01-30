import client_connection
import camera
import time

connection = client_connection.Connection("127.0.0.1", 3333)
# cam = camera.Camera(0)

time.sleep(0.5)
connection.send([888, 300])
time.sleep(20)
