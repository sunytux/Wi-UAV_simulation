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
from rayTracingWrapper import CloudRT


def main(logger, drone, user, bs):

    RESULT_DIR = tempfile.mkdtemp()

    rt = CloudRT(RESULT_DIR)
    rt.setTxPose(drone.x, drone.y, drone.z, drone.u, drone.v, drone.w)
    rt.setTxPose(user.x, user.y, user.z, user.u, user.v, user.w)

    # while True:
    rayTracing(rt, drone, user, bs)

    drone.routine()


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

    CTF_Im = rt.simulate()
    drone.ant[0].CTF_Im = CTF_Im

    # Base-station to Drone
    rt.setTxPose(bs.x, bs.y, bs.z, bs.u, bs.v, bs.w)
    rt.setRxPose(drone.x, drone.y, drone.z, drone.u, drone.v, drone.w)

    CTF_Im = rt.simulate()
    drone.ant[1].CTF_Im = CTF_Im


class Antenna(object):
    """docstring for Antenna"""
    def __init__(self):
        self.CTF_Im = 0
        self.CTF_Re = 0


class Terminal(object):
    """docstring for Terminal"""
    def __init__(self, logger, x, y, z, u, v, w):
        # super(Terminal, self).__init__()
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
        self.logger.info('User to drone: ant0 = ' + str(self.ant[0].CTF_Im[0]))
        self.logger.info('User to drone: ant1 = ' + str(self.ant[1].CTF_Im[0]))


if __name__ == '__main__':
    main(*args())
