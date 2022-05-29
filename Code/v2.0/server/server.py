import eventlet
import socketio
from GazeTracking2.gaze_tracking import GazeTracking, GazeDetector

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('New Connection:', sid)

@sio.event
def handshake(sid, data):
    print('Handshake', data)

    direction, all_result = gaze_tracking.get_eye_direction(data['duration'])
     
    sio.emit('result', {'direction': direction})

    print("Result sent to game:", direction)

@sio.event
def disconnect(sid):
    print('Connection disconnected:', sid)

if __name__ == '__main__':
    print("Server is starting ...")
    gaze_tracking = GazeTracking(GazeDetector(), print_logs=True)
    eventlet.wsgi.server(eventlet.listen(('', 4343)), app)
