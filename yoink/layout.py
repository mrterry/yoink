import pylab as plt


def make_selector_figure(gut=0.04, sepx=0.01, wide=0.2, tall=0.3,
                         dx_cbar=0.05):
    fig = plt.figure()
    axes = {}

    x0 = gut + wide + sepx
    x1 = 1 - (gut + dx_cbar + sepx)

    y0 = gut
    y1 = 1 - gut

    l, b = x0, y0
    w, h = x1 - x0, y1 - y0
    img = fig.add_axes([l, b, w, h])
    img.yaxis.set_visible(False)
    img.xaxis.set_visible(False)
    axes['img'] = img

    l, b = x1 + sepx, y0
    w, h = dx_cbar, y1 - y0
    cmap = fig.add_axes([l, b, w, h])
    cmap.yaxis.set_visible(False)
    cmap.xaxis.set_visible(False)
    axes['cmap'] = cmap

    l, b = gut, 0.5 * (y0 + y1 - tall)
    w, h = wide, tall
    select = fig.add_axes([l, b, w, h])
    select.yaxis.set_visible(False)
    select.xaxis.set_visible(False)
    axes['select'] = select

    return fig, axes


def make_annotate_figure(gut=0.04, sepx=0.05, sepy=0.04,
                         wide=0.09, tall=0.06, dx_cbar=0.05):
    fig = plt.figure()
    axes = {}

    x0 = gut + wide + sepx
    x1 = 1 - (gut + max(dx_cbar, wide) + sepx)

    y0 = gut + tall + sepy
    y1 = 1 - gut

    l, b = x0, y0
    w, h = x1 - x0, y1 - y0
    axes['img'] = fig.add_axes([l, b, w, h])

    l, b = x1 + sepx, gut + tall + sepy
    w, h = dx_cbar, y1 - y0 - tall - sepy
    cmap = fig.add_axes([l, b, w, h])
    cmap.yaxis.set_visible(False)
    cmap.xaxis.set_visible(False)
    axes['cmap'] = cmap

    l, b = x1 + sepx, gut
    w, h = wide, tall
    clo = fig.add_axes([l, b, w, h])
    clo.yaxis.set_visible(False)
    clo.xaxis.set_visible(False)
    axes['cmap_lo'] = clo

    l, b = x1 + sepx, y1 - tall
    w, h = wide, tall
    chi = fig.add_axes([l, b, w, h])
    chi.yaxis.set_visible(False)
    chi.xaxis.set_visible(False)
    axes['cmap_hi'] = chi

    l, b = gut, 1 - gut - tall
    w, h = wide, tall
    yhi = fig.add_axes([l, b, w, h])
    yhi.yaxis.set_visible(False)
    yhi.xaxis.set_visible(False)
    axes['yhi'] = yhi

    l, b, = gut, gut + tall + sepy
    ylo = fig.add_axes([l, b, w, h])
    ylo.yaxis.set_visible(False)
    ylo.xaxis.set_visible(False)
    axes['ylo'] = ylo

    l, b = x0, gut
    xlo = fig.add_axes([l, b, w, h])
    xlo.yaxis.set_visible(False)
    xlo.xaxis.set_visible(False)
    axes['xlo'] = xlo

    l, b = x1 - wide, gut
    xhi = fig.add_axes([l, b, w, h])
    xhi.yaxis.set_visible(False)
    xhi.xaxis.set_visible(False)
    axes['xhi'] = xhi

    l, b = x0 + wide + sepx, gut
    w, h = x1 - x0 - 2 * (sepx + wide), tall
    dump = fig.add_axes([l, b, w, h])
    dump.yaxis.set_visible(False)
    dump.xaxis.set_visible(False)
    axes['dump'] = dump

    return fig, axes
