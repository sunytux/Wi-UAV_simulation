#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Library for plotting graphs
"""

from myTools import utils
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib as mpl
import numpy as np
import os

CMAP = cm.get_cmap('Spectral')
CMAP = cm.get_cmap('plasma')
CMAP = cm.get_cmap('viridis')
CMAP = cm.get_cmap('jet')

SCENARIO_DIR = '/opt/COTS/CloudRT/database/scenario'


def plot_scenario():
    data = utils.readJson(os.path.join(SCENARIO_DIR, 'subrealcity.json'))

    for bloc in data['layer'][0]['geometry']:
        bloc = np.array(bloc['v'])
        x_min = min(bloc[:, 0])
        y_min = min(bloc[:, 1])
        x_max = max(bloc[:, 0])
        y_max = max(bloc[:, 1])
        w = x_max - x_min
        h = y_max - y_min
        rect = patches.Rectangle(
            (x_min, y_min), w, h,
            linewidth=1,
            edgecolor='black',
            facecolor='gray',
            zorder=2
        )
        plt.gca().add_patch(rect)


def plot_heatmap(x, y, z, w, h, legend=False):
    """Plot a heatmap

       all arguments are numpy array except legend which is a string
    """

    z_nom = (z - min(z)) / (max(z) - min(z))

    for i in range(len(x)):
        rect = patches.Rectangle(
            # (x[i] - w[i] / 2, y[i] - h[i] / 2),
            (x[i], y[i]),
            w[i], h[i],
            linewidth=0,
            facecolor=CMAP(z_nom[i]),
            alpha=0.6,
            zorder=2
        )
        plt.gca().add_patch(rect)

    if legend:
        ax = plt.gcf().add_axes([0.9, 0.11, 0.01, 0.77])

        cmap = CMAP
        # cmap.set_over('0.25')
        # cmap.set_under('0.75')

        norm = mpl.colors.Normalize(vmin=min(z), vmax=max(z))
        cb = mpl.colorbar.ColorbarBase(
            ax, cmap=cmap, norm=norm, orientation='vertical'
        )
        cb.set_label(legend)


def plot_terminals(terminals):
    """Plot terminals on a map

    terminal is a list of dict formatted as such:
    [{"x" :386, "y" :272, "z" :1.8, "u" :0, "v" :0, "w" :0}, ...]
    The base station should be the first element
    """

    for i in range(len(terminals)):
        if i == 0:
            plt.plot(
                terminals[i]['x'], terminals[i]['y'], 'o',
                color='white',
                markersize=10,
                markeredgewidth=2,
                markeredgecolor='black'
                # markeredgecolor='white'
            )
        else:
            plt.plot(
                terminals[i]['x'], terminals[i]['y'], '*',
                color='white',
                markersize=15,
                markeredgewidth=2,
                markeredgecolor='black'
                # markeredgecolor='white'
            )
