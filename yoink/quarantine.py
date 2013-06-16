from widgets import if_attentive
from matplotlib.widgets import Widget
import matplotlib.pyplot as plt


class KeyboardCrop(Widget):
    """
    Keyboard driven interface to set crop an image

    KeyboardCrop.edge_effects is a dict that controls the keyboard interface.
    the keys are the edges effected (north/south/east/west)
    the values are dicts of keyboard-keys and how far to shift the image
    (nominally in pixels).

    Example usage given in keyboard_crop()
    """
    def __init__(self, im, limits, width=20, height=20, **kwargs):
        self.im = im
        self.crop = limits
        fig, axes = plt.subplots(2, 2, sharex='col', sharey='row')
        self.canvas = fig.canvas
        (self.ax1, self.ax2), (self.ax3, self.ax4) = axes
        self.edge_effects = {}

        self.width = width
        self.height = height

        self.ax1.imshow(im, **kwargs)
        self.ax2.imshow(im, **kwargs)
        self.ax3.imshow(im, **kwargs)
        self.ax4.imshow(im, **kwargs)

        self.cids = [self.canvas.mpl_connect('key_press_event', self._press)]
        self.update_limits()

    def update_limits(self):
        self.ax1.set_xlim(self.crop['west'], self.crop['west'] + self.width)
        self.ax2.set_xlim(self.crop['east'] - self.width, self.crop['east'])
        self.ax1.set_ylim(self.crop['north'], self.crop['north'] + self.height)
        self.ax3.set_ylim(self.crop['south'] - self.height, self.crop['south'])
        if self.drawon:
            self.canvas.draw()

    @if_attentive
    def _press(self, event):
        key = event.key
        if key is 'enter':
            return

        for edge, effects in self.edge_effects:
            if key in effects:
                self.crop[edge] += effects[key]
        self.update_limits()

    def get_edges(self):
        return [self.crop[key] for key in ('south', 'east', 'north', 'west')]
