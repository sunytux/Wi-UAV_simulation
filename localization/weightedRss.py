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
import matplotlib.pyplot as plt
from docopt import docopt
import os
import numpy as np
import statistics
from scipy.stats import norm

USER = 4

LOG_FILE = "flight.csv"
DB_FILE = "/home/sami/docs/phd/projects/04_wireless_UAV_simulator/data/"\
          "ground-truth/ground-truth-map.csv"
TERMINALS = [
    {"x": 55, "y": 77, "z": 76, "u": 0, "v": 0, "w": 0},
    {"x": 536, "y": 244, "z": 1.8, "u": 0, "v": 0, "w": 0},
    {"x": 386, "y": 272, "z": 1.8, "u": 0, "v": 0, "w": 0},
    {"x": 536, "y": 144, "z": 1.8, "u": 0, "v": 0, "w": 0},
    {"x": 308, "y": 121, "z": 1.8, "u": 0, "v": 0, "w": 0}
]

STEP = 10


def main(outputDir):

    f = open(os.path.join(outputDir, LOG_FILE), 'w')

    terminals = []
    for t in TERMINALS:
        terminals.append(baseStation(t["x"], t["y"], t["z"],
                                     t["u"], t["v"], t["w"]))

    drone = Drone(0, 0, 0,
                  0, 0, 0,
                  len(terminals),
                  # antOffset=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]),
                  routineAlgo="scan",
                  AoAAlgo="weighted-rss")

    rt = CloudRT_DataBase(TERMINALS, DB_FILE)

    log = Logs(f, drone, terminals)

    env = EnvironmentRF(rt, log, terminals, drone)

    time = 0
    X = []
    Y = []
    U_AoA = []
    V_AoA = []
    U_AoU = []
    V_AoU = []
    ERR = []
    for x in range(0, 650, STEP):
        for y in range(0, 500, STEP):
            drone.x = x
            drone.y = y
            env.scan(time, USER)

            aoa = drone.getAoA()
            aou = math.atan2(terminals[USER].y - drone.y,
                             terminals[USER].x - drone.x)

            error = aoa - aou
            if error > np.deg2rad(180):
                error -= np.deg2rad(360)
            elif error < np.deg2rad(-180):
                error += np.deg2rad(360)

            error = np.rad2deg(error)

            X.append(x)
            Y.append(y)
            U_AoA.append(np.cos(aoa))
            V_AoA.append(np.sin(aoa))
            U_AoU.append(np.cos(aou))
            V_AoU.append(np.sin(aou))
            ERR.append(error)

            time += 1
    f.close()

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
        label="histogram"
    )

    # Approched normal distribution
    mean = statistics.mean(ERR)
    stdev = statistics.stdev(ERR)
    x_axis = np.arange(-180, 180, 0.1)

    plt.plot(
        x_axis, norm.pdf(x_axis, mean, stdev),
        label="$ \mathcal{N} $"
    )

    # Approched normal distribution
    ERR_simplified = filter(lambda x: abs(x) < 100, ERR)
    mean = statistics.mean(ERR_simplified)
    stdev = statistics.stdev(ERR_simplified)
    x_axis = np.arange(-180, 180, 0.1)

    plt.plot(
        x_axis, norm.pdf(x_axis, mean, stdev),
        label="$ \mathcal{N} $ w/o error > $ 100^\circ $"
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
