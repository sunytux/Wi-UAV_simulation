#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Wireless UAV simulator.

This script aims at validating UAV trajectory planner in the context of
wireless UAV networks by computing several channel metrics along its path. This
is done in an iterative manner. At each position, the received signals on the
four UAV's antennas is simulated with an external Matlab simulator, which is
then used by the trajectory planner to compute the next UAV position and
orientation.

# TODO The stop condition is ...


It takes as input: user, base-station (BS) and UAV initial conditions as well
as a map of the environment and returns a complete set of information
describing both the UAV and the environment at every moment.

Usage:
    simTrajectory.py -i <INPUT_FILE>

Arguments:
    -i <INPUT_FILE> Path to Json file of the experience.

Options:
    -h, --help
"""
from myTools import LOGGER
from myTools.simulator import *
from myTools import utils
from docopt import docopt


DB_FILE = "/home/sami/docs/phd/projects/04_wireless_UAV_simulator/data/"\
          "ground-truth/ground-truth-map.csv"
DEFAULT_CONF = {
    # Setup
    "scenario": "subrealcity.json",
    "drone": {"x": 325, "y": 250, "z": 100, "u": 0, "v": 0, "w": 0},
    "antenna-offsets": [0, 90, 180, 270],
    "terminals": [
        {"x": 55, "y": 77, "z": 76, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 244, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 386, "y": 272, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 144, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 308, "y": 121, "z": 1.8, "u": 0, "v": 0, "w": 0}
    ],

    # Algorithm options
    "use-database": False,
    "routine-algo": "optimize",
    "AoA-algo": "weighted-rss",
    "max-iteration": 12,

    # Output files
    "simulation-output-csv": "/tmp/sim/flight.csv",
    "CloudRT-output-dir": "/tmp/sim/CloudRT",

    # Logs flags
    "matlab-quite-mode": True
}


def run(exp):
    f = open(exp['simulation-output-csv'], 'w')

    terminals = []
    for t in exp['terminals']:
        terminals.append(
            baseStation(t["x"], t["y"], t["z"], t["u"], t["v"], t["w"])
        )

    drone = Drone(
        exp["drone"]["x"], exp["drone"]["y"], exp["drone"]["z"],
        exp["drone"]["u"], exp["drone"]["v"], exp["drone"]["w"],
        len(terminals),
        antOffset=np.deg2rad(exp["antenna-offsets"]),
        routineAlgo=exp["routine-algo"],
        AoAAlgo=exp["AoA-algo"]
    )

    if exp['use-database']:
        rt = CloudRT_DataBase(exp['terminals'], DB_FILE)
    else:
        rt = CloudRT(
            exp['CloudRT-output-dir'],
            scenario=exp["scenario"],
            quiteMode=exp["matlab-quite-mode"]
        )

    log = Logs(f, drone, terminals)

    env = EnvironmentRF(rt, log, terminals, drone)

    for i in range(exp['max-iteration']):
        LOGGER.debug("Iterration %d", i)
        drone.routine(i, env)

    f.close()


def args():
    """Handle arguments for the main function."""

    inputFile = docopt(__doc__)['-i']
    exp = DEFAULT_CONF
    exp.update(utils.readJson(inputFile))

    return [exp]


if __name__ == '__main__':
    run(*args())
