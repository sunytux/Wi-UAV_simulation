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

# TODO find a cleaner way to handle directories
PROJECT_PWD = "/home/sami/desk/wireless_UAV_simulator/" \
              "CloudRT_+_UAV_simulator/project/subcity"


class CloudRT():
    """docstring for CloudRT wrapper"""
    def __init__(self, CloudRTPath):
        self.CloudRTPath = CloudRTPath

        self.eng = matlab.engine.start_matlab()
        self.eng.cd(CloudRTPath)

        self.conf = self.eng.initConf(CloudRTPath)

    def simulate(self):
        self.conf, result = self.eng.simulate(self.conf,
                                              self.CloudRTPath,
                                              nargout=2)
        self.eng.workspace['result'] = result

        # TODO define what metric should be used
        CTF_Im = self.eng.eval('result.result.CTF_Im')

        return CTF_Im

    def updateDronePosition(self, x, y):
        self.conf = self.eng.updateDronePosition(self.conf,
                                                 self.CloudRTPath,
                                                 x, y)


def main():

    rt = CloudRT(PROJECT_PWD)

    rt.updateDronePosition(300, 100)

    CTF_Im = rt.simulate()
    print("The computed CTF_Im", CTF_Im)

    rt.updateDronePosition(50, 200)

    CTF_Im = rt.simulate()
    print("The computed CTF_Im", CTF_Im)


if __name__ == '__main__':
    main()
