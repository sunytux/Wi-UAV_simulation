#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

""" Script for the validation of the 2nd block of the localisation process

Usage:
    validBlock2.py [-m MODE] -o DIR

Arguments:
    -o DIR          Output directory.

Options:
    -h, --help
    -m MODE         UAV trajectory mode.
"""
from myTools.simulator import *
from myTools import plot
from myTools import utils
from myTools import DEFAULT_CONF

from docopt import docopt
from scipy.stats import norm
import matplotlib.pyplot as plt

import math
import random

USER = 4
STEP = 100

MODE = "horiz"
USE_DB = False

MU1 = np.deg2rad(-0.03)  # RADIAN !
SIGMA1 = np.deg2rad(27.011)
MU2 = np.deg2rad(178.684)
SIGMA2 = np.deg2rad(28.324)
ALPHA = 0.905538461538

EXP = DEFAULT_CONF
EXP.update({
    "routine-algo": "scan",
    "AoA-algo": "weighted-rss"
})


def main(mode, outputDir):

    drone, terminals, env, rt, log = readConfig(EXP)

    memAoA = [[]] * len(terminals)

    if mode == "grid":
        gridTrajectory(drone, env, memAoA)
    elif mode == "random":
        randomTrajectory(drone, env, memAoA, 20)
    elif mode == "horiz":
        horizTrajectory(drone, env, memAoA, 20)
    elif mode == "vert":
        vertTrajectory(drone, env, memAoA, 20)

    log.close()

    # plotAoA(memAoA)
    plotCostFct(memAoA)

    plt.gcf().savefig(
        os.path.join(outputDir, "cost-fct-user-" + str(USER)),
        bbox_inches='tight',
        dpi=300
    )


def randomTrajectory(drone, env, memAoA, iteration):
    for i in range(iteration):
        drone.x = (random.randint(0, drone.MAX_X) // 10) * 10
        drone.y = (random.randint(0, drone.MAX_Y) // 10) * 10

        env.scan(i, USER)
        AoA = drone.getAoA()
        memAoA[USER].append([drone.x, drone.y, AoA])


def horizTrajectory(drone, env, memAoA, iteration):
    drone.x = 50
    drone.y = 350
    for i in range(iteration):
        env.scan(i, USER)
        AoA = drone.getAoA()
        memAoA[USER].append([drone.x, drone.y, AoA])

        drone.x = (drone.x + 30) % drone.MAX_X


def vertTrajectory(drone, env, memAoA, iteration):
    drone.x = 100
    drone.y = 20
    for i in range(iteration):
        env.scan(i, USER)
        AoA = drone.getAoA()
        memAoA[USER].append([drone.x, drone.y, AoA])

        drone.y = (drone.y + 25) % drone.MAX_Y


def gridTrajectory(drone, env, memAoA):
    i = 0
    for x in range(0, 650, STEP):
        for y in range(0, 500, STEP):
            drone.x = x
            drone.y = y

            env.scan(i, USER)
            AoA = drone.getAoA()
            memAoA[USER].append([drone.x, drone.y, AoA])
            i += 1


def plotCostFct(memAoA):
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
    plot.plot_terminals(EXP['terminals'])

    W = np.ones(len(X)) * stepGridSearch
    H = np.ones(len(X)) * stepGridSearch

    # The trajectory
    xUAV = [mem[0] for mem in memAoA[USER]]
    yUAV = [mem[1] for mem in memAoA[USER]]
    plt.plot(xUAV, yUAV, 'ko', markersize=3, color='white')

    # The estimated Tx position
    plt.plot(x_hest, y_hest, marker="*", markersize=10,
             color='white', markeredgecolor='black')

    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    plot.plot_heatmap(X, Y, cost, W, H, legend="Cost")


def costFctNormal(x, y, memAoA):
    cost = 1

    for xUAV, yUAV, aoa in memAoA[USER]:
        aou = math.atan2(y - yUAV,
                         x - xUAV)
        error = utils.realAngle(aoa - aou)
        diffMu1 = utils.realAngle(error - MU1)
        diffMu2 = utils.realAngle(error - MU2)

        term = ALPHA * norm.pdf(diffMu1, 0, SIGMA1) +\
            (1 - ALPHA) * norm.pdf(diffMu2, 0, SIGMA2)

        cost *= term

    if USE_DB:
        cost = utils.nat2db(cost)

    return cost


def costFctMSE(x, y, memAoA):
    """ Mean Squared Error cost function """
    cost = 0

    for xUAV, yUAV, aoa in memAoA[USER]:
        aou = math.atan2(y - yUAV, x - xUAV)
        error = utils.realAngle(aoa - aou)

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


def args():
    """Handle arguments for the main function."""

    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    if docopt(__doc__)['-m']:
        mode = docopt(__doc__)['-m']
    else:
        mode = MODE

    return [mode, outputDir]


if __name__ == '__main__':
    main(*args())
