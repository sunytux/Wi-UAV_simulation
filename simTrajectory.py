#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Wireless UAV simulator.

This script aims at validating UAV trajectory planner in the context of
wireless UAV networks by computing several channel metrics along its path. This
is done in an iterative manner. At each position, the received signals on the
four UAV's antennas is simulated with an external Matlab simulator, which is
then used by the trajectory planner to compute the next UAV position and
orientation.

# TODO The stop condition is ...


It takes as input: user, base-station (BS) and UAV initial conditions as well
as a map of the environment and returns a complete set of information
describing both the UAV and the environment at every moment.

Usage:
    simTrajectory.py [-i ITER] [-o DIR]

Arguments:

Options:
    -i ITER         Iterations [default: 12].
    -o DIR          Output directory [default: /tmp/result].
    -h, --help
"""
from backend import *
from docopt import docopt

import os


def main(f, iterations, resultDir):

    terminals = [
        baseStation(96, 69, 200, 0, 0, 0),  # Base-station
        baseStation(325, 250, 2, 0, 0, 0),  # User 1
        baseStation(425, 150, 2, 0, 0, 0),  # User 2
        baseStation(225, 350, 2, 0, 0, 0),
        baseStation(225, 50, 2, 0, 0, 0)
    ]

    drone = Drone(176, 290, 100, 0, 0, 0, len(terminals),
                  # antOffset=np.deg2rad(range(0, 360, 20)),
                  routineAlgo="optimize",
                  AoAAlgo="max-rss")

    rt = CloudRT(resultDir, quiteMode=True)
    log = Logs(f, drone, terminals)

    env = EnvironmentRF(f, resultDir, rt, log, terminals, drone)

    for i in range(1, iterations + 1):
        LOGGER.debug("Iterration %d", i)
        drone.routine(env)
        env.incTime()

    f.close()


def args():
    """Handle arguments for the main function."""

    iterations = int(docopt(__doc__)['-i'])
    resultDir = docopt(__doc__)['-o']
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    logFilePath = os.path.join(resultDir, LOG_FILE)
    f = open(logFilePath, 'w')

    return [f, iterations, resultDir]


if __name__ == '__main__':
    main(*args())
