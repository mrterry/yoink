from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button

from yoink.widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                           RecoloredWidget, ScaledColorbar, Dumper)
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


def run(pixels):
    """
    """
    # Return the widgets or they stop responding
    widgets = {}

    # generate layout of figures and axes
    # there should be two figures: one for (sub)selecting data
    # and another for annotating that data with numbers
    sel_fig, sel_axes = make_selector_figure()
    ann_fig, ann_axes = make_annotate_figure()

    # plot source data
    sel_axes['img'].imshow(pixels, interpolation='none', vmin=0, vmax=1)

    # add shutters for cropping
    crop_widget = ShutterCrop(sel_axes['img'])
    widgets['crop_widget'] = crop_widget

    # add a line to identify the colormap on the selector fig
    cbar_select = DragableColorLine(sel_axes['img'], sel_axes['cbar'], pixels)
    widgets['cbar_select'] = cbar_select

    # using the shutters in crop_widget, re-plot only selected data
    rcol_widget = RecoloredWidget(ann_axes['img'], pixels)
    widgets['rcol_widget'] = rcol_widget
    # generate textboxes for specifying xlim, ylim
    rcol_widget.make_xyextent_textboxes(ann_axes['xlo'],
                                        ann_axes['xhi'],
                                        ann_axes['ylo'],
                                        ann_axes['yhi'])

    cbar_widget = ScaledColorbar(ann_axes['cbar'], rcol_widget.image)
    widgets['cbar_widget'] = cbar_widget

    tblo = TextBoxFloat(ann_axes['cbar_lo'], '0')
    tbhi = TextBoxFloat(ann_axes['cbar_hi'], '1')
    tblo.on_changed(cbar_widget.set_min)
    tbhi.on_changed(cbar_widget.set_max)
    widgets['tb_lo'] = tblo
    widgets['tb_hi'] = tbhi

    # update if the shutters move
    crop_widget.on_changed(rcol_widget.crop)
    # re-digitizing is expensive, so only do it when you're done dragging
    cbar_select.on_release(rcol_widget.digitize)
    rcol_widget.digitize(cbar_select.l, cbar_select.rgb)

    # button to dump the data to a file
    dump_widget = Dumper(rcol_widget, cbar_widget)
    widgets['dumper'] = dump_widget
    dump_button = Button(ann_axes['dump'], 'Dump to file')
    dump_button.on_clicked(dump_widget.dump)
    widgets['dump_button'] = dump_button

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

    select_radio = RadioButtons(sel_axes['select'],
                                labels=states.keys(),
                                active=0)
    select_radio.on_clicked(toggle_state)
    widgets['radio'] = select_radio

    # Return all the widgets or they stop working.  Garbage collection problem?
    return widgets
