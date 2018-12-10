#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    monteCarlo.py

Arguments:

Options:
    -h, --help
"""
from myTools import utils
import simTrajectory
import numpy as np
import os
import tempfile

MAP_X = 650
MAP_Y = 500
STEP = 10

N = 1000

INITIAL_CONF = 'job_sample/monteCarlo.json'
OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def main():
    xRand = np.random.uniform(0, MAP_X, N) // STEP * STEP
    yRand = np.random.uniform(0, MAP_Y, N) // STEP * STEP

    i = 0
    for x, y in zip(xRand, yRand):
        exp = utils.readJson(INITIAL_CONF)
        exp['drone']['x'] = x
        exp['drone']['y'] = y
        exp['simulation-output-csv'] = tempfile.NamedTemporaryFile(
            dir=OUTPUT_DIR,
            suffix='.csv'
        ).name

        simTrajectory.run(exp)
        i += 1
        if i % 100:
            print(str(float(i) * 100 / N) + "%")


def args():
    """Handle arguments for the main function."""

    return []


if __name__ == '__main__':
    main(*args())
