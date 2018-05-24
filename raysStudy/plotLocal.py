#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot rays

    Use DB.

Usage:
    plotRays.py -i <INPUT_DIR> [-o <OUTPUT_DIR>]
    plotRays.py --from-db -x <X> -y <Y> -u <USR> [-o <OUTPUT_DIR>]

Arguments:
    -i <INPUT_DIR>   Directory of CloudRT mat files.
    --form-db        Use the database.
    -x <X>           Drone x position.
    -y <Y>           Drone y position.
    -u <USR>         User id.
    -a <ANT>         Antenna id.

Options:
    -o <OUTPUT_DIR>  Output directory [default: /tmp/local-rays].
    -h, --help
"""
from docopt import docopt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from myTools import plot
from myTools import utils
import extractRays
import os

ANTENNA_IDXS = [0, 2, 4, 6]
ANTENNA_OFFSET = [0, 45, 90, 135, 180, 225, 270, 335]
ANTENNA_IDXS = [0, 1, 2, 3, 4, 5, 6, 7]


def main(df, x, y, user, outputDir):

    def getRss(row):
        return utils.getRss(row['E_re'], row['E_im'])
    df['rss'] = (df[['E_re', 'E_im']].apply(getRss, axis=1))

    # Azimuth angle of arrival
    plt.figure()
    plotAoaRss(df, x, y, user)
    figureName = os.path.join(
        outputDir,
        "x{:d}-y{:d}-u{:d}_AOA.png".format(x, y, user)
    )
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # Elevation angle of arrival
    plt.figure()
    plotEoaRss(df, x, y, user)
    figureName = os.path.join(
        outputDir,
        "x{:d}-y{:d}-u{:d}_EOA.png".format(x, y, user)
    )
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # Configuration
    plt.figure()
    plotConfiguration(x, y, df)
    figureName = os.path.join(
        outputDir,
        "x{:d}-y{:d}-u{:d}_conf.png".format(x, y, user)
    )
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # AoA same graph
    plt.figure()
    plotAoASameGraph(df, x, y, user)
    figureName = os.path.join(
        outputDir,
        "x{:d}-y{:d}-u{:d}_AOA-same-graph.png".format(x, y, user)
    )
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # Plot rays
    plt.figure()
    plotRays(df, x, y, user, 0)
    figureName = os.path.join(
        outputDir,
        "x{:d}-y{:d}-u{:d}_rays.png".format(x, y, user)
    )
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # Plot ray on antenna
    for ant in ANTENNA_IDXS:
        df_a = df[df['ant'] == ant]
        plt.figure()
        plotRaysOnAntenna(df_a, x, y, user, ant)
        figureName = os.path.join(
            outputDir,
            "x{:d}-y{:d}-u{:d}_rays-on-ant{:d}.png".format(x, y, user, ant)
        )
        plt.savefig(figureName, bbox_inches='tight', dpi=300)
        plt.close()


def plotRaysOnAntenna(df, x, y, user, ant):
    plot.plot3_antennaPattern()
    for index, row in df.iterrows():
        az = row['aoa']
        el = row['eoa']

        r2p = 5
        x2p = [0, r2p * np.sin(az) * np.cos(el)]
        y2p = [0, r2p * np.sin(az) * np.sin(el)]
        z2p = [0, r2p * np.cos(az)]
        plt.plot(x2p, y2p, z2p)


def plotRays(df, x, y, user, ant):
    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_flight(np.array([[x, y]]))
    plot.plot_rays(df)
    plot.plot_terminals([np.array(df[['tx.x', 'tx.y', 'tx.z']][:])])

    # Cosmetics
    plt.title("Rays")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])


def plotConfiguration(x, y, df):

    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals([np.array(df[['tx.x', 'tx.y', 'tx.z']][:])])
    plot.plot_flight(np.array([[x, y]]))

    # Cosmetics
    plt.title("Configuration")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])


def plotAoASameGraph(df, x, y, user):
    for ant in ANTENNA_IDXS:
        df_a = df[df['ant'] == ant]

        def addOffset(cell):
            return utils.realAngle(cell - ANTENNA_OFFSET[ant], deg=True)
        df_a['aoa_abs'] = df_a['aoa'].map(addOffset)

        plt.plot(df_a['aoa_abs'], df_a['rss'], 'o',
                 label="Ant: ${:d}^\circ$".format(ANTENNA_OFFSET[ant]),
                 markersize=1)

        # Cosmetics
        plt.title("RSS against Azimuth of Arrival\n"
                  "Drone = ({:d}, {:d}) - User = {:d}".format(x, y, user))
        plt.xlabel("Absolute Azimuth of Arrival [$^\circ$]")
        plt.ylabel("RSS [dBm]")
        lgnd = plt.legend()
        for legend_handle in lgnd.legendHandles:
            legend_handle._legmarker.set_markersize(9)


def plotAoaRss(df, x, y, user):

    fig, axs = \
        plt.subplots(int(len(ANTENNA_IDXS) / 2), 2, sharex=True, sharey=True)

    for ant, ax in zip(ANTENNA_IDXS, [ax for row in axs for ax in row]):
        df_a = df[df['ant'] == ant]

        ax.plot(df_a['aoa'], df_a['rss'], 'o', markersize=1)

        # Cosmetic
        ax.set_title("Antenna: ${:d}^\circ$".format(ANTENNA_OFFSET[ant]))
        ax.grid(linestyle=':', linewidth=1, color='gainsboro')
        xticks = list(range(-180, 270, 90))
        plt.setp(ax, xticks=xticks, xticklabels=xticks)
        ax.set_xlim([-200, 200])

    # Cosmetics
    title = "Drone = ({:d}, {:d}) - User = {:d}".format(x, y, user)
    xLabel = "Azimuth of Arrival relative to antenna [$^\circ$]"
    yLabel = "RSS [dBm]"
    fig.suptitle(title)
    fig.subplots_adjust(top=0.8, hspace=0.5)
    fig.text(0.5, 0.02, xLabel, ha='center')
    fig.text(0.02, 0.5, yLabel, va='center', rotation='vertical')


def plotEoaRss(df, x, y, user):

    fig, axs = \
        plt.subplots(int(len(ANTENNA_IDXS) / 2), 2, sharex=True, sharey=True)

    for ant, ax in zip(ANTENNA_IDXS, [ax for row in axs for ax in row]):
        df_a = df[df['ant'] == ant]

        ax.plot(df_a['eoa'], df_a['rss'], 'o', markersize=1)

        # Cosmetic
        ax.set_title("Antenna: ${:d}^\circ$".format(ANTENNA_OFFSET[ant]))
        ax.grid(linestyle=':', linewidth=1, color='gainsboro')
        xticks = list(range(-180, 270, 90))
        plt.setp(ax, xticks=xticks, xticklabels=xticks)
        ax.set_xlim([-200, 200])

    # Cosmetics
    title = "Drone = ({:d}, {:d}) - User = {:d}".format(x, y, user)
    xLabel = "Elevation of Arrival relative to antenna [$^\circ$]"
    yLabel = "RSS [dBm]"
    fig.suptitle(title)
    fig.subplots_adjust(top=0.8, hspace=0.5)
    fig.text(0.5, 0.02, xLabel, ha='center')
    fig.text(0.02, 0.5, yLabel, va='center', rotation='vertical')


def loadRaysFromDB(idx, user):
    df = pd.DataFrame()
    for ant in ANTENNA_IDXS:
        raysCsv = extractRays.toCsv(
            utils.getSnapshotName(idx, user, ant),
            useDB=True
        )
        df_a = pd.read_csv(raysCsv, index_col=0)

        df = pd.concat([df, df_a])

    return df


def loadRaysFromDir(directory):
    df = pd.DataFrame()
    # for ant in ANTENNA_IDXS:
    for matFile in os.listdir(directory):
        raysCsv = extractRays.toCsv(
            os.path.join(directory, matFile),
            useDB=False
        )
        df_a = pd.read_csv(raysCsv, index_col=0)

        df = pd.concat([df, df_a])

    return df


def args():
    """Handle arguments for the main function."""
    if docopt(__doc__)['--from-db']:
        x = int(docopt(__doc__)['-x'])
        y = int(docopt(__doc__)['-y'])
        user = int(docopt(__doc__)['-u'])

        idx = utils.getIdxFromPosition(x, y)
        df = loadRaysFromDB(idx, user)
    else:
        inputDir = docopt(__doc__)['-i']
        df = loadRaysFromDir(inputDir)

        x = df['rx.x'].iloc[0]
        y = df['rx.y'].iloc[0]
        user = df['user'].iloc[0]

    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    return [df, x, y, user, outputDir]


if __name__ == '__main__':
    main(*args())
