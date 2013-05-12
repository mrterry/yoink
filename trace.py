from __future__ import division

import numpy as np
from scipy.interpolate import RectBivariateSpline


def naive_trace(x, y, x1, y1):
    """
    Matt Terry's naive tracing method.  No promises that this is fast,
    reliable, or good.
    """
    # TODO weird things happening at last step, negative step size
    i, j = int(x), int(y)
    ij_end = int(x1), int(y1)

    dx, dy = x1-x, y1-y
    di = -1 if dx < 0 else 1
    dj = -1 if dy < 0 else 1
    dist_left = np.sqrt(dx**2 + dy**2)
    ct, st = dx/dist_left, dy/dist_left
    # deal 1/0 issues due to ct == 0 or st == 0

    path = [(i, j, x, y)]
    max_step = int(abs(dx))+1 + int(abs(dy)) + 1
    for step in xrange(2*max_step):
        l1 = (j+dj - y)/st
        l2 = (i+di - x)/ct

        if l1 < l2:
            j += dj
            x += l1*ct
            y = j
        else:
            i += di
            x = i
            y += l2*st
        path.append((i, j, x, y))

        if (i, j) == ij_end:
            break
    else:
        assert False
    path.append((i, j, x1, y1))
    return path


def bresenham_trace(x, y, x1, y1):
    """
    http://en.wikipedia.org/wiki/Bresenham's_line_algorithm
    Bresenham, J. E. (1 January 1965). "Algorithm for computer control of a
    digital plotter". IBM Systems Journal 4 (1): 25–30.
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
        if (x, y)  == (x1, y1):
            break
        if e2 < dx:
            err += dx
            y += sy
    else:
        assert False
    return path


def wu_trace(x, y, x1, y1):
    """
    http://en.wikipedia.org/wiki/Xiaolin_Wu's_line_algorithm
    Wu, Xiaolin (July 1991). "An efficient antialiasing technique". Computer
    Graphics 25 (4): 143–152.
    """
    steep = abs(y1-y) > abs(x1-x)
    if steep:
        x, y = y, x
        x1, y1 = y1, x1

    if x > x1:
        x, x1 = x1, x
        y, y1 = y1, y

    dx = x1 - x
    dy = y1 - y
    grad = dy/dx

    # first endpoint
    xend = x_px_11 = int(x+0.5)
    yend = y + grad*(xend - x)
    xgap = wu_rfpart(x + 0.5)
    y_px_11 = int(yend)

    frac, rfrac = wu_frac(yend)
    steps = [
            (x_px_11, y_px_11, rfrac*xgap),
            (x_px_11, y_px_11+1, frac*xgap),
            ]
    intery = yend + grad

    # second endpoint
    xend = x_px_12 = int(x1+0.5)
    yend = y1 + grad * (xend - x1)
    xgap = wu_fpart(x1 + 0.5)
    y_px_12 = int(yend)

    # main loop
    for x in range(x_px_11+1, x_px_12):
        frac, rfrac = wu_frac(intery)
        y = int(intery)
        steps += [(x, y, rfrac), (x, y+1, frac)]
        intery += grad
    frac, rfrac = wu_frac(yend)
    steps += [
            (x_px_12, y_px_12, rfrac*xgap),
            (x_px_12, y_px_12+1, frac*xgap),
            ]

    if steep:
        steps = [(y, x, f) for (x, y, f) in steps]
    return steps


def wu_fpart(x):
    return x - int(x)


def wu_rfpart(x):
    return 1 - wu_fpart(x)


def wu_frac(x):
    frac = wu_fpart(x)
    return frac, 1-frac


def naive_colormaping(x0, y0, x1, y1, spline):
    """
    Get lineout from x0/y0 to x1/y1 with points takein from naive_trace ray
    tracing algorithm.
    Returns:
        l: ndarray, shape=(N,) - normalized location of colors
        rgb ndarray, shape=(N,3) - sequence of colors at each point in l
    """
    i_j_x_y = naive_trace(x0, y0, x1, y1)
    ii, jj, x, y = zip(*i_j_x_y)
    x, y = np.array(x), np.array(y)
    dx = x.max() - x.min() 
    dy = y.max() - y.min() 
    if dx > dy:
        l = (x - x.min())/dx
    else:
        l = (y - y.min())/dy
    rgb = spline.ev(y, x)
    return l, rgb


def equispaced_colormaping(x0, y0, x1, y1, spline, N=256):
    """
    Get lineout from x0/y0 to x1/y1 with equally spaced points.
    Returns:
        l: ndarray, shape=(N,) - normalized location of colors
        rgb ndarray, shape=(N,3) - sequence of colors at each point in l
    """
    y2 = np.linspace(y0, y1, N)
    x2 = np.linspace(x0, x1, N)
    l = np.linspace(0, 1, N)
    rgb = spline.ev(y2, x2)
    return l, rgb


def bresenham_colormapping(x0, y0, x1, y1, im):
    """
    Get lineout from x0/y0 to x1/y1 with points taken using Bresenham's ray
    tracing algorithm.
    Takes the image array rather than the spline fit
    Returns:
        l: ndarray, shape=(N,) - normalized location of colors
        rgb ndarray, shape=(N,3) - sequence of colors at each point in l
    """
    x_y = bresenham_trace(x0, y0, x1, y1)
    ii, jj = zip(*x_y)
    rgb = im[jj, ii]
    centers = np.vstack((ii, jj), dtype=float)
    centers += 0.5
    line = centers[-1] - centers[0]
    l = np.dot(centers, line.reshape(2,1))
    return l, rgb


class ColormappingSpline(object):
    def __init__(self, im, kx=1, ky=1):
        nj, ni, nc = im.shape
        jrange = np.arange(nj)
        irange = np.arange(ni)
        # TODO may be able to do this faster with custom implementation that
        # works on integers
        self.r_spline = RectBivariateSpline(jrange, irange, im[:, :, 0],
                kx=kx, ky=ky)
        self.g_spline = RectBivariateSpline(jrange, irange, im[:, :, 1],
                kx=kx, ky=ky)
        self.b_spline = RectBivariateSpline(jrange, irange, im[:, :, 2],
                kx=kx, ky=ky)
        return

    def ev(self, x, y):
        rgb = np.emty((len(x), 3))
        rgb[:, 0] = self.r_spline.ev(y, x)
        rgb[:, 1] = self.g_spline.ev(y, x)
        rgb[:, 2] = self.b_spline.ev(y, x)
        return rgb
