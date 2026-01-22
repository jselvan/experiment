from flask import Flask, send_file, request, jsonify, render_template
import threading
import io
import base64
from typing import Dict, Optional
from PIL import Image, ImageDraw
from flask_socketio import SocketIO

from experiment.renderers.base import Renderer
from experiment.events.base import EventManager, Event
from experiment.util.colours import parse_colour


class FlaskRenderer(Renderer):
    """Renderer that draws onto a PIL image buffer and exposes frames over HTTP.

    Methods mirror the renderer interface used elsewhere: draw_rect, draw_circle,
    draw_image, clear, flip, get_subject_screen, set_background.
    """

    def __init__(self, size=(800, 600), background=(155, 155, 155), socketio: Optional[SocketIO] = None):
        self.size = tuple(size)
        self.default_background = parse_colour(background)
        self.background = self.default_background

        self._frame_ready = threading.Condition()
        self._last_frame_bytes: Optional[bytes] = None

        # Backing canvas and draw object
        self._canvas = Image.new("RGB", self.size, self.background)
        self._draw = ImageDraw.Draw(self._canvas)
        # Optional SocketIO instance to broadcast frames
        self._socketio = socketio

    def initialize(self):
        # No special initialization required for this renderer
        return None

    def draw_rect(self, adapter):
        # adapter.rect is expected to be (x, y, w, h) or box-like
        x, y, w, h = adapter.rect
        box = (x, y, x + w, y + h)
        self._draw.rectangle(box, fill=adapter.colour)

    def draw_circle(self, adapter):
        # adapter.position (x, y) and adapter.size is radius
        x, y = adapter.position
        r = adapter.size
        box = (x - r, y - r, x + r, y + r)
        self._draw.ellipse(box, fill=adapter.colour)

    def draw_image(self, adapter):
        # adapter.image is expected to be a PIL.Image-like object
        image = adapter.image
        if hasattr(image, "convert"):
            image = image.convert("RGB")
        image = image.resize(adapter.size)
        self._canvas.paste(image, adapter.top_left)

    def clear(self):
        self._draw.rectangle((0, 0, self.size[0], self.size[1]), fill=self.background)

    def set_background(self, colour: Optional[str | tuple] = None):
        if colour is None:
            colour = self.default_background
        self.background = parse_colour(colour)
        self.clear()
        self.flip()

    def set_socketio(self, socketio: SocketIO):
        """Attach a SocketIO instance so `flip()` can broadcast frames."""
        self._socketio = socketio

    def flip(self):
        # Convert current canvas to bytes (PNG) and notify waiting threads
        with self._frame_ready:
            bio = io.BytesIO()
            # Use PNG for lossless frames
            self._canvas.save(bio, format="PNG")
            self._last_frame_bytes = bio.getvalue()
            self._frame_ready.notify_all()
            # If a SocketIO instance is attached, emit the frame as base64
            if self._socketio is not None:
                try:
                    b64 = base64.b64encode(self._last_frame_bytes).decode("ascii")
                    # emit binary as base64 string under event 'frame'
                    self._socketio.emit("frame", {"png_base64": b64}, broadcast=True)
                except Exception:
                    # Fail silently; socket might be shutting down
                    pass

    def get_subject_screen(self) -> Optional[bytes]:
        # Return the last flipped frame bytes
        with self._frame_ready:
            if self._last_frame_bytes is None:
                # If no flipped frame yet, create one from current canvas
                bio = io.BytesIO()
                self._canvas.save(bio, format="PNG")
                return bio.getvalue()
            return self._last_frame_bytes


class FlaskEventManager(EventManager):
    """Simple event manager that accepts events from HTTP POSTs and
    returns them in `get_events()`.
    """

    def __init__(self, manager):
        super().__init__(manager)
        self._queue: list[dict] = []
        self._lock = threading.Lock()

    def post_event(self, event: dict):
        with self._lock:
            print(event)
            self._queue.append(event)

    def get_events(self):
        with self._lock:
            events = list(self._queue)
            self._queue.clear()
        # If the project expects Event instances, convert minimally
        converted = []
        for e in events:
            if isinstance(e, Event):
                converted.append(e)
            else:
                converted.append(e)
        return converted

from experiment.manager import Manager
class FlaskManager(Manager):
    def __init__(self, **kwargs):
        config = kwargs.pop("config", {})
        render_settings = config.get("renderer", {})
        host = render_settings.get("host", "0.0.0.0")
        port = render_settings.get("port", 1450)

        display_settings = config.get("display", {})
        size = display_settings.get("size", (800, 600))
        background = config.get("background", (155, 155, 155))

        renderer = FlaskRenderer(
            size=size,
            background=background,
        )
        eventmanager = FlaskEventManager(manager=self)
        super().__init__(config=config, renderer=renderer, eventmanager=eventmanager, **kwargs)
        self.host = host
        self.port = port
        assert isinstance(self.renderer, FlaskRenderer)

        # Create Flask app + SocketIO
        self.app = Flask(__name__, static_folder=None, template_folder="templates")
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Attach socketio to renderer so it can broadcast frames on flip()
        try:
            self.renderer.set_socketio(self.socketio)
        except Exception:
            # Renderer may not support socketio; ignore
            pass

        @self.app.route("/")
        def index():
            return render_template('index.html')

        @self.app.route("/frame")
        def frame():
            frame_bytes = self.renderer.get_subject_screen()
            if frame_bytes is None:
                return "", 204
            return send_file(io.BytesIO(frame_bytes), mimetype="image/png")

        @self.app.route("/set_background", methods=["POST"])
        def set_background():
            data = request.get_json(silent=True) or {}
            colour = data.get("colour")
            self.renderer.set_background(colour)
            return jsonify({"status": "ok"})

        @self.app.route("/event", methods=["POST"])
        def receive_event():
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "no json"}), 400
            # Accept event dicts and forward to EventManager
            self.eventmanager.post_event(data)
            return jsonify({"status": "ok"})

        # SocketIO handlers
        @self.socketio.on("connect")
        def _on_connect():
            # Optionally send initial frame on connect
            try:
                frame_bytes = self.renderer.get_subject_screen()
                if frame_bytes:
                    b64 = base64.b64encode(frame_bytes).decode("ascii")
                    self.socketio.emit("frame", {"png_base64": b64})
            except Exception:
                pass

        @self.socketio.on("request_frame")
        def _on_request_frame():
            frame_bytes = self.renderer.get_subject_screen()
            if frame_bytes:
                b64 = base64.b64encode(frame_bytes).decode("ascii")
                self.socketio.emit("frame", {"png_base64": b64})

        @self.socketio.on("event")
        def _on_event(data):
            # forward socket events into the EventManager
            try:
                self.eventmanager.post_event(data)
            except Exception:
                pass

        @self.socketio.on("set_background")
        def _on_set_background(data):
            colour = None
            if isinstance(data, dict):
                colour = data.get("colour")
            else:
                colour = data
            try:
                self.renderer.set_background(colour)
            except Exception:
                pass

        self._thread: Optional[threading.Thread] = None

    def start(self, use_reloader: bool = False):
        # Run Flask in a background thread. Use threaded mode so multiple
        # requests can be served.
        def run():
            # Use SocketIO's runner so websocket endpoints work
            self.socketio.run(self.app, host=self.host, port=self.port, debug=True, use_reloader=use_reloader)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        import webbrowser
        webbrowser.open(f'http://{self.host}:{self.port}/', new=2)

    def cleanup(self):
        # Stop Flask server if running
        if self._thread and self._thread.is_alive():
            # Stopping Flask cleanly is non-trivial; for now we just let the thread die on program exit
            pass
        super().cleanup()

from typing import Any, Dict
from experiment.trial import Trial, TrialResult
from experiment.experiments.adapters import RectAdapter, TimeCounter, TouchAdapter
from experiment.experiments.scene import Scene
class TestTrial(Trial):
    def __init__(self):
        super().__init__()
        self.duration = 5.0  # seconds
    def run(self, mgr):
        positions = [(200, 150), (400, 300), (600, 450)]
        rects = [
            RectAdapter(
                position=pos,
                size=[50, 50],
                colour=(0, 255, 0)
            ) for pos in positions
        ]
        tcs = [
            TimeCounter(duration=self.duration, children=[rect]) for rect in rects
        ]
        scenes = [
            Scene(mgr, tc) for tc in tcs
        ]
        ta = TouchAdapter(10, {'a': rects[0]})
        for scene in scenes:
            scene.run()
        Scene(mgr, ta).run()
        return TrialResult(continue_session=True, outcome="completed", data={"duration": self.duration})
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Trial:
        return cls()

if __name__ == "__main__":
    # Simple test of the FlaskManager
    import time

    mgr = FlaskManager()
    print("Starting Flask server...")
    mgr.start()
    print(f"Flask server running at http://{mgr.host}:{mgr.port}/")

    from experiment.blockmanager import BlockManager
    bm = BlockManager(
        config={
            'blocks': {
                1: {'length': 20, 'conditions': [1]}
            },
            'conditions': {1: {'trial_type': 'TestTrial'}}
        },
        trials={'TestTrial': TestTrial}
    )
    mgr.run_session(bm)