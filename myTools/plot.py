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


def plot_scenario(edge='black', face='gray'):
    """Plot the scenario

       Scenarios are maps given to CloudRT

       TODO scenarios are hard-coded, change that
    """
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
            edgecolor=edge,
            facecolor=face,
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

        norm = mpl.colors.Normalize(vmin=min(z), vmax=max(z))
        cb = mpl.colorbar.ColorbarBase(
            ax, cmap=CMAP, norm=norm, orientation='vertical'
        )
        cb.set_label(legend)


def plot_terminals(terminals, bsOpt={}, userOpt={}):
    """Plot terminals on a map

       terminals is a list of N terminals represented either by a Mx6 numpy
       array or a dict formatted as follow:
       [{"x" :386, "y" :272, "z" :1.8, "u" :0, "v" :0, "w" :0}, ...]
       bsOpt and userOpt is a dict of matplotlib
    """

    if type(terminals[0]) == dict:
        terminals = [np.array([[t["x"], t["y"], t["z"],
                                t["u"], t["v"], t["w"]]]) for t in terminals]

    defaultBsOpt = {
        "marker": "o",
        "markeredgewidth": 1,
        "markersize": 10,
        "color": 'green',
        "markeredgecolor": 'green'
    }
    defaultUserOpt = {
        "marker": "*",
        "markeredgewidth": 1,
        "markersize": 10,
        "color": 'red',
        "markeredgecolor": 'red'
    }
    defaultBsOpt.update(bsOpt)
    defaultUserOpt.update(userOpt)

    for i in range(len(terminals)):
        opt = defaultBsOpt if i == 0 else defaultUserOpt
        plt.plot(terminals[i][:, 0], terminals[i][:, 1], **opt)


def plot_flight(drone):
    """Plot drone trajectory

    drone is a Mx2 numpy array
    """

    plt.plot(
        drone[:, 0], drone[:, 1], 'o-',
        color='gainsboro',
        markersize=4,
        markerfacecolor='gray',
        markeredgecolor='gray'
    )
    plt.plot(
        drone[0, 0], drone[0, 1], 'kx',
        markersize=10,
        mew=4
    )
    plt.plot(
        drone[-1, 0], drone[-1, 1], 'kv',
        markersize=10
    )
