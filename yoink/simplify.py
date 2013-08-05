"""Functions for simplifying line segments"""
from __future__ import division

import numpy as np
from skimage import img_as_bool
#from skimage.morphology import skeletonize


def rdp_indexes(points, eps2, dist2=None):
    """Indexes of points kept using the Ramer-Douglas-Peucker algorithm.

    Parameters
    ----------
    points : array_like
        (n, m) n points in m dimensions
    eps2 : number
        (max allowable distance)**2
    dist2 : callable, optional
        dist to is a callable returns the square of the distance between a
        sequence of points and a line defined by its two endpoints.  defaults
        to point_line_dist2

    Returns
    -------
    indexes : list
        sorted list of indexes of kept points

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
    .. [2] Urs Ramer, "An iterative procedure for the polygonal approximation
           of plane curves", Computer Graphics and Image Processing, 1(3),
           244-256 (1972) doi:10.1016/S0146-664X(72)80017-0
    .. [3] David Douglas & Thomas Peucker, "Algorithms for the reduction of the
           number of points required to represent a digitized line or its
           caricature", The Canadian Cartographer 10(2), 112-122 (1973)
           doi:10.3138/FM57-6770-U75U-7727
    """
    dist2 = point_line_dist2 if dist2 is not None else point_line_dist2

    N = len(points)
    keep = [0, N-1]

    stack = [(0, N-1)]

    for i in xrange(N**2):
        if not stack:
            return sorted(keep)

        i0, i1 = stack.pop()
        if i1 <= i0+1:
            continue

        d = dist2(points[i0+1:i1], points[i0], points[i1])
        i = np.argmax(d)
        dmax = d[i]
        i += i0 + 1

        if dmax > eps2:
            keep.append(i)
            stack += [(i0, i), (i, i1)]

    assert False


def point_line_dist2(p, l1, l2):
    """Distance**2 between sequence of N, M-dimensional points and line l1-l2

    Parameters
    ----------
    p : array_like
        sequence of N, M-dimensional points. shape = (N, M)
    l1 : array_like
        start of line segment len == M
    l2 : array_like
        end of line segment len == M

    Returns
    -------
    dist2 : array_like
        distance**2 between each point and line. shape == N
    """
    p, l1, l2 = np.asarray(p), np.asarray(l1), np.asarray(l2)
    ap = l1 - p
    n = l2 - l1
    n /= np.sqrt(sum(n**2))
    dist = ap - np.outer(n, np.dot(ap, n)).T
    return np.sum(dist**2, 1)


def img2line(img):
    """Convert an image to a sequence of indexes

    Parameters
    ----------
    img : 2d array_like
        image to extract line from

    Returns
    -------
    iseq : array
        1d sequnce of i coordinates
    jseq : array
        1d sequnce of j coordinates
    """
    img = img_as_bool(img)
    Ns = sum(img, axis=1)
    N = sum(Ns)

    ni, nj = img.shape
    jrange = np.arange(nj)

    iseq = np.zeros(N, dtype=int)
    jseq = np.zeros(N, dtype=int)

    ii = iseq
    jj = jseq
    for i, n in enumerate(Ns):
        ii, ii[:n] = ii[:n], i
        jj, jj[:n] = jj[:n], jrange[img[i, :] == 1]

    assert not ii
    assert not jj

    return iseq, jseq
