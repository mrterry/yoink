from __future__ import division

from matplotlib.patches import Circle
from matplotlib.lines import Line2D


class DeformableBorder(object):
    def __init__(self, ax):
        self.ax = ax
        self.canvas = self.ax.figure.canvas

        self.xs = []
        self.ys = []
        self.line = Line2D(self.xs, self.ys)
        self.ax.add_artist(self.line)

        self.circles = []
        self.callbacks = []
        self.connected = False

    def connect(self):
        self.cidpress = self.canvas.mpl_connect(
                'button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect(
                'button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect(
                'motion_notify_event', self.on_motion)
        self.connected = True

    def disconnect(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)

        self.cidpress = None
        self.cidrelease = None
        self.cidmotion = None
        self.connected = False

    def draw(self):
        for f in self.callbacks:
            f()
        self.canvas.draw()

    def on_press(self, event):
        ci = self.get_circle_index(event)
        if ci is None:
            return
        circle = self.circles[ci]
        x0, y0 = circle.center
        self.moving_ci = x0, y0, event.xdata, event.ydata, ci

    def on_motion(self, event):
        if self.moving_ci is None:
            return
        xc, yc, xclick, yclick, ci = self.moving_ci

        x, y = xc + (event.xdata-xclick), yc + (event.ydata-yclick)
        self.circles[ci].center = (x, y)

        self.xs[ci], self.ys[ci] = x, y
        if len(self.xs) == 5 and ci == 0:
            self.xs[-1], self.ys[-1] = x, y
        self.line.set_data(self.xs, self.ys)

        self.draw()

    def on_release(self, event):
        if self.moving_ci:
            self.moving_ci = None
            self.draw()

    def get_circle_index(self, event):
        i = 0
        for i, c in enumerate(self.circles):
            if c.contains(event)[0]:
                return i
        if len(self.circles) == 4:
            return None

        # new circle
        i = len(self.circles)
        x, y = event.xdata, event.ydata
        circle = Circle((x, y), radius=5, alpha=0.5)
        self.circles.append(circle)
        self.ax.add_artist(circle)

        self.xs.append(x)
        self.ys.append(y)
        # finish square if adding last corner
        if i == 3:
            self.xs.append(self.xs[0])
            self.ys.append(self.ys[0])
        self.line.set_data(self.xs, self.ys)

        self.draw()
        return i
