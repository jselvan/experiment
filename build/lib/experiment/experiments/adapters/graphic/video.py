from typing import Optional, Sequence
from os import PathLike

from PIL import Image

from experiment.util.bbox import T_BBOX_SPEC
from experiment.experiments.adapters.graphic.image import ImageAdapter

class VideoAdapter(ImageAdapter):
    def __init__(self,
        video: PathLike[bytes],
        position: Sequence[float],
        size: Sequence[float],
        orientation: float=0,
        bbox: Optional[T_BBOX_SPEC]=None
    ):
        self.video = video
        self.frame = 0
        self.get_frame()
        super().__init__(
            image=self.image, 
            position=position, 
            size=size, 
            orientation=orientation, 
            bbox=bbox
        )
    def get_frame(self):
        self.image = self.video.get_frame(self.frame)
    def update(self, tick, events):
        state = super().update(tick, events)
        if state:
            # update video frame
            frame = self.elapsed // self.fps
            if frame > self.nframes:
                if self.loop:
                    frame = frame % self.nframes
                else:
                    return False
            if frame != self.frame:
                self.frame = frame
                self.get_frame()
        return state
    def reset(self):
        super().reset()
        self.frame = 0
        self.get_frame()