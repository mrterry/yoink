# all stolen from skimage
import warnings

import numpy as np
from scipy import ndimage


def _compute_harris_response(image, eps=1e-6, gaussian_deviation=1):
    """Compute the Harris corner detector response function
    for each pixel in the image

    Parameters
    ----------
    image : ndarray of floats
    Input image.

    eps : float, optional
    Normalisation factor.

    gaussian_deviation : integer, optional
    Standard deviation used for the Gaussian kernel.

    Returns
    --------
    image : (M, N) ndarray
    Harris image response
    """
    if len(image.shape) == 3:
        image = image.mean(axis=2)

    # derivatives
    image = ndimage.gaussian_filter(image, gaussian_deviation)
    imx = ndimage.sobel(image, axis=0, mode='constant')
    imy = ndimage.sobel(image, axis=1, mode='constant')

    Wxx = ndimage.gaussian_filter(imx * imx, 1.5, mode='constant')
    Wxy = ndimage.gaussian_filter(imx * imy, 1.5, mode='constant')
    Wyy = ndimage.gaussian_filter(imy * imy, 1.5, mode='constant')

    # determinant and trace
    Wdet = Wxx * Wyy - Wxy**2
    Wtr = Wxx + Wyy
    # Alternate formula for Harris response.
    # Alison Noble, "Descriptions of Image Surfaces", PhD thesis (1989)
    harris = Wdet / (Wtr + eps)

    return harris


def corner_harris(image, min_distance=10, threshold=0.1, eps=1e-6,
           gaussian_deviation=1):
    """
    Return corners from a Harris response image

    Parameters
    ----------
    image : ndarray of floats
    Input image.

    min_distance : int, optional
    Minimum number of pixels separating interest points and image boundary.

    threshold : float, optional
    Relative threshold impacting the number of interest points.

    eps : float, optional
    Normalisation factor.

    gaussian_deviation : integer, optional
    Standard deviation used for the Gaussian kernel.

    Returns
    -------
    coordinates : (N, 2) array
    (row, column) coordinates of interest points.
    """
    harrisim = _compute_harris_response(image, eps=eps,
                                        gaussian_deviation=gaussian_deviation)
    coordinates = peak_local_max(harrisim, min_distance=min_distance,
                                      threshold_rel=threshold)
    return coordinates


def peak_local_max(image, min_distance=10, threshold='deprecated',
                   threshold_abs=0, threshold_rel=0.1, num_peaks=np.inf):
    """Return coordinates of peaks in an image.

    Peaks are the local maxima in a region of `2 * min_distance + 1`
    (i.e. peaks are separated by at least `min_distance`).

    NOTE: If peaks are flat (i.e. multiple pixels have exact same intensity),
    the coordinates of all pixels are returned.

    Parameters
    ----------
    image : ndarray of floats
    Input image.
    min_distance : int
    Minimum number of pixels separating peaks and image boundary.
    threshold : float
    Deprecated. See `threshold_rel`.
    threshold_abs : float
    Minimum intensity of peaks.
    threshold_rel : float
    Minimum intensity of peaks calculated as `max(image) * threshold_rel`.
    num_peaks : int
    Maximum number of peaks. When the number of peaks exceeds `num_peaks`,
    return `num_peaks` coordinates based on peak intensity.

    Returns
    -------
    coordinates : (N, 2) array
    (row, column) coordinates of peaks.

    Notes
    -----
    The peak local maximum function returns the coordinates of local peaks (maxima)
    in a image. A maximum filter is used for finding local maxima. This operation
    dilates the original image. After comparison between dilated and original image,
    peak_local_max function returns the coordinates of peaks where
    dilated image = original.
    """
    if np.all(image == image.flat[0]):
        return []
    image = image.copy()
    # Non maximum filter
    size = 2 * min_distance + 1
    image_max = ndimage.maximum_filter(image, size=size, mode='constant')
    mask = (image == image_max)
    image *= mask

    # Remove the image borders
    image[:min_distance] = 0
    image[-min_distance:] = 0
    image[:, :min_distance] = 0
    image[:, -min_distance:] = 0

    if not threshold == 'deprecated':
        msg = "`threshold` parameter deprecated; use `threshold_rel instead."
        warnings.warn(msg, DeprecationWarning)
        threshold_rel = threshold
    # find top peak candidates above a threshold
    peak_threshold = max(np.max(image.ravel()) * threshold_rel, threshold_abs)
    image_t = (image > peak_threshold) * 1

    # get coordinates of peaks
    coordinates = np.transpose(image_t.nonzero())

    if coordinates.shape[0] > num_peaks:
        intensities = image[coordinates[:, 0], coordinates[:, 1]]
        idx_maxsort = np.argsort(intensities)[::-1]
        coordinates = coordinates[idx_maxsort][:num_peaks]

    return coordinates


def approximate_polygon(coords, tolerance):
    """
    Approximate a polygonal chain with the specified tolerance.

    It is based on the Douglas-Peucker algorithm.

    Note that the approximated polygon is always within the convex hull of the
    original polygon.

    Parameters
    ----------
    coords : (N, 2) array
    Coordinate array.
    tolerance : float
    Maximum distance from original points of polygon to approximated
    polygonal chain. If tolerance is 0, the original coordinate array
    is returned.

    Returns
    -------
    coords : (M, 2) array
    Approximated polygonal chain where M <= N.

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
    """
    if tolerance <= 0:
        return coords

    chain = np.zeros(coords.shape[0], 'bool')
    # pre-allocate distance array for all points
    dists = np.zeros(coords.shape[0])
    chain[0] = True
    chain[-1] = True
    pos_stack = [(0, chain.shape[0] - 1)]
    end_of_chain = False

    while not end_of_chain:
        start, end = pos_stack.pop()
        # determine properties of current line segment
        r0, c0 = coords[start, :]
        r1, c1 = coords[end, :]
        dr = r1 - r0
        dc = c1 - c0
        segment_angle = - np.arctan2(dr, dc)
        segment_dist = c0 * np.sin(segment_angle) + r0 * np.cos(segment_angle)

        # select points in-between line segment
        segment_coords = coords[start + 1:end, :]
        segment_dists = dists[start + 1:end]

        # check whether to take perpendicular or euclidean distance with
        # inner product of vectors

        # vectors from points -> start and end
        dr0 = segment_coords[:, 0] - r0
        dc0 = segment_coords[:, 1] - c0
        dr1 = segment_coords[:, 0] - r1
        dc1 = segment_coords[:, 1] - c1
        # vectors points -> start and end projected on start -> end vector
        projected_lengths0 = dr0 * dr + dc0 * dc
        projected_lengths1 = - dr1 * dr - dc1 * dc
        perp = np.logical_and(projected_lengths0 > 0,
                              projected_lengths1 > 0)
        eucl = np.logical_not(perp)
        segment_dists[perp] = np.abs(
            segment_coords[perp, 0] * np.cos(segment_angle)
            + segment_coords[perp, 1] * np.sin(segment_angle)
            - segment_dist
        )
        segment_dists[eucl] = np.minimum(
            # distance to start point
            np.sqrt(dc0[eucl] ** 2 + dr0[eucl] ** 2),
            # distance to end point
            np.sqrt(dc1[eucl] ** 2 + dr1[eucl] ** 2)
        )

        if np.any(segment_dists > tolerance):
            # select point with maximum distance to line
            new_end = start + np.argmax(segment_dists) + 1
            pos_stack.append((new_end, end))
            pos_stack.append((start, new_end))
            chain[new_end] = True

        if len(pos_stack) == 0:
            end_of_chain = True

    return coords[chain, :]
