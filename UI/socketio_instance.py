# UI/socketio_instance.py
import socketio

# Single global socket client for the entire app
sio = socketio.Client(reconnection=True)
SOCKET_URL = "http://127.0.0.1:5001"
