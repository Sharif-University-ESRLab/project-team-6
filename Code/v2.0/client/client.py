import eventlet
import socketio
from datetime import datetime
import time
import settings
import sys
import signal


sio = socketio.Client()


@sio.event
def connect():
    print("Connected")

@sio.event
def result(data):
    log_text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Direction: {data['direction']}\n"
    with open('directions.log', 'a') as f:
        f.write(log_text)
    print(log_text, end='')

@sio.event
def disconnect():
    print("Disconnected")


def signal_handler(sig, frame):
    sio.disconnect()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

sio.connect(settings.SOCKET_SERVER)
duration = 2
wait_time = duration + 1

while True:
    sio.emit("handshake", {"duration": duration})
    time.sleep(wait_time)
    