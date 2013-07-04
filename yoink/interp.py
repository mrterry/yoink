"""Functions for interpreting data in different contexts.  So, inverting a
colormap, interpolating points from pixel to data coordinates, and such."""
from __future__ import division, print_function

import numpy as np
from scipy.spatial import cKDTree


def invert_cmap(pix, l, colors):
    """
    Given a sequence of pixels, convert each to an equivalent index in the
    color sequence l, colors

    Uses a scipy.spatial.cKDTree to find the color with closest coordinates in
    RGB space.
    """
    kd = cKDTree(colors)
    ni, nj, nc = pix.shape
    pix = pix.reshape((ni * nj, nc))
    d, i = kd.query(pix)
    i = i.reshape((ni, nj))
    return l[i]


def order_corners(corners):
    """
    bottom-left, bottom-right, top-right, top-left
    min(x**2+y**2), argmin(y), argmax(x), left
    """
    corners = list(corners)
    assert len(corners) == 4
    assert len(corners[0]) == 2
    ordered = []

    radii = [x ** 2 + y ** 2 for x, y in corners]
    i = np.argmin(radii)
    ordered.append(corners.pop(i))

    i = np.argmin([y for x, y in corners])
    ordered.append(corners.pop(i))

    i = np.argmax([x for x, y in corners])
    ordered.append(corners.pop(i))

    ordered += corners

    return ordered


def get_corner_grid(corners, ni, nj):
    """
    Get uniform grid between corners

    Parameters
    ----------
    corners : list
        list of x,y coordinates
    ni : int
        number of points in first index
    nj : int
        number of points in second index

    Returns
    -------
    x : ndarray, shpae=(ni, nj)
        grid of first dimension coordinates
    y : ndarray, shpae=(ni, nj)
        grid of second dimension coordinates
    """
    bl, br, tr, tl = order_corners(corners)
    x = np.zeros((ni, nj))

    left_x = _midspace(tl[0], bl[0], ni)
    right_x = _midspace(tr[0], br[0], ni)

    bot_y = _midspace(bl[1], br[1], nj)
    top_y = _midspace(tl[1], tr[1], nj)

    di = 1. / ni
    dj = 1. / nj
    ispan = np.arange(di / 2, 1., di)
    jspan = np.arange(dj / 2, 1., dj)

    x = np.empty((ni, nj))
    x[:, :] = jspan
    x *= (right_x - left_x)[:, None]
    x += left_x[:, None]

    y = np.empty((ni, nj))
    y[:, :] = ispan[:, None]
    y *= (top_y - bot_y)
    y += bot_y
    return x, y


def _midspace(start, end, n):
    """
    Cut region start/end into n regions and return the midpoint of each bin
    """
    x = np.linspace(start, end, n + 1)
    x = x[:-1] + np.diff(x)
    return x
