from flask import Flask, request, stream_with_context, jsonify
from jinja2 import ChoiceLoader, FileSystemLoader
from flask_socketio import SocketIO
from flask import render_template, Response

from typing import Optional
import threading
import numpy as np
import cv2

from experiment.manager import Manager
from experiment.remote.base import RemoteServer

class FlaskServer(RemoteServer):
    def __init__(self, manager: Optional[Manager]=None, show=True, template_path=None):
        self.manager: Optional[Manager] = manager
        self.show = show
        self.app = Flask(__name__, template_folder='templates/base')
        if template_path is not None:
            self.app.jinja_loader = ChoiceLoader([
                FileSystemLoader(template_path),
                self.app.jinja_loader
            ])
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.app.route('/')(self.index)
        self.app.route('/screen')(self.screen)
        self.app.route('/behaviour_summary')(self.behaviour_summary)

        self.socketio.on_event('command', self.handle_command)

    def notify_trial_end(self):
        """Emit a socket event to clients indicating trial end."""
        self.socketio.emit('trial_end', {'message': 'Trial has ended'})

    def add_manager(self, manager: Manager):
        self.manager = manager

    def handle_command(self, action):
        action['type'] = 'remote'
        if self.manager is not None and self.manager.eventmanager is not None:
            self.manager.eventmanager.post_event(action)

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
            return jsonify(self.manager.datastore.records)
        else:
            return jsonify({})

    def screen(self):
        return Response(stream_with_context(self.generate_stream()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    def index(self):
        return render_template('index.html')
    
    def run(self):
        # self.app.run(host="0.0.0.0", port=5000)
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    def start(self):
        if self.manager is None:
            raise ValueError("Manager not set for FlaskServer")
        self.flask_thread = threading.Thread(target=self.run, daemon=True)
        self.flask_thread.start()
        if self.show:
            import webbrowser
            webbrowser.open('http://127.0.0.1:5000', new=2)
        # self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    def stop(self):
        self.socketio.stop()
        self.flask_thread.join()
