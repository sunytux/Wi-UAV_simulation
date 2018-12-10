#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Wrapper for CloudRT ray tracing matlab simulator.

Warning: This is written in python 2.7 for matlab engine compatibility (beurk).

Usage:
    CloudRT.py

Arguments:

Options:
    -h, --help
"""
import matlab.engine
import os
import StringIO
import tempfile
import pandas as pd
import numpy as np


class CloudRT():
    """docstring for CloudRT wrapper"""

    CLOUDRT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "CloudRT_app")

    def __init__(self, resultDir, scenario="Plank.json", quiteMode=False):
        self.resultDir = resultDir
        self.confFile = tempfile.NamedTemporaryFile(suffix='.json').name

        self.opt = {}
        if quiteMode:
            self.opt = {"stdout": StringIO.StringIO()}

        self.eng = matlab.engine.start_matlab()
        self.eng.cd(self.CLOUDRT_DIR)

        self.conf = self.eng.initConf(self.confFile, resultDir,
                                      scenario, **self.opt)

        self.setTxPose(0, 0, 0, 0, 0, 0)
        self.setRxPose(0, 0, 0, 0, 0, 0)

    def simulate(self, simId):
        self.conf, CTF_Re, CTF_Im = self.eng.simulate(self.conf,
                                                      self.confFile,
                                                      self.resultDir,
                                                      simId,
                                                      nargout=3, **self.opt)

        return CTF_Re, CTF_Im

    def setTxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setTxPose(self.conf, self.confFile,
                                       self.resultDir,
                                       x, y, z, u, v, w, **self.opt)

    def setRxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setRxPose(self.conf, self.confFile,
                                       self.resultDir,
                                       x, y, z, u, v, w, **self.opt)


class CloudRT_DataBase():
    """Ray-tracer object with pre-computed results.

       terminals is a list of N terminals represented by a dict formatted as
       follow:
       [{"x" :386, "y" :272, "z" :1.8, "u" :0, "v" :0, "w" :0}, ...]
    """

    STEP = 10

    def __init__(self, terminals, dbFile):
        self.terminals = terminals

        # TODO clean that shit
        DEFAULT_ANTENNAS_OFFSET = np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315])
        self.terminalOffsets = []
        for offset in DEFAULT_ANTENNAS_OFFSET:
            self.terminalOffsets.append(
                [np.deg2rad(90) + offset, np.deg2rad(90 + 45), 0]
            )

        self.rx = [0 for i in range(6)]
        self.tx = [0 for i in range(6)]

        self.df = pd.read_csv(dbFile, index_col=0)

    def simulate(self, simId):
        x, y = self.determineDronePosition()
        userIdx, antIdx = self.determineAntenna()

        row = self.df[(self.df['x'] == x) &
                      (self.df['y'] == y) &
                      (self.df['user'] == userIdx) &
                      (self.df['ant'] == antIdx)]

        return float(row['re']), float(row['im'])

    def setTxPose(self, x, y, z, u, v, w):
        self.tx = [x, y, z, u, v, w]

    def setRxPose(self, x, y, z, u, v, w):
        # TODO handle out of the map
        self.rx = [x, y, z, u, v, w]

    def determineDronePosition(self):
        x = (self.rx[0] // 10) * 10 % 640  # TODO clean that
        y = (self.rx[1] // 10) * 10 % 500  # TODO clean that
        return x, y

    def determineAntenna(self):
        userIdx = self.terminals.index(
            {"x": self.tx[0], "y": self.tx[1], "z": self.tx[2],
             "u": self.tx[3], "v": self.tx[4], "w": self.tx[5]}
        )
        antIdx = self.terminalOffsets.index(
            [self.rx[3], self.rx[4], self.rx[5]]
        )

        return userIdx, antIdx
