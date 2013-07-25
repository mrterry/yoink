"""Things I'm not ready to remove, but should be prevented from infecting
things that actually work."""
from __future__ import division, print_function

from matplotlib.widgets import Widget
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from skimage.feature import corner_harris

from .guess import guess_corners, mean_rotation, clear_border
from .data import rotated_lena, rotated_parabola
from .widgets import if_attentive


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


def keyboard_crop(im):
    corners = corner_harris(im)
    lim = {
        'west': corners[:, 1].min()-3,
        'east': corners[:, 1].max()+3,
        'north': corners[:, 0].max()-3,
        'south': corners[:, 0].min()+3,
    }
    limiter = KeyboardCrop(im, lim)

    limiter.edge_effects['west'] = {'left': -1, 'right': +1}
    limiter.edge_effects['north'] = {'up': +1, 'down': -1}
    limiter.edge_effects['east'] = {'left': +1, 'right': -1}
    limiter.edge_effects['south'] = {'up': -1, 'down': +1}

    ylo, xhi, yhi, xlo = limiter.get_edges()
    cropped = im[ylo:yhi, xlo:xhi]
    return cropped


def lena_example():
    im = rotated_lena()

    # find corners on grayscale image
    # use negative so that boundary is 0
    bw = im[:, :, 0]
    bw = 255 - bw

    corners, outline = guess_corners(bw)
    angle = mean_rotation(corners) * 180./np.pi
    im2 = clear_border(im, outline)
    im2 = ndimage.rotate(im, angle, reshape=False, mode='nearest')
    cropped = keyboard_crop(im2)

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    ax1.imshow(im)
    ax1.plot(corners[:, 1], corners[:, 0], 'o')
    ax2.imshow(im2)
    ax3.imshow(cropped)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.imshow(cropped[:20, :20])
    ax2.imshow(cropped[:20, -20:])
    ax3.imshow(cropped[-20:, :20])
    ax4.imshow(cropped[-20:, -20:])
    return cropped


def parabola_example():
    im = rotated_parabola()

    # find corners on grayscale image
    # use negative so that boundary is 0
    bw = im[:, :, 0]
    bw = 255 - bw

    corners, outline = guess_corners(bw)
    angle = mean_rotation(corners)
    im2 = clear_border(im, outline)
    im2 = ndimage.rotate(im, angle, reshape=False, mode='nearest')
    cropped = keyboard_crop(im2)

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    ax1.imshow(im)
    ax1.plot(corners[:, 1], corners[:, 0], 'o')
    ax2.imshow(im2)
    ax3.imshow(cropped)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.imshow(cropped[:20, :20])
    ax2.imshow(cropped[:20, -20:])
    ax3.imshow(cropped[-20:, :20])
    ax4.imshow(cropped[-20:, -20:])
    return cropped
