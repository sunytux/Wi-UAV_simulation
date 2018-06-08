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
    simulator.py

Arguments:

Options:
    -h, --help
"""
import logging
import tempfile
import math
from rayTracingWrapper import CloudRT


def main(logger, drone, user, bs):

    RESULT_DIR = tempfile.mkdtemp()
    LOG_FILE = "flight.log"

    f = open(LOG_FILE, 'w')

    rt = CloudRT(RESULT_DIR)
    rt.setTxPose(drone.x, drone.y, drone.z, drone.u, drone.v, drone.w)
    rt.setTxPose(user.x, user.y, user.z, user.u, user.v, user.w)

    for i in xrange(1, 3):
        rayTracing(rt, drone, user, bs)

        drone.routine()
        log(f, drone, user, bs)


def log(f, drone, user, bs):
    line = ",".join(["{:.3f}"] * 8) + "\n"
    line = line.format(drone.x, drone.y, user.x, user.y, bs.x, bs.y,
                       drone.ant[0].rss, drone.ant[1].rss)
    f.write(line)


def args():
    """Handle arguments for the main function."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # TODO cleaner way to handle initial value
    user = Terminal(logger, 538, 459, 2, 0, 0, 0)
    bs = Terminal(logger, 96, 69, 2, 0, 0, 0)
    drone = Drone(logger, 50, 200, 40, 0, 180, 0)

    return [logger, drone, user, bs]


def rayTracing(rt, drone, user, bs):
    """Compute received signal on the antenna for a given situation."""

    # User to Drone
    rt.setTxPose(user.x, user.y, user.z, user.u, user.v, user.w)
    rt.setRxPose(drone.x, drone.y, drone.z, drone.u, drone.v, drone.w)

    IQ = rt.simulate()
    drone.ant[0].setIQ(*IQ)

    # Base-station to Drone
    rt.setTxPose(bs.x, bs.y, bs.z, bs.u, bs.v, bs.w)
    rt.setRxPose(drone.x, drone.y, drone.z, drone.u, drone.v, drone.w)

    IQ = rt.simulate()
    drone.ant[1].setIQ(*IQ)


class Antenna(object):
    """docstring for Antenna"""
    def __init__(self):
        self.Re = 0  # I
        self.Im = 0  # Q

    def setIQ(self, Re, Im):
        self.Im = Im
        self.Re = Re

    @property
    def rss(self):
        return 10 * math.log10(10 * (math.pow(self.Im, 2.0) +
                                     math.pow(self.Re, 2.0)))

    @rss.setter
    def rss(self, amount):
        pass


class Terminal(object):
    """docstring for Terminal"""
    def __init__(self, logger, x, y, z, u, v, w):
        self.logger = logger
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.w = w

        self.ant = [Antenna()]

    def _addAntenna(self):
        self.ant.append(Antenna())

    def updatePos(self, x, y):
        pass


class Drone(Terminal):
    """docstring for Drone"""
    def __init__(self, logger, x, y, z, u, v, w):
        Terminal.__init__(self, logger, x, y, z, u, v, w)

        self._addAntenna()

    def routine(self):
        self.logger.debug('Hello from drone routine')
        self.logger.info('Drone is at (%d, %d, %d)', self.x, self.y, self.z)
        self.logger.info('User to drone: rss = ' + str(self.ant[0].rss))
        self.logger.info('User to drone: rss = ' + str(self.ant[1].rss))

        self.x += 20
        self.y += 10


if __name__ == '__main__':
    main(*args())
