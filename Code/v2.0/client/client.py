import eventlet
import socketio
from datetime import datetime
import time
import settings


sio = socketio.Client()


@sio.event
def connect():
    print("Connected")

@sio.event
def result(data):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Direction: {data['direction']}")

@sio.event
def disconnect():
    print("Disconnected")



sio.connect(settings.SOCKET_SERVER)
duration = 2
wait_time = duration + 1

while True:
    sio.emit("handshake", {"duration": duration})
    time.sleep(wait_time)
    