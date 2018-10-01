#! /usr/bin/python3 -u
# -*- coding: utf-8 -*-

"""Ground Truth

Usage:
    plotGroundTruth.py -i <INPUT_FILE> -j <INIT_JOB> -o <OUTPUT_FILE>

Arguments:
    -i INPUT_FILE     Data file with simulation results.
    -j INIT_JOB       Initial job that will be copied.
    -o <OUTPUT_FILE>  Output file.

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

STEP = 10


def main(inputDir, initialJobFile, outputFile):

    initJob = utils.readJson(initialJobFile)

    df = pd.read_csv(inputDir, index_col=0)

    df['rss'] = (df[['re', 'im']]
                 .apply(lambda row: getRss(row['re'], row['im']), axis=1))
    df = df.groupby('id').apply(criterion)

    # Figure
    plt.title("Ground truth")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot the city
    plot.plot_scenario()

    # Plot terminals
    plot.plot_terminals(initJob['terminals'])

    # Plot the heatmap
    plot.plot_heatmap(df['x'].values,
                      df['y'].values,
                      df['rss'].values,
                      np.ones(len(df['x'])) * STEP,
                      np.ones(len(df['x'])) * STEP,
                      legend='RSS (dB)')

    plt.gcf().savefig(outputFile, bbox_inches='tight')


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
    inputDir = docopt(__doc__)['-i']
    initialJobFile = docopt(__doc__)['-j']
    outputFile = docopt(__doc__)['-o']

    return [inputDir, initialJobFile, outputFile]


if __name__ == '__main__':
    main(*args())
