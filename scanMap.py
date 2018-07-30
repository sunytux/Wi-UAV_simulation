#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    scanMap.py [-i ITER] [-o DIR]

Arguments:

Options:
    -i ITER         Iterations [default: 12].
    -o DIR          Output directory [default: /tmp/result].
    -h, --help
"""
from backend import *
from docopt import docopt

import os


def main(logFilePath, resultDir, iterations):

    f = open(logFilePath, 'w')

    terminals = [
        baseStation(96, 69, 200, 0, 0, 0),  # Base-station
        baseStation(325, 250, 2, 0, 0, 0),  # User 1
        baseStation(425, 125, 2, 0, 0, 0),  # User 2
        baseStation(225, 350, 2, 0, 0, 0),
        baseStation(225, 50, 2, 0, 0, 0)
    ]

    drone = Drone(176, 290, 100, 0, 0, 0, len(terminals),
                  antOffset=np.deg2rad(range(0, 360, 45)),
                  # AoAAlgo="max-rss",
                  routineAlgo="scan")

    rt = CloudRT(resultDir, quiteMode=True)
    log = Logs(f, drone, terminals)

    env = EnvironmentRF(resultDir, rt, log, terminals, drone)

    for time in range(iterations):
        LOGGER.debug("Iterration %d", time)
        drone.routine(time, env)

    f.close()


def args():
    """Handle arguments for the main function."""

    iterations = int(docopt(__doc__)['-i'])
    resultDir = docopt(__doc__)['-o']
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    logFilePath = os.path.join(resultDir, LOG_FILE)

    return [logFilePath, resultDir, iterations]


if __name__ == '__main__':
    main(*args())
