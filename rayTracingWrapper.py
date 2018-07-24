#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Wrapper for CloudRT ray tracing matlab simulator.

In the context of 1 drone, 1 User
Warning: This is written in python 2.7 for matlab engine compatibility (beurk).

Usage:
    rayTracingWrapper.py

Arguments:

Options:
    -h, --help
"""
import matlab.engine
import os
import tempfile
import StringIO

# TODO find a cleaner way to handle directories
RESULT_DIR = tempfile.mkdtemp()


class CloudRT():
    """docstring for CloudRT wrapper"""

    CLOUDRT_DIR = os.path.join(os.getcwd(), "CloudRT_app")

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

        self.simIdx = 0

    def simulate(self):
        self.conf, CTF_Re, CTF_Im = self.eng.simulate(self.conf,
                                                      self.resultDir,
                                                      self.simIdx,
                                                      nargout=3, **self.opt)
        self.simIdx += 1
        return CTF_Re, CTF_Im

    def setTxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setTxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, **self.opt)

    def setRxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setRxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, **self.opt)


def main():

    rt = CloudRT(RESULT_DIR)

    rt.setTxPose(300, 100, 40, 0, 180, 0)

    CTF_Im = rt.simulate()
    print("The computed CTF_Im", CTF_Im)

    rt.setTxPose(50, 200, 40, 0, 180, 0)

    CTF_Im = rt.simulate()
    print("The computed CTF_Im", CTF_Im)


if __name__ == '__main__':
    main()
