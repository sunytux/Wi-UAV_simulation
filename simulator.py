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
from rayTracingWrapper import CloudRT, PathLoss
import numpy as np

# TODO make it clean
RESULT_DIR = tempfile.mkdtemp()
RESULT_DIR = "/tmp/result"
LOG_FILE = "flight.log"

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def main(f):

    user = baseStation(325, 250, 2, 0, 0, 0)
    bs = baseStation(96, 69, 200, 0, 0, 0)
    env = EnvironmentRF(bs, user)

    drone = Drone(176, 290, 100, 0, 0, 0,
                  # antOffset=np.deg2rad(range(0, 360, 20)),
                  routineAlgo="locate",
                  AoAAlgo="weighted-rss")

    for i in range(1, 12):
        LOGGER.debug("Iterration %d", i)
        drone.routine(env)
        # FIXME next iteration of drone info are logged
        log(f, drone, env.user, env.bs)

    f.close()


def log(f, drone, user, bs):
    line = [drone.x, drone.y, user.x, user.y, bs.x, bs.y]
    line += [float(a.rss) for a in drone.ant]
    lineFmt = ",".join(["{:.16f}"] * len(line)) + "\n"
    line = lineFmt.format(*line)

    f.write(line)


def args():
    """Handle arguments for the main function."""

    f = open(LOG_FILE, 'w')

    return [f]


class Antenna(object):
    """docstring for Antenna"""
    def __init__(self, u, v, w):
        self.Re = 0  # I
        self.Im = 0  # Q
        self.u = u
        self.v = v
        self.w = w

    def setIQ(self, Re, Im):
        if Re == 0 and Im == 0:
            LOGGER.warning("Re = 0 and Im = 0")
        self.Im = Im
        self.Re = Re

    @property
    def rss(self):
        # TODO clean that
        if self.Re == 0 and self.Im == 0:
            return -999
        return self.Im**2 + self.Re**2

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

        # self.rt = PathLzoss()
        self.rt = CloudRT(RESULT_DIR, quiteMode=True)

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

        for i in range(len(drone.ant)):
            self.rt.setRxPose(drone.x, drone.y, drone.z,
                              drone.u + drone.ant[i].u,
                              drone.v + drone.ant[i].v,
                              drone.w + drone.ant[i].w)

            IQ = self.rt.simulate()
            drone.ant[i].setIQ(*IQ)


class Drone(Terminal):
    """docstring for Drone"""
    DEFAULT_ANTENNAS_OFFSET = np.deg2rad([0, 90, 180, 270])

    def __init__(self, x, y, z, u, v, w, antOffset=DEFAULT_ANTENNAS_OFFSET,
                 routineAlgo="locate", AoAAlgo="max-rss"):
        Terminal.__init__(self, x, y, z, u, v, w)

        self.antOffset = antOffset

        self.routineAlgo = routineAlgo
        self.AoAAlgo = AoAAlgo

        for offset in self.antOffset:
            self._addAntenna(np.deg2rad(90) + offset, np.deg2rad(90), 0)

    def routine(self, env):
        if self.routineAlgo == "locate":
            self.routine_locate(env)
        elif self.routineAlgo == "optimize":
            self.routine_optimize(env)

    def routine_optimize(self, env):
        # Drone-user
        env.scan(self, "user")
        AoAUser = self.getAoA()
        maxRssUser = max([a.rss for a in self.ant])

        LOGGER.debug('User to drone: AoA = ' + str(np.rad2deg(AoAUser)))
        LOGGER.debug('User to drone: rss = ' + str(np.rad2deg(maxRssUser)))

        # Drone-base-station
        env.scan(self, "bs")
        AoABs = self.getAoA()
        maxRssBs = max([a.rss for a in self.ant])

        LOGGER.debug('Bs to drone: AoA = ' + str(np.rad2deg(AoABs)))
        LOGGER.debug('Bs to drone: rss = ' + str(maxRssBs))

        if maxRssBs > maxRssUser:
            d = [math.cos(AoAUser + self.u), math.sin(AoAUser + self.u)]
        else:
            d = [math.cos(AoABs + self.u), math.sin(AoABs + self.u)]

        COEF = 20

        self.x += COEF * d[0]
        self.y += COEF * d[1]

    def routine_locate(self, env):

        # Drone-user
        env.scan(self, "user")
        AoA = self.getAoA()
        maxRss = max([a.rss for a in self.ant])

        LOGGER.debug('User to drone: AoA = ' + str(np.rad2deg(AoA)))
        LOGGER.debug('User to drone: rss = ' + str(maxRss))

        d = [math.cos(AoA + self.u), math.sin(AoA + self.u)]

        COEF = 20

        self.x += COEF * d[0]
        self.y += COEF * d[1]

    def getAoA(self):
        if self.AoAAlgo == "max-rss":
            return self.getAoA_maxRSS()
        elif self.AoAAlgo == "weighted-rss":
            return self.getAoA_weightedRSS()

    def getAoA_maxRSS(self):
        """Return the estimated AoA using the maximum rss algorithm.

        Return : AoA relative to the drone in radians.
        """
        rss = [(i, self.ant[i].rss) for i in range(len(self.ant))]
        rss = sorted(rss, key=lambda a: a[1])[-1]

        return self.antOffset[rss[0]]

    def getAoA_weightedRSS(self):
        """Return the estimated AoA using the weighted-rss algorithm.

        Return : AoA relative to the drone in radians.
        """
        rss = [(i, self.ant[i].rss) for i in range(len(self.ant))]
        rss = sorted(rss, key=lambda a: a[1])[:-3:-1]

        phi1, rss1 = self.antOffset[rss[0][0]], rss[0][1]
        phi2, rss2 = self.antOffset[rss[1][0]], rss[1][1]

        # When phi1 and phi2 are separated by more than 180° their mean is on
        # the wrong side of the circle
        if max([phi1, phi2]) - min([phi1, phi2]) > np.deg2rad(180):
            if phi1 > phi2:
                phi2 += np.deg2rad(360)
            else:
                phi1 += np.deg2rad(360)

        return (rss1 * phi1 + rss2 * phi2) / (rss1 + rss2)


if __name__ == '__main__':
    main(*args())
