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
    simTrajectory.py [<INPUT_FILE>] [-i ITER] [-o DIR]

Arguments:

Options:
    <INPUT_FILE>    Path to Json file of the experience [default: ./exp.json].
    -i ITER         Iterations [default: 12].
    -o DIR          Output directory [default: /tmp/result].
    -h, --help
"""
from myTools.simulator import *
from myTools import utils
from docopt import docopt
import json
import os
import logging

LOG_FILE = "flight.csv"

DEFAULT_INPUT_FILE = "./exp.json"
DEFAULT_SCENARIO = "subrealcity.json"

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def main(inputFile, logFilePath, resultDir, iterations):

    f = open(logFilePath, 'w')

    exp = utils.readJson(inputFile)

    terminals = []
    for t in exp['terminals']:
        terminals.append(baseStation(t["x"], t["y"], t["z"],
                                     t["u"], t["v"], t["w"]))

    drone = Drone(exp["drone"]["x"], exp["drone"]["y"], exp["drone"]["z"],
                  exp["drone"]["u"], exp["drone"]["v"], exp["drone"]["w"],
                  len(terminals),
                  # antOffset=np.deg2rad(range(0, 360, 20)),
                  routineAlgo=exp["routine-algo"],
                  AoAAlgo=exp["AoA-algo"])

    if "scenario" in exp:
        scenario = exp["scenario"]
    else:
        scenario = DEFAULT_SCENARIO

    rt = CloudRT(resultDir, scenario, quiteMode=True)
    log = Logs(f, drone, terminals)

    env = EnvironmentRF(resultDir, rt, log, terminals, drone)

    for time in range(iterations):
        LOGGER.debug("Iterration %d", time)
        drone.routine(time, env)

    f.close()


def args():
    """Handle arguments for the main function."""

    iterations = int(docopt(__doc__)['-i'])

    if docopt(__doc__)['<INPUT_FILE>']:
        inputFile = docopt(__doc__)['<INPUT_FILE>']
    else:
        inputFile = DEFAULT_INPUT_FILE

    resultDir = docopt(__doc__)['-o']
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    logFilePath = os.path.join(resultDir, LOG_FILE)

    return [inputFile, logFilePath, resultDir, iterations]


if __name__ == '__main__':
    main(*args())
