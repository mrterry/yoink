from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button
import numpy as np

from yoink.widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                           RecoloredWidget, ScaledColorbar)
from yoink.textbox import TextBoxFloat


class CmapExtractor(object):
    """
    Run the app for extracting data from a pseudo-color ("false-color",
    "colormapped") image.
    Generates two figures: a selector figures and an annotation figure.

    Parameters
    ----------

    pixels: array-like
        The pixels for the image to extract data from

    path: str
        The filename to save data.
    """
    def __init__(self, pixels, path):
        self.path = path
        # generate layout of figures and axes
        # there should be two figures: one for (sub)selecting data
        # and another for annotating that data with numbers
        self.sel_fig, self.sel_axes = self.create_selector_figure()
        self.ann_fig, self.ann_axes = self.create_annotate_figure()

        #
        # Set up the widgets on the selection figure
        #
        # plot source data
        self.select_image = self.sel_axes['img'].imshow(pixels,
                                                        interpolation='none',
                                                        vmin=0,
                                                        vmax=1)

        # add shutters for cropping, initially disabled
        self.crop_widget = ShutterCrop(self.sel_axes['img'])
        self.crop_widget.active = False
        self.crop_widget.set_visible(False)

        # add a line to identify manually select the colorbar
        self.cbar_select = DragableColorLine(self.sel_axes['img'],
                                             self.sel_axes['cbar'],
                                             pixels)
        self.cbar_select.active = False
        self.cbar_select.set_visible(False)

        # Radio buttons to select which Widget is active
        self.create_selector_toggle()

        #
        # Now set up widgets on the annotation figure
        #
        # We are converting a multi-color image to a scalar image.
        # Plot that scalar image
        self.rcol_widget = RecoloredWidget(self.ann_axes['img'], pixels)
        self.rcol_image = self.rcol_widget.image
        # fill axes with textboxes for typing in the x & y limits
        # these set the scale of x and y
        self.rcol_widget.make_xyextent_textboxes(self.ann_axes['xlo'],
                                                 self.ann_axes['xhi'],
                                                 self.ann_axes['ylo'],
                                                 self.ann_axes['yhi'])

        # Crop the re-colored image when the cropping shutters move
        self.crop_widget.on_changed(self.rcol_widget.crop)

        # Draw a colorbar for the re-colored image, and set the initial cmap
        self.cbar_widget = ScaledColorbar(self.ann_axes['cbar'],
                                          self.rcol_widget.image)
        self.rcol_widget.digitize(self.cbar_select.l, self.cbar_select.rgb)

        # Re-draw the colormap when the colorbar-selector moves
        # re-digitizing is expensive, so only do it when you release the mouse
        self.cbar_select.on_release(self.rcol_widget.digitize)

        self.create_cbar_textboxes()  # colorbar text boxes

        # Add a button to dump the data to a file
        self.dump_button = Button(self.ann_axes['dump'], 'Dump to file')
        self.dump_func = self.dump_npz
        self.dump_button.on_clicked(self.dump)

    def create_cbar_textboxes(self):
        """Create textbox widgets to manually specifying the range of z"""
        self.textboxes = {}
        clo = TextBoxFloat(self.ann_axes['cbar_lo'], '0')
        chi = TextBoxFloat(self.ann_axes['cbar_hi'], '1')
        # If the textbox changes, propagate those changes to the colorbar ticks
        clo.on_changed(self.cbar_widget.set_min)
        chi.on_changed(self.cbar_widget.set_max)
        self.textboxes['cbar_lo'] = clo
        self.textboxes['cbar_hi'] = chi

    def toggle_state(self, new_state):
        """Change the active selector widget"""
        assert new_state in self.selector_widgets
        for k in self.selector_widgets:
            if k == new_state:
                continue
            self.selector_widgets[k].active = False
            self.selector_widgets[k].set_visible(False)
        self.selector_widgets[new_state].active = True
        self.selector_widgets[new_state].set_visible(True)

    def create_selector_toggle(self):
        self.selector_widgets = OrderedDict()
        self.selector_widgets['Do nothing'] = NothingWidget()
        self.selector_widgets['Select Colorbar'] = self.cbar_select
        self.selector_widgets['Crop Image'] = self.crop_widget

        self.toggle_state('Do nothing')

        self.select_radio = RadioButtons(self.sel_axes['select'],
                                         labels=self.selector_widgets.keys(),
                                         active=0)
        self.select_radio.on_clicked(self.toggle_state)

    def dump_npz(self):
        data = self.get_data()
        print 'dumping to', self.path
        np.savez(self.path, **data)
        print 'dumped'

    def dump_txt(self):
        data = self.get_data()
        print 'dumping to', self.path, + '.*.txt'
        for key, val in data:
            np.savetxt('%s.%s.txt' % (self.path, key), val)
        print 'dumped'

    def dump(self, event):
        self.dump_func()

    def get_data(self):
        # The rcol_image knows about x, y.  z should go from 0-1
        data = {}
        z = np.array(self.rcol_image._A)

        ni, nj = z.shape
        x0, x1, y0, y1 = self.rcol_image.get_extent()
        x = np.linspace(x0, x1, ni+1)
        y = np.linspace(y0, y1, nj+1)
        if self.rcol_image.origin == 'upper':
            y = y[::-1]
        data['x'] = x
        data['y'] = y

        # The colorbar lies about the range of z (by design)
        # correct z based on what the colorbar says
        zmin = self.cbar_widget.fmt.mn
        zmax = self.cbar_widget.fmt.mx
        dz = zmax - zmin
        z = zmin + dz * z
        data['z'] = z

        data['l'] = self.cbar_select.l
        data['rgb'] = self.cbar_select.rgb
        return data

    def create_selector_figure(self, gut=0.04, sepx=0.01, wide=0.2, tall=0.3,
                               dx_cbar=0.05, **ax_kwargs):
        fig = plt.figure()
        axes = {}

        x0 = gut + wide + sepx
        x1 = 1 - (gut + dx_cbar + sepx)

        y0 = gut
        y1 = 1 - gut

        l, b = x0, y0
        w, h = x1 - x0, y1 - y0
        img = fig.add_axes([l, b, w, h], **ax_kwargs)
        img.yaxis.set_visible(False)
        img.xaxis.set_visible(False)
        axes['img'] = img

        l, b = x1 + sepx, y0
        w, h = dx_cbar, y1 - y0
        cbar = fig.add_axes([l, b, w, h], **ax_kwargs)
        cbar.yaxis.set_visible(False)
        cbar.xaxis.set_visible(False)
        axes['cbar'] = cbar

        l, b = gut, 0.5 * (y0 + y1 - tall)
        w, h = wide, tall
        select = fig.add_axes([l, b, w, h], **ax_kwargs)
        select.yaxis.set_visible(False)
        select.xaxis.set_visible(False)
        axes['select'] = select

        return fig, axes

    def create_annotate_figure(self, gut=0.04, sepx=0.05, sepy=0.04,
                               wide=0.09, tall=0.06, dx_cbar=0.05,
                               **ax_kwargs):
        fig = plt.figure()
        axes = {}

        x0 = gut + wide + sepx
        x1 = 1 - (gut + max(dx_cbar, wide) + sepx)

        y0 = gut + tall + sepy
        y1 = 1 - gut

        l, b = x0, y0
        w, h = x1 - x0, y1 - y0
        axes['img'] = fig.add_axes([l, b, w, h], **ax_kwargs)

        sizes = {}
        sizes['cbar'] = (x1+sepx, gut+tall+sepy, dx_cbar, y1-y0-tall-sepy)
        sizes['cbar_lo'] = (x1+sepx, gut, wide, tall)
        sizes['cbar_hi'] = (x1+sepx, y1-tall, wide, tall)
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
