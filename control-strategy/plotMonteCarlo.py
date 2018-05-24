#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    monteCarlo.py

Arguments:

Options:
    -h, --help
"""
from myTools import utils
import numpy as np
import os

import pandas as pd
import matplotlib.pyplot as plt
from myTools import plot

MAP_X = 650
MAP_Y = 500
STEP = 10

# N = 1000

INITIAL_CONF = 'job_sample/monteCarlo.json'
d = "50"  # TODO srly ?
OUTPUT_DIR = 'output-' + d
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

COLS = [
    "time", "simIdxs",
    "drone.x", "drone.y", "drone.z", "drone.u", "drone.v", "drone.w",
    "user-0.x", "user-0.y", "user-0.z", "user-0.u", "user-0.v", "user-0.w",
    "user-1.x", "user-1.y", "user-1.z", "user-1.u", "user-1.v", "user-1.w",
    "user-2.x", "user-2.y", "user-2.z", "user-2.u", "user-2.v", "user-2.w",
    "user-3.x", "user-3.y", "user-3.z", "user-3.u", "user-3.v", "user-3.w",
    "user-4.x", "user-4.y", "user-4.z", "user-4.u", "user-4.v", "user-4.w",
    "ant.0", "ant.1", "ant.2", "ant.3"
]

TOP = 10  # %
# {
#     5: -87.10104962147781,  # dBm
#     10: -88.33015679913899,
#     15: -89.29408855807944,
#     20: -90.16465432974937

# }

QUANTILES = [
    -136.95579736244662,
    -124.44278742632754,
    -121.03412865822568,
    -119.0431886177247,
    -117.89259703043294,
    -116.69616602469827,
    -115.61378349900544,
    -114.57228959285314,
    -113.7283014339852,
    -112.8324540028303,
    -112.27990361509165,
    -111.69990702684623,
    -111.23767342699153,
    -110.54103041534684,
    -110.02252320974155,
    -109.61863238196642,
    -109.33620699279469,
    -108.95304217291581,
    -108.67815308227225,
    -108.32055976543167,
    -107.92460583500625,
    -107.6040025352012,
    -107.20358859366752,
    -106.90125731366302,
    -106.52063756606329,
    -106.27941200386617,
    -105.99439949171156,
    -105.59281820530518,
    -105.29461541962971,
    -104.91083107606863,
    -104.55487953844622,
    -104.1723630033643,
    -103.91098651808838,
    -103.5134601805817,
    -103.13341620608978,
    -102.81094231714115,
    -102.5307351485153,
    -102.1663099697152,
    -101.77351628491492,
    -101.46524558352316,
    -101.1549303897893,
    -100.83890969311065,
    -100.51861306722284,
    -100.22239245612045,
    -99.79922176798883,
    -99.43814091610426,
    -98.95709232369492,
    -98.74331168723793,
    -98.3977351604496,
    -98.1530336188637,
    -97.81940426228732,
    -97.44988112723017,
    -97.17886582858324,
    -96.90354912612874,
    -96.618819446097,
    -96.3748717108432,
    -96.04513814998059,
    -95.79461115557456,
    -95.43065790749057,
    -95.08476729004151,
    -94.76573515813413,
    -94.5217155507138,
    -94.19927669185205,
    -93.89131226811075,
    -93.61331456094541,
    -93.37081720738905,
    -93.09247203314003,
    -92.76976594490216,
    -92.54417238845008,
    -92.344917598558,
    -92.05698259925191,
    -91.88875684968505,
    -91.70317473526438,
    -91.46228245161416,
    -91.27420456646783,
    -91.08396496786044,
    -90.86152018888367,
    -90.64714628848114,
    -90.49084740219064,
    -90.3029800416977,
    -90.16465432974937,
    -89.96742609789028,
    -89.81487651407538,
    -89.61880593032858,
    -89.46788106370207,
    -89.29408855807944,
    -89.11708243022083,
    -88.90714368736786,
    -88.72569575172555,
    -88.52500786589823,
    -88.33015679913899,
    -88.10498833868665,
    -87.91340701543885,
    -87.69932698207683,
    -87.38792494945805,
    -87.10104962147781,
    -86.81947757123604,
    -86.35931143317327,
    -85.9639459202106,
    -85.43067543085454,
    -80.55470269361074
]

QUANTILE = QUANTILES[100 - TOP]


def main():

    exp = utils.readJson(INITIAL_CONF)
    simFiles = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)]

    heatmap = np.zeros((MAP_X // STEP, MAP_Y // STEP))

    initRss, finalRss = [], []
    nSucceed = np.zeros(len(QUANTILES))
    N = 0
    for simFile in simFiles:
        N += 1

        df_sim = pd.read_csv(simFile, names=COLS)
        posA = df_sim.iloc[-1]
        posB = df_sim.iloc[-2]
        posC = df_sim.iloc[1]
        posAMinRss = utils.nat2db(float(min(
            posA[['ant.0', 'ant.1', 'ant.2', 'ant.3']]
        )))
        posBMinRss = utils.nat2db(float(min(
            posB[['ant.0', 'ant.1', 'ant.2', 'ant.3']]
        )))
        posCMinRss = utils.nat2db(float(min(
            posC[['ant.0', 'ant.1', 'ant.2', 'ant.3']]
        )))
        for i in range(len(QUANTILES)):
            # if posBMinRss >= QUANTILE or posAMinRss >= QUANTILE:
            if posAMinRss >= QUANTILES[i]:
                nSucceed[i] += 1

        finalRss.append(posAMinRss)
        initRss.append(posCMinRss)

        i = int(float(posA['drone.x']) // STEP)
        j = int(float(posA['drone.y']) // STEP)

        # TODO fix this
        if i == 65:
            i -= 1
        if j == 50:
            j -= 1

        # plt.plot([i*10], [j*10], 'og')

        heatmap[i, j] += 1

    # print("{:.2f}% of simulation endup in top {:d}% positions"
    #       .format(float(nSucceed) / N * 100, TOP))

    # OMG Really ? xD
    # TODO learn meshgrid
    X, Y, Z = [], [], []
    for x in range(0, 650, STEP):
        for y in range(0, 500, STEP):
            i = x // 10
            j = y // 10
            X.append(x)
            Y.append(y)
            Z.append(heatmap[i, j] * 100 / N)

    # Plot
    # Cumulative sum
    plt.figure()
    plotCdfRss(finalRss)
    plotCdfRss(initRss)
    # Cosmetics
    # plt.title("RSS Empirical CDF for d = " + d)
    plt.xlabel("RSS [dBm]")
    plt.ylabel("Percentage [%]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')

    figureName = os.path.join(os.getcwd(), "cdf-" + d + ".png")
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()

    # Cosmetics
    # plt.title("Arrival density - d = " + d + " (" + str(N) + " simulations)")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, 650, 0, 500])

    # Plot map
    plot.plot_scenario(edge='gainsboro', face='whitesmoke')

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
    plot.plot_terminals(exp['terminals'], bsOpt=bsOpt, userOpt=userOpt)

    # Plot heatmap of arrival
    plot.plot_heatmap(
        X, Y, Z,
        np.ones(len(X)) * STEP,
        np.ones(len(X)) * STEP,
        legend="Arrival density [%]"
    )

    figureName = os.path.join(os.getcwd(), "monteCarlo-" + d + ".png")
    plt.savefig(figureName, bbox_inches='tight', dpi=300)
    plt.close()


def plotCdfRss(rss):
    rssCpy = np.sort(rss[:])
    x, y = [], []
    for idx, val in enumerate(rssCpy):
        x.append(val)
        y.append(float(idx) / len(rssCpy) * 100)

    # Plot
    plt.plot(x, y)

    plt.yticks(np.arange(min(x), max(x), 10))
    plt.yticks(np.arange(min(y), max(y), 10))
    plt.xlim((min(x), max(x)))
    plt.ylim((min(y), max(y)))


def args():
    """Handle arguments for the main function."""

    return []


if __name__ == '__main__':
    main(*args())
