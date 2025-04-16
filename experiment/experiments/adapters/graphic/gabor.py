from typing import Optional, Sequence

from PIL import Image
import numpy as np

from experiment.util.bbox import T_BBOX_SPEC
from experiment.experiments.adapters.graphic.image import ImageAdapter

class GaborAdapter(ImageAdapter):
    def __init__(self, 
        position: Sequence[int], 
        size: Sequence[int],
        lambda_: float,
        orientation: float,
        sigma: float,
        phase: float,
        trim: float=.005,
        bbox: Optional[T_BBOX_SPEC]=None,
    ):

        self.size = size
        self.lambda_ = lambda_
        self.orientation = orientation
        self.sigma = sigma
        self.phase = phase
        self.trim = trim
        image = self._compute()
        super().__init__(position=position, image=image, size=size, bbox=bbox)

    def _compute(self):
        w, h = self.size
        X0 = (np.linspace(1, w, w)/w)-.5
        Y0 = (np.linspace(1, h, h)/h)-.5
        Xm, Ym = np.meshgrid(X0, Y0)
        size = max(w, h)
        freq = size / self.lambda_
        phase = (self.phase/180)*np.pi

        theta = (self.orientation/180)*np.pi
        Xt = Xm * np.cos(theta)
        Yt = Ym * np.sin(theta)

        grating = np.sin(((Xt+Yt) * freq * 2 * np.pi) + phase)
        gauss = np.exp(-((Xm ** 2) + (Ym ** 2)) / (2 * (self.sigma / size)) ** 2)
        gauss[gauss < self.trim] = 0
        img_data = (grating * gauss + 1) / 2 * 255
        return Image.fromarray(img_data).convert('RGBA')
