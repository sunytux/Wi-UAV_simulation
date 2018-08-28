#! /usr/bin/python3 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    plotGroundTruth.py

Arguments:

Options:
    -h, --help
"""
from myTools import plot

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_FILE = "/home/sami/docs/phd/projects/04_wireless_UAV_simulator/data/" \
            "ground-truth_firstJobs/ground-truth-map.csv"

STEP = 10


def main():

    df = pd.read_csv(DATA_FILE, index_col=0)
    df['rss'] = (df[['re', 'im']]
                 .apply(lambda row: getRss(row['re'], row['im']), axis=1))
    df = df.groupby('id').apply(criterion)

    plot.plot_scenario()
    plot.plot_heatmap(df['x'].values,
                      df['y'].values,
                      df['rss'].values,
                      np.ones(len(df['x'])) * STEP,
                      np.ones(len(df['x'])) * STEP)

    plt.title("Ground truth")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')

    plt.show()


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
    return math.pow(re, 2.0) + math.pow(im, 2.0)


if __name__ == '__main__':
    main()
