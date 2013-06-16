import pylab as plt
import numpy as np
from scipy import ndimage

from yoink.widgets import KeyboardCrop
from yoink.guess import guess_corners, mean_rotation, clear_border
from yoink.data import rotated_lena, rotated_parabola

try:
    from skimage.feature import corner_harris
except ImportError:
    from yoink.mini_skimage import corner_harris


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

    plt.show()

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
