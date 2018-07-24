#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot and save figures of flight logs.

Usage:
    plotRadiationPattern.py [<PATH>] [-o DIR]

Arguments:
    <PATH>          Path to flight logs [default: /tmp/result/flight.csv].

Options:
    -o DIR          Output directory [default: /tmp/result/png].
    -h, --help
"""
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from docopt import docopt
import os


def main(csvPath, resultDir):

    data = readData(csvPath)

    fig1 = plt.figure()
    plotFlight(fig1, data)

    figureName = os.path.join(resultDir, "flight.png")
    plt.savefig(figureName, bbox_inches='tight')

    for idx in range(len(data)):
        fig = plt.figure()
        plotRadiationPattern(fig, data, idx)

        figureName = os.path.join(resultDir, "flight-{}.png".format(idx))
        fig.savefig(figureName, bbox_inches='tight')
        plt.close('all')


def args():
    """Handle arguments for the main function."""

    if docopt(__doc__)['<PATH>']:
        csvPath = docopt(__doc__)['<PATH>']
    else:
        csvPath = "/tmp/result/flight.csv"

    resultDir = docopt(__doc__)['-o']
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    return [csvPath, resultDir]


def readData(csvPath):
    with open(csvPath) as f:
        reader = csv.reader(f)
        # next(reader) # skip header
        data = np.array([map(float, r) for r in reader])

    return data


def plotFlight(fig, data):
    # Data manipulation
    drone = data[:, :2]
    user = data[:, 2:4]
    bs = data[:, 4:6]

    # Plots
    fig.clear()
    # Drone trajectory
    plt.plot(drone[:, 0], drone[:, 1], 'o-',
             color='gainsboro',
             markersize=4,
             markerfacecolor='gray',
             markeredgecolor='gray')
    plt.plot(drone[0, 0], drone[0, 1], 'kx',
             markersize=10,
             mew=4)
    plt.plot(drone[-1, 0], drone[-1, 1], 'kv',
             markersize=10)

    # Terminals
    plt.plot(user[:, 0], user[:, 1], 'r*',
             markersize=10)
    plt.plot(bs[:, 0], bs[:, 1], 'go',
             markersize=10)

    # Cosmetics
    plt.title("Flight trajectory")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')


def plotRadiationPattern(fig, data, idx):
    # Data manipulation
    droneIdx = data[idx, :2]
    userIdx = data[idx, 2:4]
    bsIdx = data[idx, 4:6]

    rssIdx = np.append(data[idx, 6:], data[idx, 6])
    rssIdx /= max(rssIdx)

    angles = np.linspace(0.0, 2 * np.pi, num=len(rssIdx))

    userAngle = math.atan2(userIdx[1] - droneIdx[1],
                           userIdx[0] - droneIdx[0])
    bsAngle = math.atan2(bsIdx[1] - droneIdx[1],
                         bsIdx[0] - droneIdx[0])

    # Plots
    fig.clear()
    ax1 = fig.add_axes([0, 0, 1, 1], polar=True)

    # Rss
    ax1.plot(angles, rssIdx, 'o-',
             color='gainsboro',
             lw=2.5,
             markersize=4,
             markerfacecolor='cornflowerblue',
             markeredgecolor='cornflowerblue')

    # Drone
    ax1.plot(0, 0, 'kv',
             markersize=10)

    # Terminals
    ax1.plot(userAngle, max(rssIdx) * 1.2, 'r*',
             markersize=10)
    ax1.plot(bsAngle, max(rssIdx) * 1.2, 'go',
             markersize=10)

    # Cosmetic
    ax1.set_ylim(0, 1.3)
    ax1.set_yticks([1])
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')


if __name__ == '__main__':
    main(*args())
