import eventlet
import socketio
import time
import numpy as np
from GazeTracking.tracker import get_eye_direction

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def handshake(sid, data):
    print('handshake', data)
    # time.sleep(data['duration'])
    direction, all_result = get_eye_direction(data['duration'])

    d = "" 
    if direction == "Looking left":
        d = 'LEFT'
    elif direction == "Looking right" or direction == "Looking center":
        d = 'RIGHT'

    print("Send to Game ...", d)
    sio.emit('result', {'direction': d})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    print("Server is starting ...")
    eventlet.wsgi.server(eventlet.listen(('', 4343)), app)
