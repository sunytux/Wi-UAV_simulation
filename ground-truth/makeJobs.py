#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    makeJobs.py [-i <INPUT_DIR>]

Arguments:

Options:
    -i INPUT_DIR    Directory with setup files [default: ./input].
    -h, --help
"""
# TODO I am not happy with that
import sys
sys.path.insert(0, "../")
from myTools import utils

import logging
from docopt import docopt
import os
import numpy as np


STEP = 10  # m
MAP_X_SIZE = 650  # m
MAP_Y_SIZE = 500   # m

PRIOR_X_RANGE = [300, 550]
PRIOR_Y_RANGE = [100, 275]


def main(inputDir):

    jobDir = os.path.join(inputDir, 'jobs')
    priorDir = os.path.join(jobDir, 'prior')
    if not os.path.exists(jobDir):
        os.makedirs(jobDir)
        os.makedirs(priorDir)

    coordTable = np.zeros((MAP_X_SIZE / STEP, MAP_Y_SIZE / STEP))
    thisJobId = 0
    for i in range(0, MAP_X_SIZE / STEP):
        for j in range(0, MAP_Y_SIZE / STEP):

            thisJobId += 1
            coordTable[i, j] = thisJobId

            thisJob = utils.readJson('initialJob.json')
            thisJob["ID"] = thisJobId
            thisJob["drone"]["x"] = i * STEP
            thisJob["drone"]["y"] = j * STEP

            if (PRIOR_X_RANGE[0] < i * STEP < PRIOR_X_RANGE[1] and
                    PRIOR_Y_RANGE[0] < j * STEP < PRIOR_Y_RANGE[1]):
                thisJobDir = priorDir
            else:
                thisJobDir = jobDir
            thisJobFile = os.path.join(thisJobDir,
                                       '{:06d}.json'.format(thisJobId))
            utils.writeJson(thisJobFile, thisJob)

    utils.writeJson(os.path.join(inputDir, 'table.json'), coordTable.tolist())


def args():
    """Handle arguments for the main function."""
    inputDir = docopt(__doc__)['-i']
    if 'UAV_DATA_DIR' in os.environ:
        inputDir.replace("$UAV_DATA_DIR",
                         os.environ['UAV_DATA_DIR'])

    return [inputDir]


if __name__ == '__main__':
    main(*args())
