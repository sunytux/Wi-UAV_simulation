#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

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

    with open(csvPath) as f:
        reader = csv.reader(f)
        # next(reader) # skip header
        data = np.array([map(float, r) for r in reader])

    for idx in range(len(data)):
        fig = plt.figure()
        ax1 = fig.add_axes([0, 0, 1, 1], polar=True)
        plotRadiationPattern(ax1, data, idx)

        figureName = os.path.join(resultDir, "flight-{}.png".format(idx))
        fig.savefig(figureName, bbox_inches='tight')
        plt.close('all')


def plotRadiationPattern(ax1, data, idx):
    droneIdx = data[idx, :2]
    userIdx = data[idx, 2:4]
    bsIdx = data[idx, 4:6]

    rssIdx = np.append(data[idx, 6:], data[idx, 6])
    rssIdx /= max(rssIdx)

    # TODO this is not correct angles are not set like this !
    angles = np.linspace(0.0, 2 * np.pi, num=len(rssIdx))

    userAngle = math.atan2(userIdx[1] - droneIdx[1],
                           userIdx[0] - droneIdx[0])
    bsAngle = math.atan2(bsIdx[1] - droneIdx[1],
                         bsIdx[0] - droneIdx[0])

    ax1.clear()
    # Rss
    ax1.plot(angles, rssIdx,
             lw=2.5)

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


if __name__ == '__main__':
    main(*args())
