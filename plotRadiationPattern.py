#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""TODO

Usage:
    plotFlight.py

Arguments:

Options:
    -h, --help
"""
import csv
import math
import matplotlib.pyplot as plt
import numpy as np


def main():
    f = csv.reader(open("flight.log", 'r'))

    step = 0
    for row in f:
        step += 1

        rss = np.array([abs(float(r)) for r in row[6:]])
        rss -= max(rss)
        rss = np.array([math.pow(10.0, i / 10.0) for i in rss])

        rss = map(float, row[6:])
        rss.append(rss[0])  # for plotting purposes 
        rss = np.array(rss) / max(rss)

        drone = map(float, row[:2])
        user = map(float, row[2:4])
        bs = map(float, row[4:6])

        # TODO this is not correct angles are not set like this !
        angles = np.linspace(0.0, 2 * np.pi, num=len(rss))

        userAngle = math.atan2(user[1] - drone[1], user[0] - drone[0])
        bsAngle = math.atan2(bs[1] - drone[1], bs[0] - drone[0])

        fig1 = plt.figure()
        ax1 = fig1.add_axes([0, 0, 1, 1], polar=True)
        # ax1.set_ylim(0, 1.3)
        # ax1.set_yticks([1])

        ax1.plot(angles, rss, lw=2.5)
        ax1.plot(0, 0, 'kv', markersize=10)
        ax1.plot(userAngle, max(rss) * 1.2, 'r*', markersize=10)
        ax1.plot(bsAngle, max(rss) * 1.2, 'go', markersize=10)
        # plt.show()

        fig1.savefig("png/flight-{}.png".format(step), bbox_inches='tight')
        plt.close('all')


if __name__ == '__main__':
    main()
