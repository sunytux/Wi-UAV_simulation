#! /usr/bin/python3 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    plotGroundTruth.py -i <INPUT_FILE> -j <INIT_JOB> -o <OUTPUT_DIR>

Arguments:
    -i INPUT_FILE     Data file with simulation results.
    -j INIT_JOB       Initial job that will be copied.
    -o <OUTPUT_DIR>   Output directory.

Options:
    -h, --help
"""
from myTools import plot
from myTools import utils
import math
from docopt import docopt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

STEP = 10


def main(inputFile, initialJobFile, outputDir):

    initJob = utils.readJson(initialJobFile)

    df = pd.read_csv(inputFile, index_col=0)

    df['rss'] = (df[['re', 'im']]
                 .apply(lambda row: getRss(row['re'], row['im']), axis=1))
    df = df.groupby('id').apply(criterion)

    # Ground-truth
    plotGroundTruth(initJob, df)
    plt.gcf().savefig(os.path.join(outputDir, "ground-truth"),
                      bbox_inches='tight', dpi=300)
    plt.close()

    # Weakest-user
    plt.figure()
    plotWeakestUser(initJob, df)
    plt.gcf().savefig(os.path.join(outputDir, "weakest-user"),
                      bbox_inches='tight', dpi=300)
    plt.close()

    # Quantile
    plt.figure()
    X = 10
    plotQuantile(initJob, df, X)
    plt.gcf().savefig(os.path.join(outputDir, "quantile-" + str(X)),
                      bbox_inches='tight', dpi=300)
    plt.close()


def plotQuantile(initJob, df, X):
    quantile = df['rss'].quantile(1 - X / 100)

    # print quantile
    d = {}
    for i in range(0, 101):
        d[i] = df['rss'].quantile(i / 100)
    # print(d)

    minRss = min(df['rss'])

    def isHigherQuantile(row):
        return row['rss'] if row['rss'] >= quantile else minRss

    df['rss_quantile'] = df.apply(isHigherQuantile, axis=1)

    # Figure
    plt.title("Top " + str(X) + " % positions")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot the city
    plot.plot_scenario()

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
    plot.plot_terminals(initJob['terminals'], bsOpt=bsOpt, userOpt=userOpt)

    # Plot the ground-truth
    plot.plot_heatmap(
        df['x'].values,
        df['y'].values,
        df['rss_quantile'].values,
        np.ones(len(df['x'])) * STEP,
        np.ones(len(df['x'])) * STEP,
        legend='RSS [dBm]'
    )


def plotGroundTruth(initJob, df):
    # Figure
    # plt.title("Ground truth")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot the city
    plot.plot_scenario()

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
    plot.plot_terminals(initJob['terminals'], bsOpt=bsOpt, userOpt=userOpt)

    # Plot the ground-truth
    plot.plot_heatmap(
        df['x'].values,
        df['y'].values,
        df['rss'].values,
        np.ones(len(df['x'])) * STEP,
        np.ones(len(df['x'])) * STEP,
        legend='RSS [dBm]'
    )


def plotWeakestUser(initJob, df):
    # Figure
    # plt.title("Weakest user")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot the city
    plot.plot_scenario()

    # Plot terminals
    bsOpt = {
        "marker": "o",
        "markeredgewidth": 1,
        "markersize": 15,
        "color": 'white',
        "markeredgecolor": 'black'
    }
    userOpt = {
        "marker": "*",
        "markeredgewidth": 1,
        "markersize": 20,
        "color": 'white',
        "markeredgecolor": 'black'
    }

    for idx, t in enumerate(initJob['terminals']):
        opt = bsOpt if idx == 0 else userOpt
        color = matplotlib.colors.to_hex(
            plot.CMAP(float(idx) / (len(initJob['terminals']) - 1))
        )
        opt["color"] = color
        # opt["markeredgecolor"] = color
        plot.plot_terminals([t], bsOpt=opt, userOpt={})

    # Plot the weakest-user
    plot.plot_heatmap(
        df['x'].values,
        df['y'].values,
        df['user'].values,
        np.ones(len(df['x'])) * STEP,
        np.ones(len(df['x'])) * STEP,
    )


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


def args():
    """Handle arguments for the main function."""
    inputFile = docopt(__doc__)['-i']
    initialJobFile = docopt(__doc__)['-j']
    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    return [inputFile, initialJobFile, outputDir]


if __name__ == '__main__':
    main(*args())
