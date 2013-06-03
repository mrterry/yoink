from __future__ import division

from functools import wraps

import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Widget, AxesWidget

from yoink.trace import equispaced_colormaping


def if_attentive(f):
    @wraps(f)
    def wrapper(self, event):
        if not self.ignore(event):
            return f(self, event)
    return wrapper


class DragableCmap(Widget):
    """
    Fake colormap-like image taken from the end points of a DeformableLine
    """
    def __init__(self, select_ax, cmap_ax, source):
        self.select_ax = select_ax
        self.cmap_ax = cmap_ax
        self._active = True
        self.visible = True

        self.line = DeformableLine(select_ax, max_points=2)
        self.source = source

        self.l = None
        self.rgb = None

        xl, xr = select_ax.get_xlim()
        dx = xr - xl
        yb, yt = select_ax.get_ylim()
        dy = yt - yb
        self.line.add_point(xl + 0.25*dx, yb + 0.25*dy)
        self.line.add_point(xl + 0.75*dx, yb + 0.75*dy)

        self._create_cmap()
        self.line.callbacks.append(self.update)

    def _create_cmap(self):
        rgb = np.zeros((2, 1, 4))
        self.im = self.cmap_ax.imshow(rgb,
                aspect='auto', origin='lower', extent=[0, 1, 0, 1])
        self.cmap_ax.yaxis.tick_right()
        self.cmap_ax.xaxis.set_visible(False)
        self.update()

    def update(self):
        if len(self.line.circles) != 2:
            return
        x0, y0 = self.line.circles[0].center
        x1, y1 = self.line.circles[1].center
        self.l, self.rgb = equispaced_colormaping(x0, y0, x1, y1, self.source)

        n, ncol = self.rgb.shape
        self.im.set_data(self.rgb.reshape((n, 1, ncol)))
        self.draw()

    def make_cmap(self, name, **kwargs):
        assert None not in (self.l, self.rgb)
        seq = [(x, col) for x, col in zip(self.l, self.rgb)]
        return LinearSegmentedColormap.from_list(name, seq, **kwargs)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = self.line.active = active

    def set_visible(self, vis):
        self.visible = vis
        self.line.set_visible(vis)
        self.draw()

    def draw(self):
        self.select_ax.figure.canvas.draw()
        self.cmap_ax.figure.canvas.draw()


class DeformableLine(AxesWidget):
    """
    Segemented line with movable vertexes
    """
    def __init__(self, ax, is_closed=False, max_points=None):
        AxesWidget.__init__(self, ax)
        self.visible = True

        self.xs = []
        self.ys = []
        self.line = Line2D(self.xs, self.ys)
        self.ax.add_artist(self.line)

        self.circles = []

        self.is_closed = is_closed
        self.max_points = max_points

        self.callbacks = []
        self.moving_ci = None

        self.connect_event('button_press_event', self._press)
        self.connect_event('button_release_event', self._release)
        self.connect_event('motion_notify_event', self._motion)

    def draw(self):
        for f in self.callbacks:
            f()
        self.canvas.draw()

    def get_circle_index(self, event):
        i = 0
        for i, c in enumerate(self.circles):
            if c.contains(event)[0]:
                return i
        if len(self.circles) == self.max_points:
            return None

        i = self.add_point(event.xdata, event.ydata)
        return i

    def add_point(self, x, y):
        # new circle
        i = len(self.circles)
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

    def set_visible(self, vis):
        self.visible = vis
        self.line.set_visible(vis)
        for c in self.circles:
            c.set_visible(vis)
        self.draw()

    def get_visible(self, vis):
        return self.visible

    @if_attentive
    def _press(self, event):
        ci = self.get_circle_index(event)
        if ci is None:
            return
        circle = self.circles[ci]
        x0, y0 = circle.center
        self.moving_ci = x0, y0, event.xdata, event.ydata, ci

    @if_attentive
    def _release(self, event):
        if self.moving_ci:
            self.moving_ci = None
            self.draw()

    @if_attentive
    def _motion(self, event):
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


class ShutterCrop(AxesWidget):
    """
    Crop an image by dragging transparent panes over excluded region.
    """
    def __init__(self, ax,
            dx_frac=0.05, dy_frac=0.05,
            facecolor='gray', edgecolor='none', alpha=0.5, picker=5,
            **rect_kw):
        self.rects = {}  # AxesWidget sets active=True, so rects needs to exist
        AxesWidget.__init__(self, ax)
        self.visible = True

        self.active_pick = None

        kw = dict(facecolor=facecolor, edgecolor=edgecolor, picker=picker,
                alpha=alpha, **rect_kw)
        self._make_rects(dx_frac, dy_frac, kw)

        self.connect_event('pick_event', self._pick),
        self.connect_event('button_release_event', self._release),
        self.connect_event('motion_notify_event', self._motion),

    def _make_rects(self, dx_frac, dy_frac, kw):
        xlo, xhi = self.ax.get_xlim()
        dx = xhi-xlo
        ylo, yhi = self.ax.get_ylim()
        dy = yhi - ylo
        width = dx_frac*dx
        height = dy_frac*dy

        self.rects['north'] = Rectangle((xlo, yhi-height), dx, height, **kw)
        self.rects['south'] = Rectangle((xlo, ylo), dx, height, **kw)
        self.rects['east'] = Rectangle((xhi-width, ylo), width, dy, **kw)
        self.rects['west'] = Rectangle((xlo, ylo), width, dy, **kw)

        for k, r in self.rects.iteritems():
            self.ax.add_artist(r)

    def set_visible(self, vis):
        self.visible = vis
        for r in self.rects.values():
            r.set_visible(vis)
        self.canvas.draw()

    def get_extents(self):
        west = self.rects['west']
        xlo = west.get_x() + west.get_width()
        xhi = self.rects['east'].get_x()

        south = self.rects['south']
        ylo = south.get_y() + south.get_height()
        yhi = self.rects['north'].get_y()
        return xlo, xhi, ylo, yhi

    @if_attentive
    def _pick(self, event):
        for k in self.rects:
            r = self.rects[k]
            if event.artist is r:
                bounds = (
                        r.get_x(),
                        r.get_y(),
                        r.get_width(),
                        r.get_height(),
                        )
                click = (event.mouseevent.xdata, event.mouseevent.ydata)
                self.active_pick = (r, click, bounds)
                return

    @if_attentive
    def _release(self, event):
        self.active_pick = None

    @if_attentive
    def _motion(self, event):
        if self.active_pick is None:
            return
        bar, (xclick, yclick), (x, y, w, h) = self.active_pick

        if bar is self.rects['south']:
            new_height = h + (event.ydata-yclick)
            bar.set_height(new_height)
        elif bar is self.rects['west']:
            new_w = w + (event.xdata-xclick)
            bar.set_width(new_w)
        elif bar is self.rects['north']:
            dy = event.ydata - yclick
            new_h = h - dy
            new_y = y + dy
            bar.set_height(new_h)
            bar.set_y(new_y)
        elif bar is self.rects['east']:
            dx = event.xdata - xclick
            new_w = w - dx
            new_x = x + dx
            bar.set_x(new_x)
            bar.set_width(new_w)

        self.canvas.draw()


class KeyboardCrop(Widget):
    """
    Keyboard driven interface to set crop an image

    KeyboardCrop.edge_effects is a dict that controls the keyboard interface.
    the keys are the edges effected (north/south/east/west)
    the values are dicts of keyboard-keys and how far to shift the image
    (nominally in pixels).

    Example usage given in keyboard_crop()
    """
    def __init__(self, im, limits, width=20, height=20, **kwargs):
        import matplotlib.pyplot as plt
        self.im = im
        self.crop = limits
        fig, axes = plt.subplots(2, 2, sharex='col', sharey='row')
        self.canvas = fig.canvas
        (self.ax1, self.ax2), (self.ax3, self.ax4) = axes
        self.edge_effects = {}

        self.width = width
        self.height = height

        self.ax1.imshow(im, **kwargs)
        self.ax2.imshow(im, **kwargs)
        self.ax3.imshow(im, **kwargs)
        self.ax4.imshow(im, **kwargs)
        self.update_limits()

    def update_limits(self):
        self.ax1.set_xlim(self.crop['west'], self.crop['west']+self.width)
        self.ax2.set_xlim(self.crop['east']-self.width, self.crop['east'])
        self.ax1.set_ylim(self.crop['north'], self.crop['north']+self.height)
        self.ax3.set_ylim(self.crop['south']-self.height, self.crop['south'])
        self.canvas.draw()

    def on_press(self, event):
        key = event.key
        if key is 'enter':
            return

        for edge, effects in self.edge_effects:
            if key in effects:
                self.crop[edge] += effects[key]
        self.update_limits()

    def connect(self):
        self.press_cid = self.canvas.mpl_connect(
                'key_press_event', self.on_press)

    def disconnect(self):
        self.canvas.mpl_disconnect(self.press_cid)
        self.press_cid = None

    def get_edges(self):
        return [self.crop[key] for key in ('south', 'east', 'north', 'west')]
