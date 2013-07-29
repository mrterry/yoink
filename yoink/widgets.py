"""Backend independent widgets."""
from __future__ import division, print_function
from functools import wraps, partial

import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Widget, AxesWidget
from matplotlib.colorbar import colorbar_factory
from matplotlib.ticker import ScalarFormatter

from .textbox import TextBoxFloat
from .trace import equispaced_colormapping
from .interp import invert_cmap

from .has_actions import Actionable


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


class ShadowLine(AxesWidget):
    """
    """
    def __init__(self, ax, orig_line, cropper, **opts):
        AxesWidget.__init__(self, ax)
        self.orig_line = orig_line
        self.cropper = cropper
        self.line, = ax.plot([], [], transform=self.ax.transAxes, **opts)
        self.orig_line.on_release(self.update)

    def update(self, crop=None):
        x, y = self.orig_line.vertexes.T
        crop = self.cropper.get_extents()

        x0, x1, y0, y1 = crop
        a = (x - x0) / (x1 - x0)
        b = (y - y0) / (y1 - y0)

        self.line.set_data(a, b)
        if self.drawon:
            self.canvas.draw()


class DragableColorLine(Widget, Actionable):
    """
    Fake colormap-like image taken from the end points of a DeformableLine

    Parameters
    ----------
    select_ax : axes
        Axes to draw the selector line on
    cbar_ax : axes
        Axes to draw the colorbar into
    pixels : array-like (3d)
        ndarray to pick colors from
    line_kw : dict, optional
        keyword args to pass to Line2D
    circle_kw : dict, optional
        keyword args to pass to Circle

    Attributes
    ----------
    select_ax : axes
        Axes to draw the selector line on
    cbar_ax : axes
        Axes to draw the colorbar into
    pixels : array-like (3d)
        Pixels values
    line : DeformableLine
        Segmented line
    pixels :  ndarray
        pixels pull colors from
    """
    ACTIONS = [
        ('on_release', 'released', 'disconnect_release'),
        ('on_changed', 'changed', 'disconnect'),
    ]

    def __init__(self, select_ax, cbar_ax, pixels,
                 line_kw=None, circle_kw=None):
        Widget.__init__(self)
        Actionable.__init__(self)
        self.select_ax = select_ax
        self.cbar_ax = cbar_ax
        self._active = True
        self.visible = True

        self.observers = {}
        self.release_observers = {}
        self.cid = 0

        lkw = dict(color='black', linewidth=1)
        if line_kw is not None:
            lkw.update(line_kw)
        ckw = dict(alpha=0.5, radius=10)
        if circle_kw is not None:
            ckw.update(circle_kw)
        self.line = DeformableLine(select_ax,
                                   grows=False, shrinks=False, max_points=2,
                                   line_kw=lkw,
                                   circle_kw=ckw)
        self.pixels = pixels.copy()

        xl, xr = select_ax.get_xlim()
        dx = xr - xl
        yb, yt = select_ax.get_ylim()
        dy = yt - yb
        self.line.add_point(xl + 0.25 * dx, yb + 0.25 * dy)
        self.line.add_point(xl + 0.75 * dx, yb + 0.75 * dy)

        self._fill_cbar_ax()
        self.line.on_changed(self.update)
        self.line.on_release(self.released)

    def _fill_cbar_ax(self):
        """Put a colorbar-like image in the axes"""
        x = np.linspace(0, 1, 50).reshape((50, 1))
        ax = self.cbar_ax

        # Dummy image to get the colorbar
        self._im = ax.imshow(x,
                             extent=[0, 1, 0, 1],
                             visible=False,
                             aspect='auto')
        self._im.drawon = False

        self.cbar = colorbar_factory(ax, self._im)
        ax.yaxis.set_visible(True)

        self.update()

    def update(self):
        """update the properties of the line, redraw, and trigger observers"""
        if len(self.line.circles) != 2:
            return
        x0, y0 = self.line.circles[0].center
        x1, y1 = self.line.circles[1].center
        self.l, self.rgb = equispaced_colormapping(x0, y0, x1, y1, self.pixels)
        cmap = make_cmap(self.l, self.rgb)
        self._im.set_cmap(cmap)
        if self.drawon:
            self.select_ax.figure.canvas.draw()
            self.cbar_ax.figure.canvas.draw()
        self.changed()

    @property
    def active(self):
        """Return whether the widget is active"""
        return self._active

    @active.setter
    def active(self, active):
        """Set whether the widget is active"""
        self._active = self.line.active = active

    def set_visible(self, isvisible):
        """Set whether the widget is visible"""
        self.visible = isvisible
        self.line.set_visible(isvisible)
        if self.drawon:
            self.select_ax.figure.canvas.draw()
            self.cbar_ax.figure.canvas.draw()


class DeformableLine(AxesWidget, Actionable):
    """
    Segemented line with movable vertexes

    Parameters
    ----------
    ax : axes
        Axes to draw the line on
    is_closed : bool, optional default=False
        Do the line endpoints connect?
    max_points : int, optional default=None
        Maximum number of points allowed in line
    grows : bool, optional
        May the line add segments
    shrinks : bool, optional
        May the line shed segments
    line_kw : dict, optional
        Dictionary to customize Line2D
    circle_kw : dict, optional
        Dictionary to customize Circles

    Attributes
    ----------
    ax : axes
        Axes to draw the line on
    is_closed : bool, optional default=False
        Do the line endpoints connect?
    max_points : int | None
        Maximum number of points allowed in line
    grows : bool
        May the line add segments
    shrinks : bool
        May the line shed segments
    circle_kw : dict
        Dictionary to customize Circles
    """
    ACTIONS = [
        ('on_changed', 'changed', 'disconnect'),
        ('on_release', 'released', 'disconnect_release'),
    ]

    def __init__(self, ax,
                 is_closed=False, max_points=None, grows=True, shrinks=True,
                 line_kw=None, circle_kw=None):
        AxesWidget.__init__(self, ax)
        Actionable.__init__(self)
        self.visible = True

        self.observers = {}
        self.release_observers = {}
        self.cid = 0

        self.xs = []
        self.ys = []
        kw = line_kw if line_kw is not None else {}
        self.line, = self.ax.plot(self.xs, self.ys, **kw)

        self.circle_kw = circle_kw if circle_kw is not None else {}

        self.circles = []

        self.moving_ci = None

        self.is_closed = is_closed
        self.max_points = max_points

        self._lclick_cids = None
        self.grows = grows

        self._rclick_cids = None
        self._can_shrink = False
        self.shrinks = shrinks

        self.connect_event('button_press_event', self._left_press),
        self.connect_event('button_release_event', self._release),
        self.connect_event('motion_notify_event', self._motion),

    @property
    def shrinks(self):
        return self._can_shrink

    @shrinks.setter
    def shrinks(self, shrinks):
        self._can_shrink = shrinks

        if shrinks and self._rclick_cids is None:
            self._rclick_cids = [self.connect_event('button_press_event',
                                                    self._right_press)]
        elif not shrinks and self._rclick_cids is not None:
            for cid in self._rclick_cids:
                self.canvas.mpl_disconnect(cid)
                self.cids.remove(cid)
            self._rclick_cids = None

    def add_point(self, x, y):
        """Add a new segment to the DeformableLine"""
        # new circle
        i = len(self.xs)
        circle = Circle((x, y), **self.circle_kw)
        self.circles.append(circle)
        self.ax.add_artist(circle)

        self.xs.append(x)
        self.ys.append(y)
        # finish square if adding last corner
        if self.is_closed and len(self.xs) == self.max_points:
            self.xs.append(self.xs[0])
            self.ys.append(self.ys[0])
        self.line.set_data(self.xs, self.ys)
        if self.drawon:
            self.canvas.draw()
        self.changed()
        return i

    def remove_point(self, i):
        self.ax.artists.remove(self.circles.pop(i))
        self.xs.pop(i)
        self.ys.pop(i)
        self.line.set_data(self.xs, self.ys)
        if self.drawon:
            self.canvas.draw()
        self.changed()

    def set_visible(self, isvisible):
        self.visible = isvisible
        self.line.set_visible(isvisible)
        for c in self.circles:
            c.set_visible(isvisible)
        if self.drawon:
            self.canvas.draw()

    def get_visible(self):
        return self.visible

    @if_attentive
    def _left_press(self, event):
        if event.button != 1 or event.inaxes is not self.ax:
            return
        # Get the circle index
        for ci, c in enumerate(self.circles):
            if c.contains(event)[0]:
                break
        else:
            if not self.grows:
                return
            elif (self.max_points is None or
                  self.max_points > len(self.circles)):
                ci = self.add_point(event.xdata, event.ydata)
            else:
                return

        x0, y0 = self.xs[ci], self.ys[ci]
        self.moving_ci = x0, y0, event.xdata, event.ydata, ci

    @if_attentive
    def _right_press(self, event):
        if event.button != 2 or event.inaxes is not self.ax:
            return
        for ci, c in enumerate(self.circles):
            if c.contains(event)[0]:
                self.remove_point(ci)

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
        if event.inaxes is not self.ax:
            return
        xc, yc, xclick, yclick, ci = self.moving_ci

        x, y = xc + (event.xdata - xclick), yc + (event.ydata - yclick)
        self.set_vertex(ci, x, y)

    def set_vertex(self, ci, x, y):
        self.circles[ci].center = (x, y)
        self.xs[ci], self.ys[ci] = x, y
        if self.is_closed and len(self.circles) == self.max_points and ci == 0:
            self.xs[-1], self.ys[-1] = x, y
        self.line.set_data(self.xs, self.ys)
        if self.drawon:
            self.canvas.draw()
        self.changed()

    @property
    def vertexes(self):
        return self.line.get_xydata()


class ShutterCrop(AxesWidget, Actionable):
    """
    Crop an image by dragging transparent panes over excluded region.

    Parameters
    ----------
    dx_frac : float, optional, default=0.05
        Initial fraction of view that is cropped on each side

    **rect_kw : optional
        Keyword args to customize the shutter `Rectangle`

    By default, shutters have:
        facecolor='gray',
        edgecolor='none',
        alpha=0.5,
        picker=5

    Attributes
    ----------
    ax : axes
        Axes to draw the shutters on
    rects : dict
        Dictionary of Rectangles
    """
    ACTIONS = [
        ('on_changed', 'changed', 'disconnect'),
    ]

    def __init__(self, ax, dx_frac=0.05, **rect_kw):
        self.rects = {}  # AxesWidget sets active=True, so rects needs to exist
        AxesWidget.__init__(self, ax)
        Actionable.__init__(self)
        self.visible = True

        self.observers = {}
        self.cid = 0

        self.active_pick = None

        kw = dict(
            facecolor='gray',
            edgecolor='none',
            alpha=0.5,
            picker=5,
        )
        kw.update(rect_kw)
        self._make_rects(dx_frac, kw)

        self.connect_event('pick_event', self._pick),
        self.connect_event('button_release_event', self._release),
        self.connect_event('motion_notify_event', self._motion),

    def _make_rects(self, dx_frac, kw):
        """Create the rectangles for each shutter"""
        xlo, xhi = self.ax.get_xlim()
        dx = xhi - xlo
        ylo, yhi = self.ax.get_ylim()
        dy = yhi - ylo
        width = dx_frac * dx
        height = dx_frac * dy

        self.rects['north'] = Rectangle((xlo, yhi - height), dx, height, **kw)
        self.rects['south'] = Rectangle((xlo, ylo), dx, height, **kw)
        self.rects['east'] = Rectangle((xhi - width, ylo), width, dy, **kw)
        self.rects['west'] = Rectangle((xlo, ylo), width, dy, **kw)

        for k, r in self.rects.items():
            self.ax.add_artist(r)

    def set_visible(self, isvisible):
        """Make the widget (in)visible"""
        self.visible = isvisible
        for r in self.rects.values():
            r.set_visible(isvisible)
        if self.drawon:
            self.canvas.draw()

    def get_visible(self):
        """Return whether the widget is visible"""
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
        """Callback for to stop monitoring a picked artist"""
        self.active_pick = None

    @if_attentive
    def _motion(self, event):
        """Callback to move a picked artist"""
        if self.active_pick is None:
            return
        if event.inaxes is not self.ax:
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


class RecoloredWidget(AxesWidget, Actionable):
    """
    Widget that recolors a multichannel image using a given a scale sequence
    and associated colors.

    Parameters
    ----------
    ax : axes
        Axes to draw the widget
    pixels : 3d array
        Source pixels to recolor

    Attributes
    ----------
    ax : axes
        Axes to draw the widget
    pixels : 3d array
        Source pixels to recolor
    image : matplotlib.Image
    """
    ACTIONS = [
        ('on_changed', 'changed', 'disconnect'),
    ]

    # TODO what to do for colors "far" from scale
    def __init__(self, ax, pixels):
        AxesWidget.__init__(self, ax)
        Actionable.__init__(self)
        self._pixels = pixels
        self.pixels = pixels[:, :, 0].copy()
        self.image = self.ax.imshow(self.pixels,
                                    aspect='auto',
                                    interpolation='none',
                                    vmin=0,
                                    vmax=1)
        self.l = None

        self.observers = {}
        self.cid = 0

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

    def set_side_extent(self, side, val):
        """Set the cropping extent for a single side `side` to value `val`"""
        ext = list(self.image.get_extent())
        ext[side] = val
        self.image.set_extent(ext)

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
        to the new scale, create a cbar with l & rgb, and redraw the image.
        """
        if l is self.l:
            return
        self.l = l
        self.rgb = rgb
        self.pixels[:, :] = invert_cmap(self._pixels, l, rgb)
        self.cmap = make_cmap(l, rgb)
        self.image.set_cmap(self.cmap)
        if self.drawon:
            self.canvas.draw()
        self.changed()


def make_cmap(l, rgb):
    """Make a colormap from the sequence of distances & colors"""
    seq = [(x, col) for x, col in zip(l, rgb)]
    cmap = LinearSegmentedColormap.from_list(None, seq)
    return cmap


class ScaledColorbar(AxesWidget):
    """
    Colorbar with manually specified extrema

    Parameters
    ----------
    ax : axes
        parent axes
    im : ScalarMappable
        ScalarMappable to draw a colorbar for

    Attributes
    ----------
    cbar : matplotlib Colorbar
        colorbar
    fmt : matplotlib formatter
        colorbar text formatter
    """
    def __init__(self, ax, im):
        AxesWidget.__init__(self, ax)

        self.cbar = colorbar_factory(ax, im)
        self.fmt = self.cbar.formatter = OffsetFormatter()
        self.ax.yaxis.set_visible(True)

    def set_min(self, mn):
        self.fmt.mn = mn
        self.cbar.update_ticks()

    def set_max(self, mx):
        self.fmt.mx = mx
        self.cbar.update_ticks()


class OffsetFormatter(ScalarFormatter):
    """
    child of matplotlib.ScalarFormatter to make it easy to set the numerical
    limits of the colorbar

    Parameters
    ----------
    *args : optional
        positional arguments to forward to ScalarFormatter
    *kwargs : optional
        keyword arguments to forward to ScalarFormatter

    Attributes
    ----------
    mn : number
        scale minimum
    mx : number
        scale maximum
    """
    def __init__(self, *args, **kwargs):
        ScalarFormatter.__init__(self, *args, **kwargs)
        self.mn = 0.
        self.mx = 1.

    def __call__(self, x, pos=None):
        dc = self.mx - self.mn
        x = x*dc + self.mn
        return ScalarFormatter.__call__(self, x, pos=pos)


class CroppedImage(AxesWidget, Actionable):
    """
    Widget that recolors a multichannel image using a given a scale sequence
    and associated colors.

    Parameters
    ----------
    ax : axes
        Axes to draw the widget
    pixels : 3d array
        Source pixels to recolor

    Attributes
    ----------
    ax : axes
        Axes to draw the widget
    pixels : 3d array
        Source pixels to recolor
    image : matplotlib image
        The image displayed on the axes
    """
    ACTIONS = [
        ('on_changed', 'changed', 'disconect'),
    ]

    # TODO what to do for colors "far" from scale
    def __init__(self, ax, pixels):
        AxesWidget.__init__(self, ax)
        Actionable.__init__(self)
        self.pixels = pixels
        self.image = self.ax.imshow(self.pixels,
                                    aspect='auto',
                                    interpolation='none',
                                    vmin=0,
                                    vmax=1)
        self.l = None

        self.observers = {}
        self.cid = 0

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

    def set_side_extent(self, side, val):
        """Set the cropping extent for a single side `side` to value `val`"""
        ext = list(self.image.get_extent())
        ext[side] = val
        self.image.set_extent(ext)
        self.ax.set_xlim(ext[:2])
        self.ax.set_ylim(ext[2:])

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
