from __future__ import division, print_function
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button
import numpy as np

from .widgets import (ShutterCrop, DragableColorLine, NothingWidget,
                      RecoloredWidget, ScaledColorbar)
from .textbox import TextBoxFloat


class CmapExtractor(object):
    """
    Run the app for extracting data from a pseudo-color ("false-color",
    "colormapped") image.
    Generates two figures: a selector figures and an annotation figure.

    Parameters
    ----------
    pixels : array-like
        The pixels for the image to extract data from
    path : str
        The filename to save data.

    Attributes
    ----------
    pixels : array-like
        The pixels for the image to extract data from
    path : str
        The filename to save data.
    select_image : matplotlib.image.AxesImage
        The image used to select data from
    crop_widget : ShutterCrop widget
        widget applied to select figure, used to set cropping for annotate fig
    cbar_select : DragableColorLine widget
        widget used for selecting the colorbar on the select figure
    rcol_widget : RecoloredWidget
        widget for drawing the original image, but cropped and with colorbar
        applied to it
    cbar_widget : ScaledColorbar widget
        colorbar widget with manually specified limits
    dump_button : matplotlib.widgets.Button
        button widget use to trigger a dump
    dump_func : function
        function called when dump button is pressed
    textboxes : dict
        dictionary of TexBoxFloats uses to set limits on x-axis and y-axis
    selector_widgets : dict
        Dictionary of toggle-able widgets
    select_radio : matplotlib.widgets.Radio
        radio widget use to toggle active widgets
    """
    def __init__(self, pixels, path):
        self.path = path
        # generate layout of figures and axes
        # there should be two figures: one for (sub)selecting data
        # and another for annotating that data with numbers
        sel_axes = self.create_selector_axes()
        ann_axes = self.create_annotate_axes()

        #
        # Set up the widgets on the selection figure
        #
        # plot source data
        self.select_image = sel_axes['img'].imshow(pixels,
                                                   interpolation='none',
                                                   vmin=0,
                                                   vmax=1)

        # add shutters for cropping, initially disabled
        self.crop_widget = ShutterCrop(sel_axes['img'])
        self.crop_widget.active = False
        self.crop_widget.set_visible(False)

        # add a line to identify manually select the colorbar
        self.cbar_select = DragableColorLine(sel_axes['img'],
                                             sel_axes['cbar'],
                                             pixels,
                                             line_kw={'color': 'k'})
        self.cbar_select.active = False
        self.cbar_select.set_visible(False)

        # Radio buttons to select which Widget is active
        self.create_selector_toggle(sel_axes['select'])

        #
        # Now set up widgets on the annotation figure
        #
        # We are converting a multi-color image to a scalar image.
        # Plot that scalar image
        self.rcol_widget = RecoloredWidget(ann_axes['img'], pixels)
        self.rcol_image = self.rcol_widget.image
        # fill axes with textboxes for typing in the x & y limits
        # these set the scale of x and y
        self.rcol_widget.make_xyextent_textboxes(ann_axes['xlo'],
                                                 ann_axes['xhi'],
                                                 ann_axes['ylo'],
                                                 ann_axes['yhi'])

        # Crop the re-colored image when the cropping shutters move
        self.crop_widget.on_changed(
            lambda has_extent: self.rcol_widget.crop(has_extent.get_extents()),
            args=(self.crop_widget,),
        )

        # Draw a colorbar for the re-colored image, and set the initial cmap
        self.cbar_widget = ScaledColorbar(ann_axes['cbar'],
                                          self.rcol_widget.image)
        self.rcol_widget.digitize(self.cbar_select.l, self.cbar_select.rgb)

        # Re-draw the colormap when the colorbar-selector moves
        # re-digitizing is expensive, so only do it when you release the mouse
        self.cbar_select.on_release(
            lambda has_cb: self.rcol_widget.digitize(has_cb.l, has_cb.rgb),
            args=(self.cbar_select,),
        )

        # colorbar text boxes
        self.create_cbar_textboxes(ann_axes['cbar_lo'], ann_axes['cbar_hi'])

        # Add a button to dump the data to a file
        self.dump_button = Button(ann_axes['dump'], 'Dump to file')
        self.dump_func = self.dump_npz
        self.dump_button.on_clicked(self.dump)

    def create_cbar_textboxes(self, lo_ax, hi_ax):
        """Create textbox widgets to manually specifying the range of z"""
        self.textboxes = {}
        clo = TextBoxFloat(lo_ax, '0')
        chi = TextBoxFloat(hi_ax, '1')
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

    def create_selector_toggle(self, select_ax):
        self.selector_widgets = OrderedDict()
        self.selector_widgets['Do nothing'] = NothingWidget()
        self.selector_widgets['Select Colorbar'] = self.cbar_select
        self.selector_widgets['Crop Image'] = self.crop_widget

        self.toggle_state('Do nothing')

        self.select_radio = RadioButtons(select_ax,
                                         labels=self.selector_widgets.keys(),
                                         active=0)
        self.select_radio.on_clicked(self.toggle_state)

    def dump_npz(self):
        data = self.get_data()
        print('dumping to', self.path)
        np.savez(self.path, **data)
        print('dumped')

    def dump_txt(self):
        data = self.get_data()
        print('dumping to %s.*.txt' % self.path)
        for key, val in data:
            np.savetxt('%s.%s.txt' % (self.path, key), val)
        print('dumped')

    def dump(self, event):
        self.dump_func()

    def get_data(self):
        """Return the data extracted from the  image.

        Returns
        -------
        dict : Dictionary with the following keys/values
            x : array
                ni+1 coordinates of x grid
            y : 1D array
                nj+1 coordinates of x grid
            z : 2D array
                (ni,nj) values of centered in grid given by x and y
            l : array
                distance along colormap, on [0, 1] interval
            rgb: array
                color of each point on colormap
        """
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

    def create_selector_axes(self, gut=0.04, sepx=0.01, wide=0.2, tall=0.3,
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

        return axes

    def create_annotate_axes(self, gut=0.04, sepx=0.05, sepy=0.04,
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

        for name, lbwh in sizes.items():
            ax = fig.add_axes(lbwh, **ax_kwargs)
            ax.yaxis.set_visible(False)
            ax.xaxis.set_visible(False)
            axes[name] = ax

        return axes
