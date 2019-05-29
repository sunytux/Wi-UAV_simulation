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
    simulator.py [-i ITER] [-o DIR]

Arguments:

Options:
    -i ITER         Iterations [default: 12].
    -o DIR          Output directory [default: /tmp/result].
    -h, --help
"""
import math
import numpy as np

from CloudRT import *
from myTools import LOGGER
from myTools import utils
import ukflib


class Logs(object):
    """docstring for Logs"""

    def __init__(self, logFile, drone, terminals):
        self.logFile = logFile
        header = self._makeHeader(drone, terminals)
        self.logFile.write(header)

    def _makeHeader(self, drone, terminals):
        def expand(t):
            return [t + ".x", t + ".y", t + ".z", t + ".u", t + ".v", t + ".w"]

        header = [
            "time", "simIdxs",
        ]
        header += expand("drone")
        for i in range(len(terminals)):
            header += expand("user-" + str(i))
        header += ["ant." + str(i) for i in range(len(drone.ant))]

        return ",".join(header) + '\n'

    def save(self, time, simIdxs, drone, terminals):
        rss = [a.rss for a in drone.ant]

        def expand(t):
            return [t.x, t.y, t.z, t.u, t.v, t.w]

        row = [
            time, simIdxs,
        ]
        row += expand(drone)
        for t in terminals:
            row += expand(t)
        row += rss

        lineFmt = "{:d},{:s}" + ",{:.16f}" * (len(row) - 2) + '\n'

        self.logFile.write(lineFmt.format(*row))

    def close(self):
        self.logFile.close()


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
            LOGGER.warn("Computed IQ are too low; Re = Im = 1e-12.")
            Re = Im = 1e-12
        self.Im = Im
        self.Re = Re

    @property
    def rss(self):
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

    def __init__(self, rt, log, terminals, drone):

        self.terminals = terminals
        self.drone = drone

        self.rt = rt
        self.log = log

    def scan(self, time, txIdx):
        """Compute received signal on drone antennas for a given situation."""

        tx = self.terminals[txIdx]

        self.rt.setTxPose(tx.x, tx.y, tx.z,
                          tx.u + tx.ant[0].u,
                          tx.v + tx.ant[0].v,
                          tx.w + tx.ant[0].w)

        for i in range(len(self.drone.ant)):
            self.rt.setRxPose(self.drone.x, self.drone.y, self.drone.z,
                              self.drone.u + self.drone.ant[i].u,
                              self.drone.v + self.drone.ant[i].v,
                              self.drone.w + self.drone.ant[i].w)

            IQ = self.rt.simulate(self.getSimID(txIdx, time, i))
            self.drone.ant[i].setIQ(*IQ)

        simIds = self.getSimID(txIdx, time, i)[0:-6]

        self.log.save(time, simIds, self.drone, self.terminals)

    def getSimID(self, userIdx, time, antenna):
        return "u{:02d}-t{:06d}-ant{:02d}".format(userIdx, time, antenna)


class Drone(Terminal):
    """docstring for Drone"""

    DEFAULT_ANTENNAS_OFFSET = np.deg2rad([0, 90, 180, 270])

    # TODO make it map agnostic
    MAX_X = 650
    MAX_Y = 500

    def __init__(self, x, y, z, u, v, w, nbUsers,
                 antOffset=DEFAULT_ANTENNAS_OFFSET,
                 routineAlgo="locate",
                 routineKwargs={},
                 AoAAlgo="weighted-rss"):
        Terminal.__init__(self, x, y, z, u, v, w)

        self.nbUsers = nbUsers
        self.antOffset = antOffset

        self.routineAlgo = routineAlgo
        self.routineKwargs = routineKwargs
        self.AoAAlgo = AoAAlgo

        for offset in self.antOffset:
            self._addAntenna(np.deg2rad(90) + offset, np.deg2rad(90 + 45), 0)

        if routineAlgo == "locate_kalman":
            self.ukf = self._init_kalman_routine()

    def routine(self, time, env):
        if self.routineAlgo == "locate":
            self.routine_locate(time, env)

        elif self.routineAlgo == "optimize":
            self.routine_optimize(time, env)

        elif self.routineAlgo == "scan":
            self.routine_scan(time, env)

        elif routineAlgo == "locate_kalman":
            self.routine_locate_kalman(time, env)

    def routine_scan(self, time, env):
        for userIdx in range(self.nbUsers):
            # LOGGER.debug('Scanning user  ' + str(userIdx))
            env.scan(time, userIdx)
            LOGGER.info('RSS on terminal ' + str(userIdx) + ': ' +
                        str([utils.nat2db(a.rss) for a in self.ant]))

    def routine_optimize(self, time, env):
        AoA = 0
        maxRss = -1
        for i in range(self.nbUsers):
            env.scan(time, i)
            LOGGER.debug('Scanning for user ' + str(i))
            userAoA = self.getAoA()
            userRss = max([a.rss for a in self.ant])
            if userRss < maxRss or maxRss == -1:  # TODO clean that
                AoA = userAoA
                maxRss = userRss
                userIdx = i

        LOGGER.debug('User ' + str(userIdx) + 'is the weakest')

        d = [math.cos(AoA + self.u), math.sin(AoA + self.u)]

        COEF = 50

        self.x += COEF * d[0]
        self.y += COEF * d[1]

        self.x = 0 if self.x < 0 else self.x
        self.x = self.MAX_X if self.x > self.MAX_X else self.x
        self.y = 0 if self.y < 0 else self.y
        self.y = self.MAX_Y if self.y > self.MAX_Y else self.y

    def routine_locate(self, time, env):
        USER = 1  # TODO add support for other users

        # Drone-user
        env.scan(time, USER)
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

    def _init_kalman_routine(self):
        processNoise = self.routineKwargs["processNoise"]
        measurementNoise = self.routineKwargs["measurementNoise"]
        sigma0 = self.routineKwargs["sigma0"]
        firstGuess = self.routineKwargs["firstGuess"]

        P0 = np.eye(2) * sigma0 ** 2

        L = 2  # State dimension (xTx and yTx)
        # Process noise, no physical meaning, it just represents how much you
        # trust your model
        Rv = np.diag([processNoise, processNoise])
        Rn = np.diag([measurementNoise])

        return ukflib.UnscentedKalmanFilter(
            L, Rv, Rn,
            init_state=firstGuess,
            kappa=0,
            alpha=1.0,
            beta=2,
            angle_mask=[0, 0],  # state xTx and yTx are not angles
            init_covariance=P0
        )

    def routine_locate_kalman(self, time, env):
        # Step 1 prediction
        self.ukf.predict(self._locate_kalman_predict)

        # Step 2 correction
        env.scan(time, self.routineKwargs["user"])
        z = utils.realAngle(self.getAoA())

        self.ukf.update(self._locate_kalman_measurement, z, self.x, self.y)

    def _locate_kalman_predict(self, state, noise):
        """Propagation function callback.

        Args
            state and noise

        Returns
            The next state.

        """

        return state + noise

    def _locate_kalman_measurement(self, state, noise, xUav, yUav):
        """Measurement function callback.

        Args
            state and noise.

        Returns
            The measurement.

        """
        z = math.atan2(state[1] - yUav,
                       state[0] - xUav) + noise
        z = utils.realAngle(z)

        return z


def readConfig(exp):
    f = open(exp['simulation-output-csv'], 'w')

    terminals = []
    for t in exp['terminals']:
        terminals.append(
            baseStation(t["x"], t["y"], t["z"], t["u"], t["v"], t["w"])
        )

    drone = Drone(
        exp["drone"]["x"], exp["drone"]["y"], exp["drone"]["z"],
        exp["drone"]["u"], exp["drone"]["v"], exp["drone"]["w"],
        len(terminals),
        antOffset=np.deg2rad(exp["antenna-offsets"]),
        routineAlgo=exp["routine-algo"],
        routineKwargs=exp["routineKwargs"],
        AoAAlgo=exp["AoA-algo"]
    )

    if exp['use-database']:
        rt = CloudRT_DataBase(exp['terminals'], exp['use-database'])
    else:
        rt = CloudRT(
            exp['CloudRT-output-dir'],
            scenario=exp["scenario"],
            quiteMode=exp["matlab-quite-mode"]
        )

    log = Logs(f, drone, terminals)

    env = EnvironmentRF(rt, log, terminals, drone)

    return drone, terminals, env, rt, log
