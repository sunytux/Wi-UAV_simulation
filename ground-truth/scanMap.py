#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    scanMap.py -i <INPUT_DIR> -o OUTPUT_DIR -j <INIT_JOB>

Arguments:
    -i INPUT_DIR    Directory with setup files.
    -o OUTPUT_DIR   Output directory.
    -j INIT_JOB     Initial job that will be copied.

Options:
    -h, --help
"""
from myTools.simulator import *
from myTools.parallelize import parallelize
from myTools import utils

from docopt import docopt
import os
import numpy as np

NB_CORE = 6


def main(inputDir, outputDir):
    # TODO clean that
    initJob = utils.readJson(docopt(__doc__)['-j'])

    def initUAVSimulator():
        terminals = []
        for t in initJob['terminals']:
            terminals.append(
                baseStation(t['x'], t['y'], t['z'],
                            t['u'], t['v'], t['w'])
            )

        drone = Drone(
            initJob['drone']['x'],
            initJob['drone']['y'],
            initJob['drone']['z'],
            initJob['drone']['u'],
            initJob['drone']['v'],
            initJob['drone']['w'],
            len(terminals),
            antOffset=np.deg2rad(range(0, 360, 45)),
            routineAlgo="scan",
            AoAAlgo="AoA-algo"
        )

        rt = CloudRT(outputDir, "subrealcity.json", quiteMode=True)

        f = open(os.path.join(outputDir, "flight.csv"), 'w')
        log = Logs(f, drone, terminals)

        env = EnvironmentRF(outputDir, rt, log, terminals, drone)

        return drone, terminals, env, rt, log

    def scan_routine(job, drone, terminals, env, rt, log):
        drone.x = job["drone"]["x"]
        drone.y = job["drone"]["y"]

        drone.routine(job["ID"], env)

    # TODO handle that
    inputDir = os.path.join(inputDir, 'jobs')
    parallelize(inputDir, outputDir, NB_CORE, initUAVSimulator, scan_routine)


def args():
    """Handle arguments for the main function."""

    inputDir = docopt(__doc__)['-i']
    outputDir = docopt(__doc__)['-o']

    return [inputDir, outputDir]


if __name__ == '__main__':
    main(*args())
