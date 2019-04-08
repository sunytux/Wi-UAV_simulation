#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Library for plotting graphs
"""

from myTools import utils
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib as mpl
import numpy as np
import os
import math

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
        Z = np.array(bloc['v'])

        # TODO make automatic (?)
        # vertices are ordered so that when plotted the shape is convex
        Z[[1, 2]] = Z[[2, 1]]

        rect = patches.Polygon(
            Z[:, :2],
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

    if type(z).__module__ != np.__name__:
        z = np.array(z)

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


def plot_flight(drone, iOpt={}, fOpt={}, insideOpt={}):
    """Plot drone trajectory

    drone is a Mx2 numpy array
    """

    defaultiOpt = {
        "marker": "x",
        "color": 'black',
        "markersize": 10,
        "mew": 4
    }
    defaultfOpt = {
        "marker": "v",
        "color": 'black',
        "markersize": 10
    }
    defaultinsideOpt = {
        "color": 'gainsboro',
        "markersize": 4,
        "markerfacecolor": 'gray',
        "markeredgecolor": 'gray'
    }
    defaultiOpt.update(iOpt)
    defaultfOpt.update(fOpt)
    defaultinsideOpt.update(insideOpt)
    if np.shape(drone)[0] > 1:
        plt.plot(drone[:, 0], drone[:, 1], 'o-', **defaultinsideOpt)
        plt.plot(drone[0, 0], drone[0, 1], **defaultiOpt)
    plt.plot(drone[-1, 0], drone[-1, 1], **defaultfOpt)


def plot3_scenario(edge='gray', face='gainsboro'):
    """Plot the scenario in 3d

       Scenarios are maps given to CloudRT

       TODO scenarios are hard-coded, change that
    """
    data = utils.readJson(os.path.join(SCENARIO_DIR, 'subrealcity.json'))
    for bloc in data['layer'][0]['geometry']:
        bloc = np.array(bloc['v'])

        # plot sides
        Z = np.array(bloc)
        Z[[1, 2]] = Z[[2, 1]]
        pc = Poly3DCollection(
            [list(zip(Z[:, 0], Z[:, 1], Z[:, 2]))],
            linewidths=1,
            edgecolors=edge,
            alpha=0.7,
        )
        pc.set_facecolor(face)

        plt.gca(projection='3d').add_collection3d(pc)

    plt.gca(projection='3d').set_xlabel('X')
    plt.gca(projection='3d').set_ylabel('Y')
    plt.gca(projection='3d').set_zlabel('Z')

    plt.gca().axis('off')
    plt.gca().set_xlim(0, 650)
    plt.gca().set_ylim(0, 500)
    plt.gca().set_zlim(0, 150)


def plot3_antennaPattern():
    """Plot antenna pattern in 3D

       Antennas are json file used by CloudRT

       TODO Antenna is hard-coded, change that
    """
    DEFAULT_PATH = "/opt/COTS/CloudRT/database/antenna/Microstripantenna.json"
    POINTS = 36 * 3

    # Load data from Json file
    data = utils.readJson(DEFAULT_PATH)

    phi_re = data["phi"]["real"]
    phi_im = data["phi"]["imag"]

    theta_re = data["theta"]["real"]
    theta_im = data["theta"]["imag"]

    # phi and theta axis
    phi = np.linspace(0, 360, 2 * POINTS, endpoint=True)
    theta = np.linspace(0, 180, POINTS, endpoint=True)

    # Convert axis to 2d for plot_surface
    phi2d, theta2d = np.meshgrid(phi, theta)

    def mod_E_phi(az, el):
        return abs(phi_re[az][el] + 1j * phi_im[az][el])

    def mod_E_theta(az, el):
        return abs(theta_re[az][el] + 1j * theta_im[az][el])

    def G(az, el):
        """Return the gain given a direction.

        az: Azimuthal angle included inside [0, 360] (= phi).
        el: Elevation angle included inside [0, 180] (=theta), 0 = zenith axis.
        """

        # If the JSON file contains less than 360 entries
        az = int(math.floor((az / 360) * (len(phi_re) - 1)))
        el = int(math.floor((el / 180) * (len(phi_re[0]) - 1)))

        return mod_E_phi(az, el)**2 + mod_E_theta(az, el)**2

    r = np.array([G(p, t) for p, t in zip(np.ravel(phi2d), np.ravel(theta2d))])
    r2d = r.reshape(phi2d.shape)

    x2d = r2d * np.sin(np.deg2rad(theta2d)) * np.cos(np.deg2rad(phi2d))
    y2d = r2d * np.sin(np.deg2rad(theta2d)) * np.sin(np.deg2rad(phi2d))
    z2d = r2d * np.cos(np.deg2rad(theta2d))

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.plot_surface(x2d, y2d, z2d,
                    cmap=plt.get_cmap('jet'),
                    linewidth=100, antialiased=True, alpha=0.4)

    # Reference point
    ax.scatter(0, 0, 0, s=100, c='#000000')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    ax.auto_scale_xyz([-3, 3], [-3, 3], [-1, 5])
    ax.set_aspect('equal', 'box')

    # plt.show()


def plot3_rays(rays):
    """Plot rays in 3d

    rays is a pandas Dataframe.
    """
    optDirectRays = {
        # "color": "tomato",
        "linewidth": 2,
        "zorder": 1001,
        "alpha": 1
    }
    optOtherRays = {
        # "color": "cornflowerblue",
        "linewidth": 1,
        "zorder": 1000,
        "alpha": 0.2
    }
    rays['rss'] -= min(rays['rss'])
    maxRss = max(rays['rss'])
    for index, row in rays.iterrows():
        x = np.array(row[['tx.x', 'ref1.x', 'ref2.x', 'rx.x']])
        y = np.array(row[['tx.y', 'ref1.y', 'ref2.y', 'rx.y']])
        z = np.array(row[['tx.z', 'ref1.z', 'ref2.z', 'rx.z']])
        ratio = row['rss'] / maxRss
        opt = optDirectRays if row['type'] == 0 else optOtherRays

        plt.plot(x, y, z, color=CMAP(ratio), **opt)


def plot_rays(rays):
    """Plot rays

    rays is a pandas Dataframe.
    """
    optDirectRays = {
        # "color": "tomato",
        "linewidth": 2,
        # "zorder": 1001,
        "alpha": 0.5
    }
    optOtherRays = {
        # "color": "cornflowerblue",
        "linewidth": 1,
        # "zorder": 1000,
        "alpha": 0.2
    }
    rays['rss'] -= min(rays['rss'])
    maxRss = max(rays['rss'])
    for index, row in rays.iterrows():
        x = np.array(row[['tx.x', 'ref1.x', 'ref2.x', 'rx.x']])
        y = np.array(row[['tx.y', 'ref1.y', 'ref2.y', 'rx.y']])
        ratio = row['rss'] / maxRss
        opt = optDirectRays if row['type'] == 0 else optOtherRays

        plt.plot(x, y, color=CMAP(ratio), **opt)
