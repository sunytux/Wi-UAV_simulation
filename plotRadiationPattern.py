#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    plotRadiationPattern.py [<PATH>]

Arguments:
    <PATH>          Path to flight logs [default: ./flight.log].

Options:
    -h, --help
"""
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from docopt import docopt


def main(path):

    with open(path) as f:
        reader = csv.reader(f)
        # next(reader) # skip header
        data = np.array([map(float, r) for r in reader])

        drone = data[:, :2]
        user = data[:, 2:4]
        bs = data[:, 4:6]

        rss = data[:, 6:]

    for idx in range(len(data)):
        # rss.append(rss[0])  # for plotting purposes
        # rss = np.array(rss) / max(rss)

        droneIdx = drone[idx]
        userIdx = user[idx]
        bsIdx = bs[idx]

        rssIdx = np.append(rss[idx, :], rss[idx, 0])  # for plotting purposes
        rssIdx = np.array(map(float, rssIdx))
        rssIdx /= max(rssIdx)

        # TODO this is not correct angles are not set like this !
        angles = np.linspace(0.0, 2 * np.pi, num=len(rssIdx))

        userAngle = math.atan2(userIdx[1] - droneIdx[1],
                               userIdx[0] - droneIdx[0])
        bsAngle = math.atan2(bsIdx[1] - droneIdx[1],
                             bsIdx[0] - droneIdx[0])

        fig1 = plt.figure()
        ax1 = fig1.add_axes([0, 0, 1, 1], polar=True)

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

        fig1.savefig("png/flight-{}.png".format(idx), bbox_inches='tight')
        plt.close('all')


def args():
    """Handle arguments for the main function."""

    if docopt(__doc__)['<PATH>']:
        path = docopt(__doc__)['<PATH>']
    else:
        path = "./flight.log"

    return [path]


if __name__ == '__main__':
    main(*args())
