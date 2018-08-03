#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    scanMap.py [-i <INPUT_DIR>] [-o OUTPUT_DIR]

Arguments:

Options:
    -i INPUT_DIR    Directory with setup files [default: ./input].
    -o OUTPUT_DIR   Output directory [default: /tmp/result].
    -h, --help
"""
import logging
from backend import *
from docopt import docopt
import os

NB_CORE = 3

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def main(inputDir, outputDir):
    def initUAVSimulator():

        terminals = [
            baseStation(55, 77, 76, 0, 0, 0),
            baseStation(325, 250, 1.8, 0, 0, 0),
            baseStation(425, 125, 1.8, 0, 0, 0),
            baseStation(225, 350, 1.8, 0, 0, 0),
            baseStation(225, 50, 1.8, 0, 0, 0),
        ]

        drone = Drone(110, 420, 100, 0, 0, 0,
                      len(terminals),
                      antOffset=np.deg2rad(range(0, 360, 45)),
                      routineAlgo="scan",
                      AoAAlgo="AoA-algo")

        rt = CloudRT(outputDir, "subrealcity.json", quiteMode=True)

        f = open(os.path.join(outputDir, "flight.csv"), 'w')
        log = Logs(f, drone, terminals)

        env = EnvironmentRF(outputDir, rt, log, terminals, drone)

        return drone, terminals, env, rt, log

    def scan_routine(job, drone, terminals, env, rt, log):
        drone.x = job["drone"]["x"]
        drone.y = job["drone"]["y"]

        drone.routine(job["ID"], env)

    parallelize(inputDir, outputDir, NB_CORE, initUAVSimulator, scan_routine)


def args():
    """Handle arguments for the main function."""

    inputDir = docopt(__doc__)['-i']
    outputDir = docopt(__doc__)['-o']

    return [inputDir, outputDir]


if __name__ == '__main__':
    main(*args())
