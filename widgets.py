from trace import equispaced_colormaping

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

import numpy as np


class ActiveCmap(object):
    def __init__(self, ax, line, image):
        self.created = False
        self.ax = ax
        self.line = line
        self.image = image
        self.created = False

        self.l = None
        self.rgb = None

    def create(self):
        self.created = True

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes('right', size='5%', pad=0.5)

        rgb = np.zeros((2, 1, 4))
        self.im = cax.imshow(rgb,
                aspect='auto', origin='lower', extent=[0, 1, 0, 1])
        cax.yaxis.tick_right()
        cax.xaxis.set_visible(False)
        self.update()
    
    def creation_callback(self):
        if self.created or len(self.line.circles) != 2:
            return
        self.create()
        self.line.callbacks.append(self.update)

    def update(self):
        x0, y0 = self.line.circles[0].center
        x1, y1 = self.line.circles[1].center
        self.l, self.rgb = equispaced_colormaping(x0, y0, x1, y1, self.image)

        n, ncol = self.rgb.shape
        self.im.set_data(self.rgb.reshape((n, 1, ncol)))

    def make_cmap(self, name, **kwargs):
        assert None not in (self.l, self.rgb)
        seq = [(x, col) for x, col in zip(self.l, self.rgb)]
        return LinearSegmentedColormap.from_list(name, seq, **kwargs)
