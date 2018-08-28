#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Library for graph plotting 
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import numpy as np

from myTools import utils

CMAP = cm.get_cmap('Spectral')


def plot_scenario():
    data = utils.readJson('/opt/COTS/CloudRT/database/scenario/subrealcity.json')

    for bloc in data['layer'][0]['geometry']:
        bloc = np.array(bloc['v'])
        x_min = min(bloc[:, 0])
        y_min = min(bloc[:, 1])
        x_max = max(bloc[:, 0])
        y_max = max(bloc[:, 1])
        w = x_max - x_min
        h = y_max - y_min
        # for i in range(len(x_min)):
        rect = patches.Rectangle((x_min, y_min), w, h,
                                 linewidth=1,
                                 edgecolor='black',
                                 facecolor='gray',
                                 zorder=2)
        plt.gca().add_patch(rect)


def plot_heatmap(x, y, z, w, h):
    """Plot a heatmap

       all arguments are numpy array
    """

    z = z / max(z)

    for i in range(len(x)):
        rect = patches.Rectangle((x[i] - w[i] / 2, y[i] - h[i] / 2),
                                 w[i], h[i],
                                 linewidth=0,
                                 facecolor=CMAP(z[i]),
                                 alpha=0.5,
                                 zorder=2)
        plt.gca().add_patch(rect)
