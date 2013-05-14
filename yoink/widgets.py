from __future__ import division

import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from yoink.trace import equispaced_colormaping


class DragableCmap(object):
    """
    Fake colormap-like image taken from the end points of a DeformableLine
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


class ShutterCrop(object):
    """
    Crop an image by dragging transparent panes over excluded region.
    """
    def __init__(self, ax, facecolor='grey'):
        self.ax = ax
        self.facecolor = facecolor
        self.canvas = self.ax.figure.canvas

        self.picked = None

    def create_patches(self):
        xlo, xhi = self.ax.get_xlim()
        dx = xhi-xlo

        ylo, yhi = self.ax.get_ylim()
        dy = yhi - ylo

        pan_width = 0.05*dx
        pan_height = 0.05*dy
        kw = dict(
                facecolor=self.facecolor,
                edgecolor='none',
                picker=5,
                alpha=0.5,
                )
        self.north = Rectangle((xlo, yhi-pan_height), dx, pan_height, **kw)
        self.south = Rectangle((xlo, ylo), dx, pan_height, **kw)
        self.east = Rectangle((xhi-pan_width, ylo), pan_width, dy, **kw)
        self.west = Rectangle((xlo, ylo), pan_width, dy, **kw)
        self.ax.add_artist(self.north)
        self.ax.add_artist(self.south)
        self.ax.add_artist(self.east)
        self.ax.add_artist(self.west)

    def on_pick(self, event):
        names = ('north', 'south', 'east', 'west')
        bars = (self.north, self.south, self.east, self.west)
        for name, bar in zip(names, bars):
            if event.artist is bar:
                bounds = (
                        bar.get_x(),
                        bar.get_y(),
                        bar.get_width(),
                        bar.get_height(),
                        )
                click = (event.mouseevent.xdata, event.mouseevent.ydata)
                self.picked = (bar, click, bounds)

    def on_release(self, event):
        self.picked = None

    def on_motion(self, event):
        if self.picked is None:
            return
        bar, (xclick, yclick), (x, y, w, h) = self.picked
        
        if bar is self.south:
            new_height = h + (event.ydata-yclick)
            self.south.set_height(new_height)
        elif bar is self.west:
            new_w = w + (event.xdata-xclick)
            self.west.set_width(new_w)
        elif bar is self.north:
            dy = event.ydata - yclick
            new_h = h - dy
            new_y = y + dy
            bar.set_height(new_h)
            bar.set_y(new_y)
        elif bar is self.east:
            dx = event.xdata - xclick
            new_w = w - dx
            new_x = x + dx
            bar.set_x(new_x)
            bar.set_width(new_w)

        self.canvas.draw()

    def connect(self):
        self.picker_cid = self.canvas.mpl_connect(
                'pick_event', self.on_pick)
        self.release_cid = self.canvas.mpl_connect(
                'button_release_event', self.on_release)
        self.motion_cid = self.canvas.mpl_connect(
                'motion_notify_event', self.on_motion)
    
    def disconnect(self):
        self.canvas.mpl_disconnect(self.picker_cid)
        self.canvas.mpl_disconnect(self.release_cid)
        self.canvas.mpl_disconnect(self.motion_cid)
    
        self.picker_cid = None
        self.picker_cid = None
        self.motion_cid = None

    def get_extents(self):
        xlo = self.west.get_x() + self.west.get_width()
        xhi = self.east.get_x()

        ylo = self.south.get_y() + self.south.get_height()
        yhi = self.north.get_y()
        return xlo, xhi, ylo, yhi


def get_bounds(rect):
    return rect.get_x(), rect.get_y(), rect.get_width(), rect.get_height()


class PixelCorral(object):
    """
    Returns the pixel grid
    """
    pass


class CoordinateMapper(object):
    """
    Map points in pixel space to alternate axis
    """
    def __init__(self):
        pass

