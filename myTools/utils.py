#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""
Library of multi-purposes functions.
"""
import json
import shutil
import zipfile
import os
import math
from functools import wraps


def writeJson(jsonFile, data):
    with open(jsonFile, 'w') as f:
        json.dump(data, f)


def readJson(jsonFile):
    with open(jsonFile) as f:
        data = json.load(f)

        return data


def extractZip(zipFile, inFile, outFile):

    with zipfile.ZipFile(zipFile) as z:
        with z.open(inFile) as zf, open(outFile, 'wb') as f:
            shutil.copyfileobj(zf, f)

    return outFile


def askErase(file):
    if os.path.isfile(file):
        i = raw_input("\"" + file + "\" already exist. Erase ?[y/n] ")
        if i == "y":
            os.remove(file)
        else:
            exit()


def getSnapshotName(idx, user, ant):
    return '{:s}_snapshot_1.mat'.format(tuple2simid(idx, user, ant))


def tuple2simid(idx, user, ant):
    return 'u{:02d}-t{:06d}-ant{:02d}'.format(user, idx, ant)


def simid2tuple(simId):
    user = int(simId[1:3])
    idx = int(simId[5:11])
    ant = int(simId[15:17])

    return (idx, user, ant)


def getIdxFromPosition(x, y):
    """TODO

    /!| this is dependent of the map !
    """
    step = 10
    i = x // step
    j = y // step
    return 50 * i + j + 1


def nat2db(x):
    return 10 * math.log10(x)


def getRss(re, im):

    # TODO result shouldn't be 0.0 redo exp t002968 and t002969
    if re + im == 0:
        re, im = 1e-6, 1e-6

    # return math.pow(re, 2.0) + math.pow(im, 2.0)
    return 10 * math.log10(math.pow(re, 2.0) + math.pow(im, 2.0))


def realAngle(alpha, deg=False):
    if deg:
        pi = 180
    else:
        pi = math.pi

    alpha %= 2 * pi
    if alpha > pi:
        alpha = -pi + (alpha % pi)
    elif alpha < -pi:
        alpha = pi - (alpha % pi)

    return alpha


def add_method(cls):
    """Dynamically Add a Method to a Class [1]

    [1] See: https://medium.com/@mgarod/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does
        # exactly the same as func
        return func

    return decorator
