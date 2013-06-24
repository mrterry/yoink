from __future__ import division, print_function
from collections import OrderedDict

from yoink.widgets import DeformableLine, ShutterCrop, NothingWidget

from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt


class LinePicker(object):
    def __init__(self, pixels, path):
        self.sel_fig, self.sel_axes = self.create_selector_figure()
        self.ann_fig, self.ann_axes = self.create_annotate_figure()

        self.select_image = self.sel_axes['img'].imshow(pixels)

        self.crop_widget = ShutterCrop(self.sel_axes['img'])
        self.crop_widget.active = False
        self.crop_widget.set_visible(False)

        line_kw = dict(linewidth=0.5, color='k', alpha=0.5)
        circle_kw = dict(radius=15, alpha=0.5)
        self.seg_line = DeformableLine(self.sel_axes['img'],
                                       grows=True, shrinks=True,
                                       line_kw=line_kw, circle_kw=circle_kw)
        self.seg_line.active = False
        self.seg_line.set_visible(True)

        self.create_selector_toggle()

        self.path = path

    def create_selector_toggle(self):
        self.selector_widgets = OrderedDict()
        self.selector_widgets['Do nothing'] = NothingWidget()
        self.selector_widgets['Segmented Line'] = self.seg_line

        self.toggle_state('Do nothing')

        self.select_radio = RadioButtons(self.sel_axes['select'],
                                         labels=self.selector_widgets.keys(),
                                         active=0)
        self.select_radio.on_clicked(self.toggle_state)

    def toggle_state(self, new_state):
        """Change the active selector widget"""
        assert new_state in self.selector_widgets
        for k in self.selector_widgets:
            if k == new_state:
                continue
            self.selector_widgets[k].active = False
#            self.selector_widgets[k].set_visible(False)
        self.selector_widgets[new_state].active = True
#        self.selector_widgets[new_state].set_visible(True)

    def create_selector_figure(self, gut=0.04, sepx=0.01, wide=0.2, tall=0.3,
                               **ax_kwargs):
        fig = plt.figure()
        axes = {}

        x0 = gut + wide + sepx
        x1 = 1 - (gut + sepx)

        y0 = gut
        y1 = 1 - gut

        l, b = x0, y0
        w, h = x1 - x0, y1 - y0
        img = fig.add_axes([l, b, w, h], **ax_kwargs)
        img.yaxis.set_visible(False)
        img.xaxis.set_visible(False)
        axes['img'] = img

        l, b = gut, 0.5 * (y0 + y1 - tall)
        w, h = wide, tall
        select = fig.add_axes([l, b, w, h], **ax_kwargs)
        select.yaxis.set_visible(False)
        select.xaxis.set_visible(False)
        axes['select'] = select

        return fig, axes

    def create_annotate_figure(self, gut=0.04, sepx=0.05, sepy=0.04,
                               wide=0.09, tall=0.06,
                               **ax_kwargs):
        fig = plt.figure()
        axes = {}

        x0 = gut + wide + sepx
        x1 = 1 - (gut + sepx)

        y0 = gut + tall + sepy
        y1 = 1 - gut

        l, b = x0, y0
        w, h = x1 - x0, y1 - y0
        axes['img'] = fig.add_axes([l, b, w, h], **ax_kwargs)

        sizes = {}
        sizes['yhi'] = (gut, 1-gut-tall, wide, tall)
        sizes['ylo'] = (gut, gut+tall+sepy, wide, tall)
        sizes['xlo'] = (x0, gut, wide, tall)
        sizes['xhi'] = (x1-wide, gut, wide, tall)
        sizes['dump'] = (x0+wide+sepx, gut, x1-x0-2*(sepx+wide), tall)

        for name, lbwh in sizes.iteritems():
            ax = fig.add_axes(lbwh, **ax_kwargs)
            ax.yaxis.set_visible(False)
            ax.xaxis.set_visible(False)
            axes[name] = ax

        return fig, axes
