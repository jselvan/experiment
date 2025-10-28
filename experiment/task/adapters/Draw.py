from experiment.task.adapters import BaseAdapter, ImageAdapter, TimeCounter

from PIL import Image, ImageDraw

class Stroke:
    def __init__(self):
        self.path = []
        self.times = []
    def add_from_event(self, event, canvas_top_left):
        x, y = event['x'], event['y']
        cl, ct = canvas_top_left
        self.path.append((x-cl, y-ct))
        self.times.append(event['time'])
    @property
    def path_length(self):
        return len(self.path)

class DrawAdapter(BaseAdapter):
    def __init__(self,
        canvas: ImageAdapter,
        time_counter: TimeCounter | float | int | None,
        pen_radius: float=10,
        pen_colour: str='BLACK',
    ):
        if canvas.bbox is None:
            raise ValueError("Canvas must have a bounding box")


        self.time_counter = TimeCounter.new(time_counter)
        super().__init__(children=[canvas, self.time_counter])
        self.canvas = canvas
        self.canvas_backup = canvas.image.copy()

        self.state = 'init'
        self.pen_radius = pen_radius
        self.pen_colour = pen_colour
        self.strokes = []
        self.last_stroke = None
        self.stroke_history = []

    def draw_point(self, point):
        x, y = point
        draw = ImageDraw.Draw(self.canvas.image)
        draw.ellipse(
            (x-self.pen_radius, y-self.pen_radius, x+self.pen_radius, y+self.pen_radius),
            fill=self.pen_colour
        )
        return self.canvas.image

    def draw(self, path):
        draw = ImageDraw.Draw(self.canvas.image)
        draw.line(
            path,
            fill=self.pen_colour,
            width=int(self.pen_radius*2),
            joint='curve'
        )
        return self.canvas.image

    def render(self, renderer):
        super().render(renderer)
        self.canvas.image = self.canvas_backup.copy()
        for stroke in self.strokes:
            if stroke.path_length > 0:
                self.draw(stroke.path)
        if self.last_stroke is not None and self.last_stroke.path_length > 0:
            self.draw(self.last_stroke.path)

    def update(self, tick, events):
        super().update(tick, events)
        if not self.time_counter.active:
            self.state = 'elapsed'
            self.active = False
            return self.active
        
        # look for any touch or drag events
        draw_event = any(
            event['type'] in ['mouse_down', 'mouse_drag'] 
            for event in events
        )
        if not draw_event:
            return self.active
        
        strokes = []
        if self.last_stroke is None:
            stroke = self.last_stroke = Stroke()
        else:
            stroke = self.last_stroke
        # get the canvas top left corner
        cl, ct = self.canvas.top_left
        for event in events:
            if event['type'] == 'mouse_down':
                if stroke.path_length > 0:
                    strokes.append(stroke)
                    stroke = Stroke()
                if self.canvas.bbox.detect_touch(self.canvas, [event]):
                    stroke.add_from_event(event, (cl, ct))
            elif event['type'] == 'mouse_drag':
                x, y = event['x'], event['y']
                if self.canvas.bbox.detect_touch(self.canvas, [event]):
                    stroke.add_from_event(event, (cl, ct))
                else:
                    if stroke.path_length > 0:
                        strokes.append(stroke)
                        stroke = Stroke()
        
        if strokes:
            self.strokes.extend(strokes)
        self.last_stroke = stroke
        return self.active

    def reset(self):
        super().reset()
        self.canvas.image = self.canvas_backup
        if self.last_stroke is not None:
            self.strokes.append(self.last_stroke)
            self.last_stroke = None
        self.stroke_history.append(self.strokes)
        self.strokes = []
        self.time_counter.reset()
        self.state = 'init'