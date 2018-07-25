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

    time, drone, bs, user, rss = readData(csvPath)

    fig1 = plt.figure()
    plotFlight(fig1, drone, user, bs)

    figureName = os.path.join(resultDir, "flight.png")
    plt.savefig(figureName, bbox_inches='tight')

    for idx in range(len(rss)):
        fig = plt.figure()
        plotRadiationPattern(fig, drone, user, bs, rss, idx)

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

        header = next(reader)
        data = np.array([r for r in reader])

    # Find the indexes for each categories
    timeIdx = header.index('time')
    droneIdxs = [i for i, x in enumerate(header) if 'drone' in x]
    bsIdxs = [i for i, x in enumerate(header) if 'bs' in x]
    userIdxs = [i for i, x in enumerate(header) if 'user' in x]
    rssIdxs = [i for i, x in enumerate(header) if 'ant' in x]

    # Split data in each categories
    time = data[:, timeIdx]
    drone = np.array([map(float, r) for r in data[:, droneIdxs]])
    bs = np.array([map(float, r) for r in data[:, bsIdxs]])
    user = np.array([map(float, r) for r in data[:, userIdxs]])
    rss = np.array([map(float, r) for r in data[:, rssIdxs]])

    return time, drone, bs, user, rss


def plotFlight(fig, drone, user, bs):

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


def plotRadiationPattern(fig, drone, user, bs, rss, idx):
    # Data manipulation
    droneIdx = drone[idx, :]
    userIdx = user[idx, :]
    bsIdx = bs[idx, :]

    rssIdx = np.append(rss[idx, :], rss[idx, 0])
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
