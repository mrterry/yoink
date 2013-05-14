from __future__ import division

from trace import equispaced_colormaping

from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

import numpy as np


class DragableCmap(object):
    """
    Fake colormap-like image take from the end points of a DeformableLine
    """
    def __init__(self, ax, line, source):
        self.created = False
        self.ax = ax
        self.line = line
        self.source = source
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
        self.l, self.rgb = equispaced_colormaping(x0, y0, x1, y1, self.source)

        n, ncol = self.rgb.shape
        self.im.set_data(self.rgb.reshape((n, 1, ncol)))

    def make_cmap(self, name, **kwargs):
        assert None not in (self.l, self.rgb)
        seq = [(x, col) for x, col in zip(self.l, self.rgb)]
        return LinearSegmentedColormap.from_list(name, seq, **kwargs)


class DeformableLine(object):
    """
    Segemented line with movable vertexes
    """
    def __init__(self, ax, is_closed=False, max_points=None):
        self.ax = ax
        self.canvas = self.ax.figure.canvas

        self.xs = []
        self.ys = []
        self.line = Line2D(self.xs, self.ys)
        self.ax.add_artist(self.line)

        self.circles = []

        self.is_closed = is_closed
        self.max_points = max_points 

        self.callbacks = []
        self.moving_ci = None
        self.connected = False

    def connect(self):
        self.press_cid = self.canvas.mpl_connect(
                'button_press_event', self.on_press)
        self.release_cid = self.canvas.mpl_connect(
                'button_release_event', self.on_release)
        self.motion_cid = self.canvas.mpl_connect(
                'motion_notify_event', self.on_motion)
        self.connected = True

    def disconnect(self):
        self.canvas.mpl_disconnect(self.press_cid)
        self.canvas.mpl_disconnect(self.release_cid)
        self.canvas.mpl_disconnect(self.motion_cid)

        self.press_cid = None
        self.release_cid = None
        self.motion_cid = None
        self.connected = False

    def draw(self):
        for f in self.callbacks:
            f()
        self.canvas.draw()

    def on_press(self, event):
        ci = self.get_circle_index(event)
        if ci is None:
            return
        circle = self.circles[ci]
        x0, y0 = circle.center
        self.moving_ci = x0, y0, event.xdata, event.ydata, ci

    def on_motion(self, event):
        if self.moving_ci is None:
            return
        xc, yc, xclick, yclick, ci = self.moving_ci

        x, y = xc + (event.xdata-xclick), yc + (event.ydata-yclick)
        self.circles[ci].center = (x, y)

        self.xs[ci], self.ys[ci] = x, y
        if self.is_closed and len(self.circles) == self.max_points and ci == 0:
            self.xs[-1], self.ys[-1] = x, y
        self.line.set_data(self.xs, self.ys)

        self.draw()

    def on_release(self, event):
        if self.moving_ci:
            self.moving_ci = None
            self.draw()

    def get_circle_index(self, event):
        i = 0
        for i, c in enumerate(self.circles):
            if c.contains(event)[0]:
                return i
        if len(self.circles) == self.max_points:
            return None

        # new circle
        i = len(self.circles)
        x, y = event.xdata, event.ydata
        circle = Circle((x, y), radius=5, alpha=0.5)
        self.circles.append(circle)
        self.ax.add_artist(circle)

        self.xs.append(x)
        self.ys.append(y)
        # finish square if adding last corner
        if self.is_closed and len(self.circles) == self.max_points:
            self.xs.append(self.xs[0])
            self.ys.append(self.ys[0])
        self.line.set_data(self.xs, self.ys)

        self.draw()
        return i
