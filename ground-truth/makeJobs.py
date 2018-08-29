#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    makeJobs.py -i <INPUT_DIR> -j <INIT_JOB>

Arguments:
    -i INPUT_DIR    Directory with setup files.
    -j INIT_JOB     Initial job that will be copied.

Options:
    -h, --help
"""

from myTools import utils
from docopt import docopt
import os
import numpy as np


STEP = 10  # m
MAP_X_SIZE = 650  # m
MAP_Y_SIZE = 500   # m


def main(inputDir, initialJob):

    jobDir = os.path.join(inputDir, 'jobs')
    if not os.path.exists(jobDir):
        os.makedirs(jobDir)

    coordTable = np.zeros((MAP_X_SIZE / STEP, MAP_Y_SIZE / STEP))
    thisJobId = 0
    for i in range(0, MAP_X_SIZE / STEP):
        for j in range(0, MAP_Y_SIZE / STEP):

            thisJobId += 1
            coordTable[i, j] = thisJobId

            thisJob = utils.readJson(initialJob)
            thisJob["ID"] = thisJobId
            thisJob["drone"]["x"] = i * STEP
            thisJob["drone"]["y"] = j * STEP

            thisJobDir = jobDir
            thisJobFile = os.path.join(thisJobDir,
                                       '{:06d}.json'.format(thisJobId))
            utils.writeJson(thisJobFile, thisJob)


def args():
    """Handle arguments for the main function."""
    inputDir = docopt(__doc__)['-i']
    initialJob = docopt(__doc__)['-j']

    return [inputDir, initialJob]


if __name__ == '__main__':
    main(*args())
