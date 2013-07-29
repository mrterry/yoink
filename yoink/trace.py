"""Find the pixels between two endpoints"""
from __future__ import division, print_function
from math import floor

import numpy as np
from scipy.ndimage.interpolation import map_coordinates


def naive_trace(x0, y0, x1, y1):
    """
    Matt Terry's naive tracing method.  No promises that this is fast,
    reliable, or good.
    """
    NEGX = NEGY = SWAP = False

    DX = x1 - x0
    DY = y1 - y0

    if abs(DY) > abs(DX):
        # avoid infinite slopes by double swapping coordinates
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        SWAP = True
        DX, DY = DY, DX
    if DX < 0:
        NEGX = True
        x0, x1 = -x0, -x1
        DX = -DX
    if DY < 0:
        NEGY = True
        y0, y1 = -y0, -y1
        DY = -DY

    def order(xi_tmp, x_tmp, yi_tmp, y_tmp):
        if NEGX:
            xi_tmp, x_tmp = int(-x_tmp), -x_tmp
        if NEGY:
            yi_tmp, y_tmp = int(-y_tmp), -y_tmp
        if SWAP:
            xi_tmp, x_tmp, yi_tmp, y_tmp = yi_tmp, y_tmp, xi_tmp, x_tmp
        return (xi_tmp, x_tmp, yi_tmp, y_tmp)

    m = DY/DX
    xy_end = int(floor(x1)), int(floor(y1))

    x = int(floor(x0))
    fx = x0 - x

    y = int(floor(y0))
    fy = y0 - y

    path = [order(x, x+fx, y, y+fy)]
    for step in xrange(2*int(abs(DX) + abs(DY))):
        y_rise = (1-fx)*m
        if y_rise + fy > 1:
            # step y
            fx += (1 - fy)/m  # only bad if m==0 and fy>0
            y += 1
            fy = 0.
        else:  # step x
            fy += y_rise
            x += 1
            fx = 0.
        path.append(order(x, x+fx, y, y+fy))
        if (x, y) == xy_end:
            path.append(order(int(x1), x1, int(y1), y1))
            return path
    assert False


def bresenham_trace(x, y, x1, y1):
    """
    For a line (x, y) to (x1, y1) return the pixels that the line crosses.

    http://en.wikipedia.org/wiki/Bresenham's_line_algorithm
    Bresenham, J. E. (1 January 1965). "Algorithm for computer control of a
    digital plotter". IBM Systems Journal 4 (1): 25-30.
    """
    x, y = int(x), int(y)
    x1, y1 = int(x1), int(y1)
    dx = abs(x1 - x)
    dy = abs(y1 - y)
    sx = 1 if x < x1 else -1
    sy = 1 if y < y1 else -1
    err = dx-dy

    BIG = 2*(dx+dy+2)
    path = []
    for step in xrange(BIG):
        path.append((x, y))

        if x == x1 and y == y1:
            break
        e2 = 2*err
        if e2 > -dy:
            err -= dy
            x += sx
        if (x, y) == (x1, y1):
            break
        if e2 < dx:
            err += dx
            y += sy
    else:
        assert False
    return path


def naive_colormapping(x0, y0, x1, y1, im, order=1):
    """
    Get lineout from x0/y0 to x1/y1 with points takein from naive_trace ray
    tracing algorithm.

    Returns
    -------

    l : ndarray, shape=(N,)
        normalized location of colors
    rgb : ndarray, shape=(N,3)
        sequence of colors at each point in l
    """
    stuff = naive_trace(x0, y0, x1, y1)
    jj, x, jj, y = zip(*stuff)
    x, y = np.array(x), np.array(y)
    dx = x[-1] - x[0]
    dy = y[-1] - y[0]
    if dx > dy:
        l = (x - x0)/dx
    else:
        l = (y - y0)/dy
    return l, get_rgb(im, y, x, order=order)


def equispaced_colormapping(x0, y0, x1, y1, im, N=256, order=1):
    """
    Get lineout from x0/y0 to x1/y1 with equally spaced points.

    Returns
    -------

    l : ndarray, shape=(N,)
        normalized location of colors
    rgb : ndarray, shape=(N,3)
        sequence of colors at each point in l
    """
    y2 = np.linspace(y0, y1, N)
    x2 = np.linspace(x0, x1, N)
    l = np.linspace(0, 1, N)
    return l, get_rgb(im, y2, x2, order=order)


def bresenham_colormapping(x0, y0, x1, y1, im):
    """
    Get lineout from x0/y0 to x1/y1 with points taken using Bresenham's ray
    tracing algorithm.  Since Bresenham ray tracing only provides a list of
    pixel coordiantes, this returns the distance between the each pixel and the
    start pixel, then projected to the line between start and end.

    Takes the image array

    Returns
    -------

    l : ndarray, shape=(N,)
        normalized location of colors
    rgb : ndarray, shape=(N,3)
        sequence of colors at each point in l

    """
    x_y = bresenham_trace(x0, y0, x1, y1)
    jj, ii = zip(*x_y)
    rgb = im[ii, jj]

    centers = np.vstack((ii, jj)).T
    points = np.array(centers - centers[0], dtype=float)
    line = centers[-1] - centers[0]
    l = np.dot(points, line)
    l /= l[-1]
    return l, rgb


def get_rgb(im, y, x, order=1):
    im = np.asarray(im)
    ni, nj, nc = im.shape
    points = np.zeros((len(x), nc), dtype=im.dtype)
    for c in range(nc):
        points[:, c] = map_coordinates(im[:, :, c], [y, x], order=order)
    points[0, :] = im[int(y[0]), int(x[0])]
    points[-1, :] = im[int(y[-1]), int(x[-1])]
    return points
