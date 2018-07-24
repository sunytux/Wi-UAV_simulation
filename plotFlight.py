#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot the trajectory of a flight simulation.

Usage:
    plotFlight.py [<PATH>] [-o DIR]

Arguments:
    <PATH>          Path to flight logs [default: /tmp/result/flight.csv].

Options:
    -o DIR          Output directory [default: /tmp/result/png].
    -h, --help
"""
import csv
import matplotlib.pyplot as plt
import numpy as np
from docopt import docopt
import os


def main(csvPath, resultDir):

    with open(csvPath) as f:
        reader = csv.reader(f)
        # next(reader) # skip header
        data = np.array([r for r in reader])

        drone = data[:, :2]
        user = data[:, 2:4]
        bs = data[:, 4:6]

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

    figureName = os.path.join(resultDir, "flight.png")
    plt.savefig(figureName, bbox_inches='tight')

    # plt.show()


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
