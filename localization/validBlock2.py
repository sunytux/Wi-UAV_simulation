#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

""" Script for the validation of the 2nd block of the localisation process

Usage:
    validBlock2.py

Options:
    -h, --help
"""
import matplotlib.pyplot as plt
import math

from scipy.stats import norm

from myTools.simulator import *
from myTools import plot
from myTools import utils


USER = 4
# MINIMUM_MEM = 10
STEP = 100

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
    "use-database": True,
    "routine-algo": "locate2",
    "AoA-algo": "weighted-rss",
    "max-iteration": 20,

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

    memAoA = [[]] * len(terminals)
    # for time in range(exp['max-iteration']):
    i = 0

    for x in range(0, 650, STEP):
        for y in range(0, 500, STEP):
            drone.x = x
            drone.y = y

            env.scan(i, USER)
            AoA = drone.getAoA()
            memAoA[USER].append([drone.x, drone.y, AoA])

            # drone.x = (random.randint(0, drone.MAX_X) // 10) * 10
            # drone.y = (random.randint(0, drone.MAX_Y) // 10) * 10

            i += 1
    f.close()

    # plotAoA(memAoA, exp)
    plotCostFct(memAoA, exp)


def plotCostFct(memAoA, exp):
    stepGridSearch = STEP
    stepGridSearch = 10
    X, Y, cost = [], [], []

    for x in range(0, 650, stepGridSearch):
        for y in range(0, 500, stepGridSearch):
            X.append(x)
            Y.append(y)
            cost.append(costFctNormal(x, y, memAoA))
            # cost.append(costFctMSE(x, y, memAoA))

    hestIdx = np.argmax(cost)
    x_hest = X[hestIdx]
    y_hest = Y[hestIdx]

    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals(exp['terminals'])

    W = np.ones(len(X)) * stepGridSearch
    H = np.ones(len(X)) * stepGridSearch

    plt.plot(x_hest, y_hest, marker="*", markersize=10,
             color='white', markeredgecolor='black')

    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    plot.plot_heatmap(X, Y, cost, W, H, legend="Cost")

    plt.show()


def costFctNormal(x, y, memAoA):
    MU1 = np.deg2rad(-0.03)  # RADIAN !
    SIGMA1 = np.deg2rad(27.011)
    MU2 = np.deg2rad(178.684)
    SIGMA2 = np.deg2rad(28.324)
    alpha = 0.905538461538

    cost = 1

    for xUAV, yUAV, aoa in memAoA[USER]:
        aou = math.atan2(y - yUAV,
                         x - xUAV)
        error = utils.realAngle(aoa - aou)
        diffMu1 = utils.realAngle(error - MU1)
        diffMu2 = utils.realAngle(error - MU2)

        term = alpha * norm.pdf(diffMu1, 0, SIGMA1) +\
            (1 - alpha) * norm.pdf(diffMu2, 0, SIGMA2)

        cost *= term
    return cost


def costFctMSE(x, y, memAoA):
    """ Mean Squared Error cost function """
    cost = 0

    for xUAV, yUAV, aoa in memAoA[USER]:
        aou = math.atan2(y - yUAV,
                         x - xUAV)
        error = aoa - aou
        if error > np.deg2rad(180):
            error -= np.deg2rad(360)
        elif error < np.deg2rad(-180):
            error += np.deg2rad(360)

        cost += error ** 2

    return cost


def plotAoA(memAoA, exp):
    # Plot results
    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals(exp['terminals'])

    X = np.array(memAoA[USER])[:, 0]
    Y = np.array(memAoA[USER])[:, 1]
    THETA = np.array(memAoA[USER])[:, 2]
    U = np.cos(THETA)
    V = np.sin(THETA)
    plt.quiver(X, Y, U, V, zorder=3)

    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    plt.show()


if __name__ == '__main__':
    run(DEFAULT_CONF)
