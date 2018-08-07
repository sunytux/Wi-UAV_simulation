#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""
Library of multipurposes functions.
"""
import json


def writeJson(jsonFile, data):
    with open(jsonFile, 'w') as f:
        json.dump(data, f)


def readJson(jsonFile):
    with open(jsonFile) as f:
        data = json.load(f)

        return data
