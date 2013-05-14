import yoink.widgets
import pylab as plt

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
    limiter = yoink.widgets.KeyboardCrop(im, lim)

    limiter.edge_effects['west'] = {'left': -1, 'right': +1}
    limiter.edge_effects['north'] = {'up': +1, 'down': -1}
    limiter.edge_effects['east'] = {'left': +1, 'right': -1}
    limiter.edge_effects['south'] = {'up': -1, 'down': +1}

    plt.show()

    ylo, xhi, yhi, xlo = limiter.get_edges()
    cropped = im[ylo:yhi, xlo:xhi]
    return cropped
