#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

""" Script for the validation of the 2nd block of the localisation process

Usage:
    validBlock2.py

Options:
    -h, --help
"""
from myTools.simulator import *
from myTools import plot
from myTools import utils
from myTools import DEFAULT_CONF

from scipy.stats import norm
import matplotlib.pyplot as plt

import math


USER = 4
STEP = 100


def run():

    drone, terminals, env, rt, log = readConfig(DEFAULT_CONF)

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
    log.close()

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
    run()
