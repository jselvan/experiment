from flask import Flask, request, stream_with_context, jsonify
from flask_socketio import SocketIO
from flask import render_template, Response


import threading
import numpy as np
import cv2

from experiment.manager import Manager
from experiment.remote.base import RemoteServer

class FlaskServer(RemoteServer):
    def __init__(self, manager: Manager, show=True):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.manager = manager
        self.app.route('/')(self.index)
        self.app.route('/screen')(self.screen)
        self.app.route('/behaviour_summary')(self.behaviour_summary)

        self.socketio.on_event('command', self.handle_command)
        self.show = show

    def handle_command(self, data):
        command = data.get('action')
        print(f"Received command: {command}")
        if command == "goodmonkey":
            self.manager.eventmanager.post_event({
                'do': 'reward',
                'type': 'remote',
            })
        elif command == "quit":
            self.manager.eventmanager.post_event({
                'do': 'quit',
                'type': 'remote',
            })

    def generate_stream(self):
        while True:
            with self.manager.renderer._frame_ready:
                self.manager.renderer._frame_ready.wait(timeout=1.0)

                frame = self.manager.renderer.get_subject_screen()
            
            # Transpose and convert to BGR
            frame = np.transpose(frame, (1, 0, 2))
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            success, jpeg = cv2.imencode('.jpg', frame)
            if success:
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    def behaviour_summary(self):
        if self.manager.datastore is not None:
            return jsonify(self.manager.datastore.get_summary())
        else:
            return jsonify({})

    def screen(self):
        return Response(stream_with_context(self.generate_stream()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    def index(self):
        return render_template('base/index.html')
    
    def run(self):
        # self.app.run(host="0.0.0.0", port=5000)
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    def start(self):
        self.flask_thread = threading.Thread(target=self.run, daemon=True)
        self.flask_thread.start()
        if self.show:
            import webbrowser
            webbrowser.open('http://127.0.0.1:5000', new=2)
        # self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    def stop(self):
        self.socketio.stop()
        self.flask_thread.join()
