#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Extract rays from snapshot to csv

This script include the matlab script `extractRays.m`

Usage:
    extractRays.py -i <SNAPSHOT> [-o <CSV>]
    extractRays.py --from-db -i <SNAPSHOT> [-o <CSV>]


Arguments:
    -i <SNAPSHOT>  CloudRT Snapshot file.
    --form-db      Use the database.

Options:
    # -o <CSV>       Output csv [default: /tmp/rays.csv].
    -h, --help
"""
import matlab.engine
import pandas as pd
from docopt import docopt
import os
from myTools import utils
import tempfile


DB = '/home/sami/docs/phd/projects/04_wireless_UAV_simulator/data/ground-truth/ground-truth-results.zip'
COLS = ['id', 'user', 'ant',
        'tx.x', 'tx.y', 'tx.z',
        'rx.x', 'rx.y', 'rx.z',
        'type', 'refOrder',
        'ref1.x', 'ref1.y', 'ref1.z',
        'ref2.x', 'ref2.y', 'ref2.z',
        'E_re', 'E_im', 'aoa', 'eoa', 'aod', 'eod']

TEMP_UNZIP_DIR = os.path.join(
    tempfile.gettempdir(),
    'rays',
    'unzip-and-raw'
)
TEMP_DB_DIR = os.path.join(
    tempfile.gettempdir(),
    'rays',
    'db'
)
TEMP_OTHER_DIR = os.path.join(
    tempfile.gettempdir(),
    'rays',
    'other'
)

for d in [TEMP_UNZIP_DIR, TEMP_DB_DIR, TEMP_OTHER_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)


def extractRays(eng, snapFile):
    temporaryCsvFile = tempfile.NamedTemporaryFile(
        prefix=TEMP_UNZIP_DIR,
        suffix='.csv'
    ).name

    eng.extractRays(snapFile, temporaryCsvFile, nargout=0)

    return temporaryCsvFile


def toCsv(matFile,
          # csvFile=tempfile.NamedTemporaryFile(suffix='.csv').name,
          useDB=False):
    # csvFile = tempfile.NamedTemporaryFile(suffix='.csv').name
    baseName = os.path.splitext(os.path.basename(matFile))[0]
    csvFile = os.path.join(TEMP_OTHER_DIR, baseName + '.csv')

    if useDB:
        csvFile = os.path.join(
            TEMP_DB_DIR,
            os.path.basename(matFile) + ".csv"
        )

        if alreadyExtractedFromDB(csvFile):
            return csvFile
        else:
            matFile = extractMatFromDB(matFile)

    elif alreadyExtracted(csvFile):
            return csvFile

    eng = matlab.engine.start_matlab()
    eng.extractRays(matFile, csvFile, nargout=0)

    df = pd.read_csv(csvFile, names=COLS)
    df.to_csv(csvFile)

    return csvFile


def extractMatFromDB(snapName):
    snapInsideZip = os.path.join('output', 'result', snapName)
    snapOutsideZip = os.path.join(TEMP_UNZIP_DIR, snapName)

    snapFile = utils.extractZip(DB, snapInsideZip, snapOutsideZip)

    return snapFile


def alreadyExtractedFromDB(csvFile):
    return os.path.isfile(os.path.join(TEMP_DB_DIR, csvFile))


def alreadyExtracted(csvFile):
    return os.path.isfile(os.path.join(TEMP_OTHER_DIR, csvFile))


def args():
    """Handle arguments for the main function."""

    useDB = docopt(__doc__)['--from-db']
    snapFile = docopt(__doc__)['-i']
    # csvFile = docopt(__doc__)['-o']
    # utils.askErase(csvFile)

    return [snapFile, useDB]


if __name__ == '__main__':
    toCsv(*args())
