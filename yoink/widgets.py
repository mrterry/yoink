from __future__ import division

from functools import wraps, partial

import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Widget, AxesWidget

from yoink.textbox import TextBoxFloat
from yoink.trace import equispaced_colormaping
from yoink.interp import invert_cmap_kdtree


def if_attentive(f):
    @wraps(f)
    def wrapper(self, event):
        if not self.ignore(event):
            return f(self, event)
    return wrapper


class NothingWidget(object):
    active = False

    def set_visible(self, vis):
        pass


class DragableColorLine(Widget):
    """
    Fake colormap-like image taken from the end points of a DeformableLine

    Parameters
    ----------

    select_ax : axes
        Axes to draw the selector line on
    cmap_ax : axes
        Axes to draw the colorbar into
    pixes : array-like (3d)
        Pixels values
    """
    def __init__(self, select_ax, cmap_ax, pixels):
        Widget.__init__(self)
        self.select_ax = select_ax
        self.cmap_ax = cmap_ax
        self._active = True
        self.visible = True

        self.observers = {}
        self.release_observers = {}
        self.cid = 0

        self.line = DeformableLine(select_ax, max_points=2)
        self.pixels = pixels.copy()

        xl, xr = select_ax.get_xlim()
        dx = xr - xl
        yb, yt = select_ax.get_ylim()
        dy = yt - yb
        self.line.add_point(xl + 0.25 * dx, yb + 0.25 * dy)
        self.line.add_point(xl + 0.75 * dx, yb + 0.75 * dy)

        self._fill_cmap_ax()
        self.line.on_changed(self.update)
        self.line.on_release(self.released)

    def on_release(self, func):
        """
        When the DragableColorLine finishes moving, call *func* with the new
        path and colors.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.release_observers[cid] = func
        self.cid += 1
        return cid

    def disconnect_release(self, cid):
        """remove the release_observer with connection id *cid*"""
        try:
            del self.release_observers[cid]
        except KeyError:
            pass

    def released(self):
        """call the release_observers"""
        for func in self.release_observers.itervalues():
            func(self.l, self.rgb)

    def on_changed(self, func):
        """
        When the DragableColorLine moves, call *func* with the new path and
        colors.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.observers[cid] = func
        self.cid += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def changed(self):
        """Call the observers"""
        for func in self.observers.itervalues():
            func(self.l, self.rgb)

    def _fill_cmap_ax(self):
        rgb = np.zeros((2, 1, 4))
        self.cmap_im = self.cmap_ax.imshow(rgb,
                                           aspect='auto',
                                           origin='lower',
                                           extent=[0, 1, 0, 1])
        self.cmap_ax.xaxis.set_visible(False)
        self.cmap_ax.yaxis.set_visible(False)
        self.update()

    def update(self):
        if len(self.line.circles) != 2:
            return
        x0, y0 = self.line.circles[0].center
        x1, y1 = self.line.circles[1].center
        self.l, self.rgb = equispaced_colormaping(x0, y0, x1, y1, self.pixels)

        n, ncol = self.rgb.shape
        self.cmap_im.set_data(self.rgb.reshape((n, 1, ncol)))
        self.cmap_im.set_extent([0, 1, self.l[0], self.l[-1]])

        self.redraw()
        self.changed()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = self.line.active = active

    def set_visible(self, isvisible):
        self.visible = isvisible
        self.line.set_visible(isvisible)
        self.redraw()

    def redraw(self):
        if self.drawon:
            self.select_ax.figure.canvas.draw()
            self.cmap_ax.figure.canvas.draw()


class DeformableLine(AxesWidget):
    """
    Segemented line with movable vertexes
    """
    def __init__(self, ax, is_closed=False, max_points=None):
        AxesWidget.__init__(self, ax)
        self.visible = True

        self.observers = {}
        self.release_observers = {}
        self.cid = 0

        self.xs = []
        self.ys = []
        self.line = Line2D(self.xs, self.ys)
        self.ax.add_artist(self.line)

        self.circles = []

        self.is_closed = is_closed
        self.max_points = max_points

        self.moving_ci = None

        self.connect_event('button_press_event', self._press)
        self.connect_event('button_release_event', self._release)
        self.connect_event('motion_notify_event', self._motion)

    def on_changed(self, func):
        """
        When the DeformableLine moves, call *func* with no parameters.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.observers[cid] = func
        self.cid += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def changed(self):
        """Call the observers"""
        for func in self.observers.itervalues():
            func()

    def on_release(self, func):
        """
        When finished moving, call *func* with no parameters.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.release_observers[cid] = func
        self.cid += 1
        return cid

    def disconnect_release(self, cid):
        """remove the release_observer with connection id *cid*"""
        try:
            del self.release_observers[cid]
        except KeyError:
            pass

    def released(self):
        """Call the release_observers"""
        for func in self.release_observers.itervalues():
            func()

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
        """Add a new segment to the DeformableLine"""
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
        if self.drawon:
            self.canvas.draw()
        self.changed()
        return i

    def set_visible(self, isvisible):
        self.visible = isvisible
        self.line.set_visible(isvisible)
        for c in self.circles:
            c.set_visible(isvisible)
        if self.drawon:
            self.canvas.draw()
        self.changed()

    def get_visible(self):
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
            if self.drawon:
                self.canvas.draw()
            self.changed()
            self.released()

    @if_attentive
    def _motion(self, event):
        if self.moving_ci is None:
            return
        xc, yc, xclick, yclick, ci = self.moving_ci

        x, y = xc + (event.xdata - xclick), yc + (event.ydata - yclick)
        self.circles[ci].center = (x, y)

        self.xs[ci], self.ys[ci] = x, y
        if self.is_closed and len(self.circles) == self.max_points and ci == 0:
            self.xs[-1], self.ys[-1] = x, y
        self.line.set_data(self.xs, self.ys)

        if self.drawon:
            self.canvas.draw()
        self.changed()


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

        self.observers = {}
        self.cid = 0

        self.active_pick = None

        kw = dict(facecolor=facecolor,
                  edgecolor=edgecolor,
                  picker=picker,
                  alpha=alpha,
                  **rect_kw)
        self._make_rects(dx_frac, dy_frac, kw)

        self.connect_event('pick_event', self._pick),
        self.connect_event('button_release_event', self._release),
        self.connect_event('motion_notify_event', self._motion),

    def on_changed(self, func):
        """
        When the ShutterCrop windows move, call *func* with the new extent.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.observers[cid] = func
        self.cid += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def changed(self):
        """Call the observers"""
        extent = self.get_extents()  # data (pixel) coordinates
        for func in self.observers.itervalues():
            func(extent)

    def _make_rects(self, dx_frac, dy_frac, kw):
        xlo, xhi = self.ax.get_xlim()
        dx = xhi - xlo
        ylo, yhi = self.ax.get_ylim()
        dy = yhi - ylo
        width = dx_frac * dx
        height = dy_frac * dy

        self.rects['north'] = Rectangle((xlo, yhi - height), dx, height, **kw)
        self.rects['south'] = Rectangle((xlo, ylo), dx, height, **kw)
        self.rects['east'] = Rectangle((xhi - width, ylo), width, dy, **kw)
        self.rects['west'] = Rectangle((xlo, ylo), width, dy, **kw)

        for k, r in self.rects.iteritems():
            self.ax.add_artist(r)

    def set_visible(self, isvisible):
        self.visible = isvisible
        for r in self.rects.values():
            r.set_visible(isvisible)
        if self.drawon:
            self.canvas.draw()

    def get_visible(self):
        return self.visible

    def get_extents(self):
        """Get the extents of the cropped image"""
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
            new_height = h + (event.ydata - yclick)
            bar.set_height(new_height)
        elif bar is self.rects['west']:
            new_w = w + (event.xdata - xclick)
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

        self.changed()
        if self.drawon:
            self.canvas.draw()
        self.changed()


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

        self.cids = [self.canvas.mpl_connect('key_press_event', self._press)]
        self.update_limits()

    def update_limits(self):
        self.ax1.set_xlim(self.crop['west'], self.crop['west'] + self.width)
        self.ax2.set_xlim(self.crop['east'] - self.width, self.crop['east'])
        self.ax1.set_ylim(self.crop['north'], self.crop['north'] + self.height)
        self.ax3.set_ylim(self.crop['south'] - self.height, self.crop['south'])
        if self.drawon:
            self.canvas.draw()

    @if_attentive
    def _press(self, event):
        key = event.key
        if key is 'enter':
            return

        for edge, effects in self.edge_effects:
            if key in effects:
                self.crop[edge] += effects[key]
        self.update_limits()

    def get_edges(self):
        return [self.crop[key] for key in ('south', 'east', 'north', 'west')]


class ScaledCmap(AxesWidget):
    def __init__(self, ax, lo_ax, hi_ax, l, rgb):
        AxesWidget.__init__(self, ax)

        self.observers = {}
        self.cid = 0

        self.l = self.z = l

        self.zlo = self.z[0]
        self.zhi = self.z[-1]
        self.lo_tb = TextBoxFloat(lo_ax, str(self.zlo))
        self.hi_tb = TextBoxFloat(hi_ax, str(self.zhi))

        n, nc = rgb.shape
        self.rgb = rgb
        self.cmap_im = self.ax.imshow(rgb.reshape((n, 1, nc)),
                                      aspect='auto',
                                      origin='lower',
                                      extent=[0, 1, 0, 1])
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.tick_right()
        self.ax.yaxis.set_visible(True)
        self.update_extent()

        self.lo_tb.on_changed(self.update_lbound)
        self.hi_tb.on_changed(self.update_ubound)

        self.l = np.linspace(0, 1, 20)
        self.rgb = np.zeros_like(self.l)

    def on_changed(self, func):
        cid = self.cid
        self.observers[cid] = func
        self.cid += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def changed(self):
        """Call the observers"""
        for func in self.observers.itervalues():
            func()

    def update_lbound(self, val):
        self.zlo = val
        self.update_extent()

    def update_ubound(self, val):
        self.zhi = val
        self.update_extent()

    def update_extent(self):
        dz = self.zhi - self.zlo
        self.z = self.zlo + self.l * dz
        extent = [0, 1, self.z[0], self.z[-1]]
        self.cmap_im.set_extent(extent)
        if self.drawon:
            self.canvas.draw()
        self.changed()

    def set_color(self, l, rgb):
        self.l = l
        n, nc = rgb.shape
        self.rgb = rgb
        self.cmap_im.set_data(rgb.reshape((n, 1, nc)))
        self.update_extent()
        self.changed()


class RecoloredWidget(AxesWidget):
    """
    Widget that recolors a multichannel image using a given a scale sequence
    and associated colors.

    Paramters
    ---------
    ax : axes
        Axes to draw the widget
    pixels : 3d array
        Source pixels to recolor
    """
    # TODO what to do for colors "far" from scale
    def __init__(self, ax, pixels):
        AxesWidget.__init__(self, ax)
        self._pixels = pixels
        self.pixels = pixels[:, :, 0].copy()
        self.image = self.ax.imshow(self.pixels,
                                    aspect='auto',
                                    interpolation='none')
        self.l = None

        self.observers = {}
        self.cid = 0

    def on_changed(self, func):
        """
        When the RecoloredWidget changes, call *func* with no arguments.

        A connection id is returned which can be used to disconnect.
        """
        cid = self.cid
        self.observers[cid] = func
        self.cid += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def changed(self):
        """Call the observers"""
        for func in self.observers.itervalues():
            func()

    def make_xyextent_textboxes(self, ax_xlo, ax_xhi, ax_ylo, ax_yhi):
        """
        Create text boxes for x-axis & y-axis limits
        connect them to the right image so that it extents auto-update
        """
        ext = self.image.get_extent()
        self.image.set_extent(ext)
        self.textboxes = []
        for i, ax in enumerate([ax_xlo, ax_xhi, ax_ylo, ax_yhi]):
            tb = TextBoxFloat(ax, str(ext[i]))
            tb.on_changed(partial(self.set_side_extent, i))
            self.textboxes.append(tb)

    def make_clim_textboxes(self, ax_lo, ax_hi):
        pass

    def set_side_extent(self, side, val):
        """Set the cropping extent for a single side `side` to value `val`"""
        ext = list(self.image.get_extent())
        ext[side] = val
        self.image.set_extent(ext)

    def dump(self):
        pass

    def crop(self, extent):
        """Crop self.image to the given extent"""
        x0, x1, y0, y1 = np.array(extent, dtype=int)
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        pix = self.pixels[y0:y1, x0:x1]

        self.image.set_data(pix)
        if self.drawon:
            self.canvas.draw()
        self.changed()

    def digitize(self, l, rgb):
        """
        Using the new scale "l" and colorsequence "rgb" translate all pixels
        to the new scale, create a cmap with l & rgb, and redraw the image.
        """
        if l is self.l:
            return
        self.l = l
        self.pixels = invert_cmap_kdtree(self._pixels, l, rgb)
        seq = [(x, col) for x, col in zip(l, rgb)]
        self.cmap = LinearSegmentedColormap.from_list(None, seq)
        self.image.set_cmap(self.cmap)
        if self.drawon:
            self.canvas.draw()
        self.changed()
