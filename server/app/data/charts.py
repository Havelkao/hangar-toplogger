import base64
import statistics
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO


class Plot(Figure):
    def __init__(self, *args, **kwargs):
        plt.style.use("seaborn-v0_8")
        self.fig = Figure(*args, **kwargs)
        self.ax = self.fig.subplots()
        self.ax.tick_params(labelsize=14)

    @property
    def encode(self):
        buf = BytesIO()
        self.fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.3)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
        return data

    def bar_labels(self, data: list, bar):
        median = statistics.median(data)
        over = [p if p > median else "" for p in data]
        under = [p if p <= median else "" for p in data]
        self.ax.bar_label(bar, under, padding=5, color="black", fontweight="bold")
        self.ax.bar_label(bar, over, padding=-25, color="white", fontweight="bold")

    def remove_axis(self, axis):
        if axis == "x":
            self.ax.set_xticklabels([])
        elif axis == "y":
            self.ax.set_yticklabels([])
        elif axis == "both":
            self.ax.set_xticklabels([])
            self.ax.set_yticklabels([])


def multi_bar():
    pass
    # for attribute, measurement in penguin_means.items():
    # offset = width * multiplier
    # rects = ax.bar(x + offset, measurement, width, label=attribute)
    # ax.bar_label(rects, padding=3)
    # multiplier += 1
