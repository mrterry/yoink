from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button

from yoink.widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                           RecoloredWidget, ScaledColorbar, ImageDumper)
from yoink.textbox import TextBoxFloat


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
    cbar = fig.add_axes([l, b, w, h])
    cbar.yaxis.set_visible(False)
    cbar.xaxis.set_visible(False)
    axes['cbar'] = cbar

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
    cbar = fig.add_axes([l, b, w, h])
    cbar.yaxis.set_visible(False)
    cbar.xaxis.set_visible(False)
    axes['cbar'] = cbar

    l, b = x1 + sepx, gut
    w, h = wide, tall
    clo = fig.add_axes([l, b, w, h])
    clo.yaxis.set_visible(False)
    clo.xaxis.set_visible(False)
    axes['cbar_lo'] = clo

    l, b = x1 + sepx, y1 - tall
    w, h = wide, tall
    chi = fig.add_axes([l, b, w, h])
    chi.yaxis.set_visible(False)
    chi.xaxis.set_visible(False)
    axes['cbar_hi'] = chi

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


def run(pixels, path):
    """
    """
    # Return the widgets or they stop responding
    widgets = {}

    # generate layout of figures and axes
    # there should be two figures: one for (sub)selecting data
    # and another for annotating that data with numbers
    sel_fig, sel_axes = make_selector_figure()
    ann_fig, ann_axes = make_annotate_figure()

    #
    # Set up the widgets on the selection figure
    #
    # plot source data
    sel_axes['img'].imshow(pixels, interpolation='none', vmin=0, vmax=1)

    # add shutters for cropping, initially disabled
    widgets['crop_widget'] = crop_widget = ShutterCrop(sel_axes['img'])
    crop_widget.active = False
    crop_widget.set_visible(False)

    # add a line to identify manually select the colorbar, initially disabled
    widgets['cbar_select'] = cbar_select = DragableColorLine(sel_axes['img'],
                                                             sel_axes['cbar'],
                                                             pixels)
    cbar_select.active = False
    cbar_select.set_visible(False)

    # Radio buttons to select which Widget is active
    states = OrderedDict()
    states['Do nothing'] = NothingWidget()
    states['Select Colorbar'] = cbar_select
    states['Crop Image'] = crop_widget

    def toggle_state(new_state):
        assert new_state in states
        for k in states:
            if k == new_state:
                continue
            states[k].active = False
            states[k].set_visible(False)
        states[new_state].active = True
        states[new_state].set_visible(True)
    toggle_state(states.keys()[0])

    widgets['radio'] = select_radio = RadioButtons(sel_axes['select'],
                                                   labels=states.keys(),
                                                   active=0)
    select_radio.on_clicked(toggle_state)

    #
    # Now set up widgets on the annotation figure
    #
    # We are converting a multi-color image to a scalar image.
    # Plot that scalar image
    widgets['rcol_widget'] = rcol_widget = RecoloredWidget(ann_axes['img'],
                                                           pixels)
    # fill axes with textboxes for typing in the x & y limits
    # these set the scale of x and y
    rcol_widget.make_xyextent_textboxes(ann_axes['xlo'],
                                        ann_axes['xhi'],
                                        ann_axes['ylo'],
                                        ann_axes['yhi'])

    # Crop the re-colored image when the cropping shutters move
    crop_widget.on_changed(rcol_widget.crop)

    # Draw a colorbar for the re-colored image, and set the initial cmap
    widgets['cbar_widget'] = cbar_widget = ScaledColorbar(ann_axes['cbar'],
                                                          rcol_widget.image)
    rcol_widget.digitize(cbar_select.l, cbar_select.rgb)

    # Re-draw the colormap when the colorbar-selector moves
    # re-digitizing is expensive, so only do it when you release the mouse
    cbar_select.on_release(rcol_widget.digitize)

    # Create textbox widgets to manually specifying the range of z
    widgets['tb_lo'] = tblo = TextBoxFloat(ann_axes['cbar_lo'], '0')
    widgets['tb_hi'] = tbhi = TextBoxFloat(ann_axes['cbar_hi'], '1')
    # If the textbox changes, propagate those changes to the colorbar ticks
    tblo.on_changed(cbar_widget.set_min)
    tbhi.on_changed(cbar_widget.set_max)

    # Add a button to dump the data to a file
    widgets['dump_button'] = dump_button = Button(ann_axes['dump'],
                                                  'Dump to file')
    widgets['dumper'] = dumper = ImageDumper(rcol_widget.image,
                                             cbar_widget,
                                             path)
    dump_button.on_clicked(dumper.dump_npz)

    # Return all the widgets.  If you don't, they don't respond interactively.
    # Maybe they are getting garbage collected?
    return widgets
