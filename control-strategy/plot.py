#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot and save figures of flight logs.

Usage:
    plot.py -d <FLIGHT_LOG> -o DIR

Arguments:
    -d <FLIGHT_LOG>  Path to flight logs.
    -o DIR           Output directory.

Options:
    -h, --help
"""
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from docopt import docopt
import os
from myTools import plot


def main(csvPath, resultDir):
    time, sim, drone, users, rss = readData(csvPath)

    # TODO find better way
    for user in range(len(users)):
        d = os.path.join(resultDir, "user-" + str(user))
        if not os.path.exists(d):
            os.makedirs(d)

    # Plot the flight trajectory
    plotFlight(drone, users)
    figureName = os.path.join(resultDir, "flight.png")
    plt.savefig(figureName, bbox_inches='tight')

    exit()

    # Plot the max-RSS switching figure
    fig2 = plt.figure()
    plotMaxRss(fig2, time, sim, users, rss)
    figureName = os.path.join(resultDir, "maxRss.png")
    plt.savefig(figureName, bbox_inches='tight')

    # For each users plot the radiation pattern at each iterations
    for idx in range(len(rss)):
        fig = plt.figure()
        userIdx = getUserId(sim[idx])
        plotRadiationPattern(fig, drone, users, userIdx, rss, idx)

        figureName = os.path.join(resultDir, "user-" + str(userIdx),
                                  "rss-time-{}.png".format(time[idx]))
        fig.savefig(figureName, bbox_inches='tight')
        plt.close('all')


def args():
    """Handle arguments for the main function."""
    csvPath = docopt(__doc__)['-d']
    resultDir = docopt(__doc__)['-o']
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    return [csvPath, resultDir]


def readData(csvPath):
    with open(csvPath) as f:
        reader = csv.reader(f)

        header = next(reader)
        data = np.array([r for r in reader])

    def columnThatContains(s):
        return [i for i, x in enumerate(header) if s in x]

    def selectAndConvertColumn(col):
        return np.array([map(float, r) for r in data[:, col]])

    # Find the indexes for each categories
    timeCol = header.index('time')
    simCol = header.index('simIdxs')
    droneCol = columnThatContains('drone')
    rssCol = columnThatContains('ant')

    # Split data in each categories
    time = np.array(map(int, data[:, timeCol]))
    sim = data[:, simCol]
    drone = selectAndConvertColumn(droneCol)
    rss = selectAndConvertColumn(rssCol)

    users = []
    for i in range(len(columnThatContains('user-')) / 6):
        thisUserCol = columnThatContains('user-' + str(i))
        users.append(selectAndConvertColumn(thisUserCol))

    return time, sim, drone, users, rss


def getUserId(simId):
    return int(simId.split('-')[0].strip('u'))


def plotFlight(drone, users):

    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals(users)
    plot.plot_flight(drone)

    # Cosmetics
    plt.title("Flight trajectory")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])


def plotRadiationPattern(fig, drone, users, userID, rss, idx):
    # Data manipulation
    droneIdx = drone[idx, :]
    userIdx = users[userID][idx, :]

    rssIdx = np.append(rss[idx, :], rss[idx, 0])
    rssIdx /= max(rssIdx)

    angles = np.linspace(0.0, 2 * np.pi, num=len(rssIdx))

    userAngle = math.atan2(userIdx[1] - droneIdx[1],
                           userIdx[0] - droneIdx[0])

    # Plots
    fig.clear()
    ax1 = fig.add_axes([0, 0, 1, 1], polar=True)

    # Rss
    ax1.plot(angles, rssIdx, 'o-',
             color='gainsboro',
             lw=2.5,
             markersize=4,
             markerfacecolor='cornflowerblue',
             markeredgecolor='cornflowerblue')

    # Drone
    ax1.plot(0, 0, 'kv',
             markersize=10)

    # Terminals
    opt = 'go' if userID == 0 else 'r*'
    ax1.plot(userAngle, max(rssIdx) * 1.2, opt,
             markersize=10)

    # Cosmetic
    ax1.set_ylim(0, 1.3)
    ax1.set_yticks([1])
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')


def plotMaxRss(fig, time, sim, users, rss):

    iterations = np.unique(time)
    maxRss = np.zeros((len(iterations), len(users)))
    minTime = min(time)
    for idx in range(len(time)):
        thisMaxRss_dB = 10 * np.log10(max(rss[idx, :]))
        thisUser = getUserId(sim[idx])
        thisTime = time[idx]

        maxRss[int(thisTime) - minTime, thisUser] = thisMaxRss_dB
    # Plots
    fig.clear()
    for usr in range(len(users)):
        if sum(maxRss[:, usr]) != 0:
            plt.plot(iterations, maxRss[:, usr], 'o-',
                     label='User-{:d}'.format(usr))

    # Cosmetics
    plt.title("Maximum measured Rss")
    plt.xlabel("iterations [/]")
    plt.ylabel("Measured Rss [dB]")
    plt.xticks(np.arange(iterations[0], iterations[-1] + 1, 1.0))
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.legend()


if __name__ == '__main__':
    main(*args())
