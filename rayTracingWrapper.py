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
import math
import numpy as np

# TODO remove this feature
import StringIO

# TODO find a cleaner way to handle directories
RESULT_DIR = tempfile.mkdtemp()


class CloudRT():
    """docstring for CloudRT wrapper"""

    CLOUDRT_DIR = os.path.join(os.getcwd(), "CloudRT_app")

    def __init__(self, resultDir):
        self.resultDir = resultDir
        self.out = StringIO.StringIO()

        self.eng = matlab.engine.start_matlab()
        self.eng.cd(self.CLOUDRT_DIR)

        self.conf = self.eng.initConf(resultDir, stdout=self.out)

        # Setting initial Drone/User positions
        # Random place outside of a building: (538, 459)
        self.setTxPose(100, 100, 40, 0, 180, 0)
        self.setRxPose(538, 459, 2, 0, 0, 0)

    def simulate(self):
        self.conf, result = self.eng.simulate(self.conf,
                                              self.resultDir,
                                              nargout=2, stdout=self.out)
        self.eng.workspace['result'] = result

        # TODO define what metric should be used
        # TODO define which idx
        CTF_Re = self.eng.eval('single(result.result.CTF_Re(1))')
        CTF_Im = self.eng.eval('single(result.result.CTF_Im(1))')

        return CTF_Re, CTF_Im

    def setTxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setTxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, stdout=self.out)

    def setRxPose(self, x, y, z, u, v, w):
        self.conf = self.eng.setRxPose(self.conf, self.resultDir,
                                       x, y, z, u, v, w, stdout=self.out)


class PathLoss(object):
    """docstring for PathLoss"""

    P = 10
    n = 10
    K = 100
    b = 10
    f = 2.57e9

    def __init__(self):
        self.tx_x = 0
        self.tx_y = 0
        self.tx_z = 0
        self.tx_u = 0
        self.tx_v = 0
        self.tx_w = 0
        self.rx_x = 0
        self.rx_y = 0
        self.rx_z = 0
        self.rx_u = 0
        self.rx_v = 0
        self.rx_w = 0

    def setTxPose(self, x, y, z, u, v, w):
        self.tx_x = x
        self.tx_y = y
        self.tx_z = z
        self.tx_u = u
        self.tx_v = v
        self.tx_w = w

    def setRxPose(self, x, y, z, u, v, w):
        self.rx_x = x
        self.rx_y = y
        self.rx_z = z
        self.rx_u = u
        self.rx_v = v
        self.rx_w = w

    def simulate(self):
        d = np.linalg.norm([self.tx_x - self.rx_x,
                            self.tx_y - self.rx_y,
                            self.tx_z - self.rx_z])

        Pdb = 10 * self.n * math.log10(d)
        Pdb += -10 * math.log10(self.K)
        Pdb += 10 * self.b * math.log10(self.f)

        # TODO I don't know what I'm doing xD
        P = 0 - Pdb

        CTF_Re = math.sqrt(math.pow(10, P / 10) / 20)
        CTF_Im = CTF_Re

        return CTF_Re, CTF_Im


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
