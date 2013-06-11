from collections import OrderedDict

from matplotlib.widgets import RadioButtons, Button

from yoink.layout import make_selector_figure, make_annotate_figure
from yoink.widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                           ManualColorbar, RecoloredWidget)


def run(pixels):
    """
    """
    # generate layout of figures and axes
    # there should be two figures: one for (sub)selecting data
    # and another for annotating that data with numbers
    sel_fig, sel_axes = make_selector_figure()
    ann_fig, ann_axes = make_annotate_figure()

    # plot source data
    sel_axes['img'].imshow(pixels, interpolation='none')

    # add shutters for cropping
    crop_widget = ShutterCrop(sel_axes['img'])

    # add a line to identify the colormap on the selector fig
    cbar_select = DragableColorLine(sel_axes['img'], sel_axes['cbar'], pixels)
    # echo the selected cbar, but now add a scale
    cbar_widget = ManualColorbar(ann_axes['cbar'],
                                 ann_axes['cbar_lo'],
                                 ann_axes['cbar_hi'],
                                 cbar_select.l, cbar_select.rgb)
    # update the colors in cbar_widget when you move the selector line
    cbar_select.on_changed(cbar_widget.set_color)

    # using the shutters in crop_widget, re-plot only selected data
    rcol_widget = RecoloredWidget(ann_axes['img'], pixels)
    # generate textboxes for specifying xlim, ylim
    rcol_widget.make_xyextent_textboxes(ann_axes['xlo'],
                                        ann_axes['xhi'],
                                        ann_axes['ylo'],
                                        ann_axes['yhi'])
    # update if the shutters move
    crop_widget.on_changed(rcol_widget.crop)
    # re-digitizing is expensive, so only do it when you're done dragging
    cbar_select.on_release(rcol_widget.digitize)
    rcol_widget.digitize(cbar_select.l, cbar_select.rgb)

    # button to dump teh data to a file
    dump_button = Button(ann_axes['dump'], 'Dump to file')
    dump_button.on_clicked(rcol_widget.dump)

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

    # Return all the widgets or they stop working.  Garbage collection problem?
    return crop_widget, cbar_select, cbar_widget, rcol_widget, select_radio
