#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Wrapper for CloudRT ray tracing matlab simulator.

Warning: This is written in python 2.7 for matlab engine compatibility (beurk).

Usage:
    rayTracingWrapper.py

Arguments:

Options:
    -h, --help
"""
import matlab.engine
import os
import StringIO


class CloudRT():
    """docstring for CloudRT wrapper"""

    CLOUDRT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "CloudRT_app")

    def __init__(self, resultDir, quiteMode=False):
        self.resultDir = resultDir

        self.opt = {}
        if quiteMode:
            self.opt = {"stdout": StringIO.StringIO()}

        self.eng = matlab.engine.start_matlab()
        self.eng.cd(self.CLOUDRT_DIR)

        self.conf = self.eng.initConf(resultDir, **self.opt)

        self.setTxPose(0, 0, 0, 0, 0, 0)
        self.setRxPose(0, 0, 0, 0, 0, 0)

    def simulate(self, simId):
        self.conf, CTF_Re, CTF_Im = self.eng.simulate(self.conf,
                                                      self.resultDir,
                                                      simId,
                                                      nargout=3, **self.opt)

        return CTF_Re, CTF_Im

    def setTxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setTxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, **self.opt)

    def setRxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setRxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, **self.opt)
