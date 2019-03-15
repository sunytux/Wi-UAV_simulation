#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    weightedRss.py -o DIR

Arguments:
    -o DIR          Output directory.

Options:
    -h, --help
"""
from myTools.simulator import *
from myTools import plot
from myTools import utils
from myTools import DEFAULT_CONF

from docopt import docopt
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

import statistics
import os

USER = 4
STEP = 10

EXP = DEFAULT_CONF
EXP.update({
    "routine-algo": "scan",
    "AoA-algo": "weighted-rss"
})


def main(outputDir):

    drone, terminals, env, rt, log = readConfig(EXP)

    time = 0
    X, Y, U_AoA, V_AoA, U_AoU, V_AoU, ERR = [], [], [], [], [], [], []

    for x in range(0, 650, STEP):
        for y in range(0, 500, STEP):
            drone.x = x
            drone.y = y
            env.scan(time, USER)

            aoa = drone.getAoA()
            aou = math.atan2(terminals[USER].y - drone.y,
                             terminals[USER].x - drone.x)

            error = utils.realAngle(aoa - aou)

            error = np.rad2deg(error)

            X.append(x)
            Y.append(y)
            U_AoA.append(np.cos(aoa))
            V_AoA.append(np.sin(aoa))
            U_AoU.append(np.cos(aou))
            V_AoU.append(np.sin(aou))
            ERR.append(error)

            time += 1
    log.close()

    # Figure 1 map of the angle estimation error
    plotAngleEstimationError(X, Y, U_AoA, V_AoA, U_AoU, V_AoU, ERR)
    plt.gcf().savefig(
        os.path.join(outputDir, "map-bearing-error-user-" + str(USER)),
        bbox_inches='tight',
        dpi=300
    )

    plt.gcf().clear()

    # Figure 2 histogram of the angle estimation error
    plotErrorHistogram(ERR)
    plt.gcf().savefig(
        os.path.join(outputDir, "histogram-bearing-error-user-" + str(USER)),
        bbox_inches='tight',
        dpi=300
    )


def plotErrorHistogram(ERR):
    # Cosmetics
    # plt.title("Bearing error")
    plt.xlabel("Bearing error [$^\circ$]")
    plt.ylabel("Normalized probability density function")

    # Histogram
    binSize = 5
    plt.hist(
        ERR,
        bins=range(-180, 180 + binSize, binSize),
        density=True,
        label="histogram",
        alpha=0.2
    )

    # normal distribution
    # mean = statistics.mean(ERR)
    # stdev = statistics.stdev(ERR)
    # x_axis = np.arange(-180, 180, 0.1)

    # label = "$ \mathcal{N} $\n" + \
    #         "$ \mu = {:.3f} $,\n$ \sigma = {:.3f} $".format(mean, stdev)
    # plt.plot(
    #     x_axis, norm.pdf(x_axis, mean, stdev),
    #     label=label
    # )

    # Approched normal distribution
    ERR_simplified = filter(lambda x: abs(x) < 100, ERR)
    density_correction = float(len(ERR_simplified)) / len(ERR)
    print(density_correction)

    mean = statistics.mean(ERR_simplified)
    stdev = statistics.stdev(ERR_simplified)
    x_axis = np.arange(-180, 180, 0.1)
    y_axis = np.array(norm.pdf(x_axis, mean, stdev)) * density_correction

    label = "$ \mathcal{N} $ oronly > $ 100^\circ $\n" + \
            "$ \mu = {:.3f} $,\n$ \sigma = {:.3f} $".format(mean, stdev)
    plt.plot(
        x_axis, y_axis,
        label=label
    )

    # Approched 2nd lobe w/ von mises
    # ERR_2 = filter(lambda x: abs(x) > 100, ERR)
    # ERR_2 = map(lambda a: (360 + a) % 360, ERR_2)

    # kappa, loc, scale = vonmises.fit(np.deg2rad(ERR_2), fscale=1)
    # print(kappa, loc, scale)

    # x_axis = np.arange(-180, 180, 0.1)

    # label = "von mises"
    # plt.plot(
    #     x_axis, vonmises.pdf(np.deg2rad(x_axis), kappa, loc=loc, scale=scale),
    #     label=label
    # )

    # Approched 2nd lobe w/ von mises
    ERR_2 = filter(lambda x: abs(x) > 100, ERR)
    ERR_2 = map(lambda a: (360 + a) % 360, ERR_2)
    density_correction = float(len(ERR_2)) / len(ERR)
    print(density_correction)

    mean = utils.realAngle(statistics.mean(ERR_2), deg=True)
    stdev = statistics.stdev(ERR_2)
    x_axis = np.arange(-180, 180, 0.1)

    label = "$ \mathcal{N} $ only < $ 100^\circ $\n" + \
            "$ \mu = {:.3f} $,\n$ \sigma = {:.3f} $".format(mean, stdev)

    y_axis = np.array(
        norm.pdf(map(lambda a: (360 + a) % 360, x_axis), mean, stdev)
    ) * density_correction
    plt.plot(
        x_axis, y_axis,
        label=label
    )

    plt.legend(loc="upper right")


def plotAngleEstimationError(X, Y, U_AoA, V_AoA, U_AoU, V_AoU, ERR):
    # Cosmetics
    # plt.title("Bearing error")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    plot.plot_scenario()
    plt.quiver(X, Y, U_AoA, V_AoA, zorder=3, alpha=0.2)

    # Plot terminal
    opt = {
        "marker": "*",
        "markeredgewidth": 2,
        "markersize": 20,
        "color": 'white',
        "markeredgecolor": 'black'
    }
    plot.plot_terminals([TERMINALS[USER]], bsOpt=opt)

    # Weakest-user
    plot.plot_heatmap(
        X, Y, map(abs, ERR),
        np.ones(len(X)) * STEP,
        np.ones(len(X)) * STEP,
        legend="Bearing error [$^\circ$]"
    )


def args():
    """Handle arguments for the main function."""

    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    return [outputDir]


if __name__ == '__main__':
    main(*args())
