#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot and save figures of flight logs superposed on ground truth heat map.

Usage:
    plotFlightWithGroundTruth.py -d <FLIGHT_LOG> -o DIR

Arguments:
    -d <FLIGHT_LOG>  Path to flight logs.
    -o DIR           Output directory.

Options:
    -h, --help
"""
import csv
import math
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from docopt import docopt
import os
from myTools import plot
import pandas as pd


DB_FILE = "/home/sami/docs/phd/projects/04_wi-uav_simulation/data/ground-truth/ground-truth-map.csv"
STEP = 10


def main(csvPath, resultDir):
    time, sim, drone, users, rss = readData(csvPath)

    df = pd.read_csv(DB_FILE, index_col=0)

    df['rss'] = (df[['re', 'im']]
                 .apply(lambda row: getRss(row['re'], row['im']), axis=1))
    df = df.groupby('id').apply(criterion)

    # Cosmetics
    # plt.title("Flight trajectory")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot
    plot.plot_scenario()

    plot.plot_flight(
        drone,
        insideOpt={
            "color": "black",
            "markerfacecolor": 'black',
            "markeredgecolor": 'black'
        }
    )

    # Plot terminals
    bsOpt = {
        "markeredgewidth": 2,
        "markersize": 15,
        "color": 'white',
        "markeredgecolor": 'black'
    }
    userOpt = {
        "markeredgewidth": 2,
        "markersize": 20,
        "color": 'white',
        "markeredgecolor": 'black'
    }
    plot.plot_terminals(users, bsOpt=bsOpt, userOpt=userOpt)

    # Plot the ground-truth
    plot.plot_heatmap(
        df['x'].values,
        df['y'].values,
        df['rss'].values,
        np.ones(len(df['x'])) * STEP,
        np.ones(len(df['x'])) * STEP,
        legend='RSS [dBm]'
    )

    figureName = os.path.join(resultDir, "flight.png")
    plt.savefig(figureName, bbox_inches='tight', dpi=300)


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


def criterion(rows):
    """Select the antenna with the weakest RSS.

       rows is every antenna simulations for a specific location
       Return the antenna with the weakest RSS (single row)
    """

    def getMaxRss(user):
        idxMaxRss = user['rss'].idxmax()
        return user.loc[idxMaxRss]

    rows = rows.groupby('user').apply(getMaxRss)

    idxMinRss = rows['rss'].idxmin()

    return rows.loc[idxMinRss]


def getRss(re, im):

    # TODO result shouldn't be 0.0 redo exp t002968 and t002969
    if re + im == 0:
        re, im = 1e-6, 1e-6

    # return math.pow(re, 2.0) + math.pow(im, 2.0)
    return 10 * math.log10(math.pow(re, 2.0) + math.pow(im, 2.0))


if __name__ == '__main__':
    main(*args())
