#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot rays

Usage:
    plotRays.py -i <INPUT_FILE>
    plotRays.py --from-db -i <INPUT_FILE>
    plotRays.py --from-db -x <X> -y <Y> -u <USR> -a <ANT>

Arguments:
    -i <INPUT_FILE> Either a post-processed csv file or a CloudRT mat file.
    --form-db       Use the database.
    -x <X>          Drone x position.
    -y <Y>          Drone y position.
    -u <USR>        User id.
    -a <ANT>        Antenna id.

Options:
    -h, --help
"""
from docopt import docopt
import pandas as pd
import matplotlib.pyplot as plt
from myTools import plot
from myTools import utils
import extractRays


def main(inputFile, useDB, extra):
    if useDB:
        if not inputFile:
            idx = utils.getIdxFromPosition(extra["x"], extra["y"])
            inputFile = utils.getSnapshotName(idx, extra["user"], extra["ant"])
        raysCsv = extractRays.toCsv(inputFile, useDB=True)
    elif inputFile.split('.')[-1].lower() == 'mat':
        raysCsv = extractRays.toCsv(inputFile)
    else:
        raysCsv = inputFile

    df = pd.read_csv(raysCsv, index_col=0)

    def getRss(row):
        return utils.getRss(row['E_re'], row['E_im'])
    df['rss'] = (df[['E_re', 'E_im']].apply(getRss, axis=1))

    plot3d(df)

    plt.show()


def plot3d(df):
    plot.plot3_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot3_rays(df)
    plt.plot(
        [df['tx.x'].iloc[0]], [df['tx.y'].iloc[0]], [df['tx.z'].iloc[0]],
        marker="*",
        markeredgewidth=1,
        markersize=10,
        color='red',
        markeredgecolor='red',
        zorder=2000,
    )
    plt.plot(
        [df['rx.x'].iloc[0]], [df['rx.y'].iloc[0]], [df['rx.z'].iloc[0]], 'kv',
        markersize=10,
        mew=4,
        zorder=2000,
    )


def args():
    """Handle arguments for the main function."""
    useDB = docopt(__doc__)['--from-db']
    inputFile = docopt(__doc__)['-i']
    extra = {
        "x": int(docopt(__doc__)['-x']) if docopt(__doc__)['-x'] else False,
        "y": int(docopt(__doc__)['-y']) if docopt(__doc__)['-y'] else False,
        "user": int(docopt(__doc__)['-u']) if docopt(__doc__)['-u'] else False,
        "ant": int(docopt(__doc__)['-a']) if docopt(__doc__)['-a'] else False
    }
    return [inputFile, useDB, extra]


def plotConfiguration():
    terminals = [
        {"x": 55, "y": 77, "z": 76, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 244, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 386, "y": 272, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 144, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 308, "y": 121, "z": 1.8, "u": 0, "v": 0, "w": 0}
    ]

    # Plot
    plt.gca().set_aspect('equal')
    plot.plot3_scenario(edge='gray', face='whitesmoke')
    plt.plot(
        [200], [400], [100], 'kv',
        color="cornflowerblue",
        markersize=20,
        mew=4,
        zorder=2000,
    )
    optUser = {
        "marker": "*",
        "markeredgewidth": 1,
        "markersize": 20,
        "color": 'red',
        "markeredgecolor": 'red',
        "zorder": 2000,
    }
    optBs = {
        "marker": "o",
        "markeredgewidth": 1,
        "markersize": 20,
        "color": 'green',
        "markeredgecolor": 'green',
        "zorder": 2000,
    }

    for idx, t in enumerate(terminals):
        opt = optUser if idx >= 1 else optBs
        plt.plot([t['x']], [t['y']], [t['z']], **opt)

    plt.show()


if __name__ == '__main__':
    main(*args())
    # plotConfiguration()
