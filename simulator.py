#! /usr/bin/python3 -u
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
    simulator.py

Arguments:

Options:
    -h, --help
"""
import logging


def main(logger, drone, user, bs, env):

    while True:
        antennas = rayTracing(drone, user, bs, env)

        drone.updateAntenna(*antennas)

        drone.routine()


def args():
    """Handle arguments for the main function."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # TODO adapt this part
    user = 0
    bs = 0
    env = 0
    drone = Drone(0, 0, logger)

    return [logger, drone, user, bs, env]


def rayTracing(drone, user, bs, env):
    """Compute received signal on the antenna for a given situation."""
    return [0, 0, 0, 0]


class Drone(object):
    """docstring for Drone"""
    def __init__(self, x, y, logger):
        self.x = x
        self.y = y
        self.z = 0
        self.yaw = 0

        self.ant1 = 0
        self.ant2 = 0
        self.ant3 = 0
        self.ant4 = 0

        self.logger = logger

    def updatePos(self, x, y):
        pass

    def updateAntenna(self, ant1, ant2, ant3, ant4):
        pass

    def routine(self):
        self.logger.debug('Hello from drone routine')
        pass


if __name__ == '__main__':
    main(*args())
