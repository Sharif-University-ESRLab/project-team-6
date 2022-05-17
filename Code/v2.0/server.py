import eventlet
import socketio
import time
import numpy as np


sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def handshake(sid, data):
    print('handshake', data)
    time.sleep(data['duration'])
    sio.emit('result', {'direction': np.random.choice(['LEFT', 'RIGHT'])})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 4343)), app)
