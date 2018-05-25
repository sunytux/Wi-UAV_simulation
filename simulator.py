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


def main(logger, drone, user, bs, mapEnv):

    while True:
        antennas = rayTracing(drone, user, bs, mapEnv)

        drone.updateAntenna(*antennas)

        drone.routine()


def args():
    """Handle arguments for the main function."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    user = Terminal(logger, 0, 0, 0, 0)
    bs = Terminal(logger, 0, 0, 0, 0)
    drone = Drone(logger, 0, 0, 120, 0)
    mapEnv = 0

    return [logger, drone, user, bs, mapEnv]


def rayTracing(drone, user, bs, mapEnv):
    """Compute received signal on the antenna for a given situation."""
    return [Antenna()] * 4


class Antenna(object):
    """docstring for Antenna"""
    def __init__(self):
        pass


class Terminal(object):
    """docstring for Terminal"""
    def __init__(self, logger, x, y, z, yaw):
        # super(Terminal, self).__init__()
        self.logger = logger
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw

        self.antennas = [Antenna()]

    def _addAntenna(self):
        self.antennas.append(Antenna())

    def updatePos(self, x, y):
        pass

    def updateAntenna(self, *antennas):
        for idx, ant in zip(range(len(antennas)), antennas):
            self.antennas[idx] = ant


class Drone(Terminal):
    """docstring for Drone"""
    def __init__(self, logger, x, y, z, yaw):
        Terminal.__init__(self, logger, x, y, z, yaw)

        self._addAntenna()
        self._addAntenna()
        self._addAntenna()

    def routine(self):
        self.logger.debug('Hello from drone routine')
        pass


if __name__ == '__main__':
    main(*args())
