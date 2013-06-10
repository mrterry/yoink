from collections import OrderedDict

from matplotlib.widgets import RadioButtons, Button

from yoink.layout import make_selector_figure, make_annotate_figure
from yoink.widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                           ScaledCmap, RecoloredWidget)


def run(pixels):
    """
    """
    # generate layout of figures and axes
    # there should be two figures: one for (sub)selecting data
    # and another for annotating that data with numbers
    sel_fig, sel_axes = make_selector_figure()
    ann_fig, ann_axes = make_annotate_figure()

    # plot source data
    sel_axes['img'].imshow(pixels)

    # add shutters for cropping
    crop_widget = ShutterCrop(sel_axes['img'])

    # add a line to identify the colormap on the selector fig
    cmap_select = DragableColorLine(sel_axes['img'], sel_axes['cmap'], pixels)
    # echo the selected cmap, but now add a scale
    cmap_scale = ScaledCmap(ann_axes['cmap'],
                            ann_axes['cmap_lo'],
                            ann_axes['cmap_hi'],
                            cmap_select.l, cmap_select.rgb)
    # update the colors in cmap_scale when you move the selector line
    set_color = lambda: cmap_scale.set_color(cmap_select.l, cmap_select.rgb)
    cmap_select.on_changed(set_color)

    # using the shutters in crop_widget, re-plot only selected data
    rcol_widget = RecoloredWidget(ann_axes['img'], pixels, crop_widget)
    # generate textboxes for specifying xlim, ylim
    rcol_widget.make_xyextent_textboxes(ann_axes['xlo'],
                                        ann_axes['xhi'],
                                        ann_axes['ylo'],
                                        ann_axes['yhi'])
    # update if the shutters move
    crop_widget.on_changed(rcol_widget.crop)
    digitize = lambda: rcol_widget.digitize(cmap_select.l, cmap_select.rgb)
    cmap_select.on_changed(digitize)

    # button to dump teh data to a file
    dump_button = Button(ann_axes['dump'], 'Dump to file')
    dump_button.on_clicked(rcol_widget.dump)

    # Radio buttons to select which Widget is active
    states = OrderedDict()
    states = {}
    states['Do nothing'] = NothingWidget()
    states['Do nothing2'] = NothingWidget()
    states['Select Colorbar'] = cmap_select
    states['Crop Image'] = crop_widget

    def toggle_state(new_state):
        print 'toggline', new_state
        assert new_state in states
        for k in states:
            if k == new_state:
                continue
            print 'disabling', k
            states[k].active = False
            states[k].set_visible(False)
        print 'enabling', new_state
        states[new_state].active = True
        states[new_state].set_visible(True)
    toggle_state(states.keys()[0])

    select_radio = RadioButtons(sel_axes['select'],
                                labels=states.keys(),
                                active=0)
    select_radio.on_clicked(toggle_state)

    # Return all the widgets or they stop working.  Garbage collection problem?
    return crop_widget, cmap_select, cmap_scale, rcol_widget, select_radio
