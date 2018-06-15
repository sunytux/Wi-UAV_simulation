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
import matplotlib.pyplot as plt


def main():
    f = csv.reader(open("flight.log", 'r'))

    plt.title("Flight")

    i = 0
    for row in f:
        i += 1
        c = '#' + ''.join('{:02X}'.format(a) for a in [i * 255 / 15] * 3)
        plt.plot(row[0], row[1], 'v', markersize=10, markerfacecolor=c,
                 markeredgecolor=c,)
        plt.plot(row[2], row[3], 'r*', markersize=10)
        plt.plot(row[4], row[5], 'go', markersize=10)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis('equal')

    plt.show()


if __name__ == '__main__':
    main()
