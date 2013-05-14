import numpy as np
from scipy.optimize import leastsq


def CornerInterp(pixel_xy, data_xy):
    """
    Given pixel coordinates and equivalent data coordinates, return a function
    that interpolates points in pixel space to points in data space.
    """
    A = np.zeros((len(pixel_xy), 3))
    A[:, 1:] = pixel_xy
    coefs, res, rank, s = np.linalg.lstsq(A, data_xy)
    coefs = coefs.T

    def f(px, py):
        # coerce px to array
        if not hasattr(px, '__len__'):
            px = [px]
        if not hasattr(py, '__len__'):
            py = [py]
        n = len(px)

        b = np.ones((3, n))
        b[1, :] = px
        b[2, :] = py
        ans = np.dot(coefs, b)
        return ans

    return f


def invert_cmap_leastsq(pix, l, colors):
    """
    Given a sequence of pixels, convert each to an equivalent index in the
    color sequence l, colors

    Performs a least squares minimization of the error to find the index.
    color(f) is interpolated.  Error is quadrature sum of color erros.
    """
    pix = pix[..., :3]  # only want rgb
    shape = pix.shape

    ans = np.zeros(list(shape)[:-1], dtype=float)

    def residuals(f, RGB):
        return [np.interp(f, l, colors[:, i]) - RGB[i] for i in range(3)]

    guess = 0.5
    it = np.nditer(pix[..., 0], flags=['multi_index'])
    while not it.finished:
        index = it.multi_index
        # use the answer from the previous iteration to guess the next answer
        guess, stuff = leastsq(residuals, guess, args=(pix[index],))
        ans[index] = guess  
        it.iternext()

    return ans


def invert_cmap_argmin(pix, l, colors):
    """
    Given a sequence of pixels, convert each to an equivalent index in the
    color sequence l, colors

    Finds the error between the target pixes and all colors in the cmap.
    Picks the color with the smallest error.
    Error is quadrature sum of color erros.
    """
    pix = pix[..., :3]  # only want rgb
    shape = pix.shape

    ans = np.zeros(list(shape)[:-1], dtype=float)

    it = np.nditer(pix[..., 0], flags=['multi_index'])
    while not it.finished:
        index = it.multi_index

        err = colors - pix[index]
        err = np.sum(err*err, axis=1)
        ans[index] = l[err.argmin()]
        it.iternext()

    return ans
