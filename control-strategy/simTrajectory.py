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
    simTrajectory.py -i <INPUT_FILE>

Arguments:
    -i <INPUT_FILE> Path to Json file of the experience.

Options:
    -h, --help
"""
from myTools import LOGGER
from myTools import DEFAULT_CONF
from myTools.simulator import *
from myTools import utils

from docopt import docopt


def run(exp):
    drone, terminals, env, rt, log = readConfig(exp)

    for i in range(exp['max-iteration']):
        LOGGER.debug("Iterration %d", i)
        drone.routine(i, env)

    log.close()


def args():
    """Handle arguments for the main function."""

    inputFile = docopt(__doc__)['-i']
    exp = DEFAULT_CONF
    exp.update(utils.readJson(inputFile))

    return [exp]


if __name__ == '__main__':
    run(*args())
