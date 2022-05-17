import eventlet
import socketio
import time
import numpy as np
from GazeTracking2.gaze_tracking import get_eye_direction

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
     
    sio.emit('result', {'direction': direction})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 4343)), app)
