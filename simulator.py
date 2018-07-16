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
import numpy as np
from rayTracingWrapper import CloudRT, PathLoss

# TODO make it clean
RESULT_DIR = tempfile.mkdtemp()
RESULT_DIR = "/tmp/result"
LOG_FILE = "flight.log"


def main(logger, drone, env):

    f = open(LOG_FILE, 'w')

    for i in range(1, 12):

        drone.routine(env)
        log(logger, f, drone, env.user, env.bs)

    f.close()


def log(logger, f, drone, user, bs):
    logger.info('Drone is at (%d, %d, %d)', drone.x, drone.y, drone.z)
    logger.info('User to drone: rss = ' + str(drone.ant[0].rss))
    logger.info('User to drone: rss = ' + str(drone.ant[1].rss))

    line = ",".join(["{:.3f}"] * 8) + "\n"
    line = line.format(drone.x, drone.y, user.x, user.y, bs.x, bs.y,
                       drone.ant[0].rss, drone.ant[1].rss)
    f.write(line)


def args():
    """Handle arguments for the main function."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # TODO cleaner way to handle initial value
    user = baseStation(538, 459, 2, 0, 0, 0)
    bs = baseStation(96, 69, 2, 0, 0, 0)
    env = EnvironmentRF(bs, user)
    drone = Drone(0, 300, 120, 0, 0, 0)

    return [logger, drone, env]


class Antenna(object):
    """docstring for Antenna"""
    def __init__(self, u, v, w):
        self.Re = 0  # I
        self.Im = 0  # Q
        self.u = u
        self.v = v
        self.w = w

    def setIQ(self, Re, Im):
        self.Im = Im
        self.Re = Re

    @property
    def rss(self):
        # TODO verif
        return 10 * math.log10(10 * (math.pow(self.Im, 2.0) +
                                     math.pow(self.Re, 2.0)))

    @rss.setter
    def rss(self, amount):
        pass


class Terminal(object):
    """docstring for Terminal"""
    def __init__(self, x, y, z, u, v, w):
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.w = w

        self.ant = []

    def _addAntenna(self, u, v, w):
        self.ant.append(Antenna(u, v, w))


class baseStation(Terminal):
    """docstring for baseStation"""
    def __init__(self, x, y, z, u, v, w):
        Terminal.__init__(self, x, y, z, u, v, w)

        self._addAntenna(0, 0, 0)


class EnvironmentRF(object):
    """docstring for EnvironmentRF"""
    def __init__(self, bs, user):
        self.bs = bs
        self.user = user

        self.rt = PathLoss()

    def scan(self, drone, tx):
        """Compute received signal on drone antennas for a given situation."""

        # TODO find cleaner way
        if tx == "bs":
            tx = self.bs
        elif tx == "user":
            tx = self.user

        self.rt.setTxPose(tx.x, tx.y, tx.z,
                          tx.u + tx.ant[0].u,
                          tx.v + tx.ant[0].v,
                          tx.w + tx.ant[0].w)

        # TODO leave the 4
        for i in range(4):
            self.rt.setRxPose(drone.x, drone.y, drone.z,
                              drone.u + drone.ant[i].u,
                              drone.v + drone.ant[i].v,
                              drone.w + drone.ant[i].w)

            IQ = self.rt.simulate()
            drone.ant[i].setIQ(*IQ)


class Drone(Terminal):
    """docstring for Drone"""
    def __init__(self, x, y, z, u, v, w):
        Terminal.__init__(self, x, y, z, u, v, w)

        # TODO find cleaner way to access antennas
        self._addAntenna(0, 0, 90)  # front
        self._addAntenna(180, 0, 90)  # back
        self._addAntenna(90, 0, 90)  # left-side
        self._addAntenna(-90, 0, 90)  # right-side

    def routine(self, env):

        # Drone-user
        env.scan(self, "user")
        # TODO Remove
        dUser = [538 - self.x, 459 - self.y]
        dUser /= np.linalg.norm(dUser)
        userRss = max([a.rss for a in self.ant])

        # Drone-bs
        env.scan(self, "bs")

        # TODO Remove
        dBs = [96 - self.x, 69 - self.y]
        dBs /= np.linalg.norm(dBs)
        bsRss = max([a.rss for a in self.ant])

        # user RSS < bs RSS -> go to user
        if userRss <= bsRss:
            d = dUser
        else:
            d = dBs

        COEF = 40

        self.x += COEF * d[0]
        self.y += COEF * d[1]


if __name__ == '__main__':
    main(*args())
