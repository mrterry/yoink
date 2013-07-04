"""Functions that try to infer the placement of key things (plot border, axes
rotation, lines on a plot, etc) in a rasterized image."""
from __future__ import division, print_function

import numpy as np
from scipy import ndimage
from skimage import img_as_uint
from skimage.measure import approximate_polygon
from skimage.feature import corner_harris


def guess_corners(bw):
    """
    Infer the corners of an image using a Sobel filter to find the edges and a
    Harris filter to find the corners.  Takes a single color chanel.

    Parameters
    ----------
    bw : (m x n) ndarray of ints

    Returns
    -------
    corners : pixel coordinates of plot corners, unsorted
    outline : (m x n) ndarray of bools True -> plot area
    """
    assert len(bw.shape) == 2
    bw = img_as_uint(bw)
    e_map = ndimage.sobel(bw)

    markers = np.zeros(bw.shape, dtype=int)
    markers[bw < 30] = 1
    markers[bw > 150] = 2
    seg = ndimage.watershed_ift(e_map, np.asarray(markers, dtype=int))

    outline = ndimage.binary_fill_holes(1 - seg)
    corners = corner_harris(np.asarray(outline, dtype=int))
    corners = approximate_polygon(corners, 1)
    return corners, outline


def _get_angle(p1, p2):
    return np.arctan2(p1[0] - p2[0], p1[1] - p2[1])


def mean_rotation(corners):
    """
    Assuming the corners define a rectangle return the angle betwen the
    rectangle and the x axis.
    """
    corners = np.asarray(corners)
    order = np.argsort(corners[:, 0])
    top = corners[order[:2]]
    bot = corners[order[2:]]

    order = np.argsort(corners[:, 1])
    left = corners[order[:2]]
    right = corners[order[2:]]

    angles = [_get_angle(top[0, :], top[1, :]),
              _get_angle(bot[0, :], bot[1, :]),
              _get_angle(left[0, :], left[1, :]) + 90,
              _get_angle(right[0, :], right[1, :]) + 90,
              ]
    angle = sum(angles) / len(angles)
    return angle


def clear_border(im, outline):
    # TODO work with float & int arrays
    im_fixed = im.copy()
    im_fixed[-outline] = 255
    return im_fixed
