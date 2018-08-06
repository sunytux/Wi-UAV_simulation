#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Start multiple instances of a given code.

"""
import logging
import json
import os
import random
from multiprocessing import Process
import time


LOGGER = logging.getLogger(__name__)


def processWrapper(procID, dirs, initSubFct, subFct):
    LOGGER.info("Starting process %d", procID)

    job = nextJob(dirs)
    if job is not False:
        context = initSubFct()

        while job is not False:
            LOGGER.debug("Start of job %d on process %d", job["ID"], procID)
            startTime = time.time()

            subFct(job, *context)

            jobProcessPath = os.path.join(dirs['ongoing'], job['file'])
            jobDonePath = os.path.join(dirs['done'], job['file'])
            os.rename(jobProcessPath, jobDonePath)

            LOGGER.debug("End of job %d on process %d in %d s", job["ID"],
                         procID, int(time.time() - startTime))

            job = nextJob(dirs)

    LOGGER.info("End of process %d", procID)


def nextJob(dirs):
    jobBaseName = findNextJob(dirs)

    if jobBaseName is not False:
        jobInputPath = os.path.join(dirs['in'], jobBaseName)
        jobProcessPath = os.path.join(dirs['ongoing'], jobBaseName)

        os.rename(jobInputPath, jobProcessPath)
        job = readJson(jobProcessPath)
        job['file'] = jobBaseName
    else:
        job = False

    return job


def findNextJob(dirs):
    inputDirContent = os.listdir(dirs['in'])

    if len(inputDirContent) > 0:
        nextJob = random.choice(inputDirContent)
        isBeingProcessed = nextJob in os.listdir(dirs['ongoing'])
        isAlreadyDone = nextJob in os.listdir(dirs['out'])
        if isBeingProcessed or isAlreadyDone:
            nextJob = findNextJob(dirs)
    else:
        nextJob = False

    return nextJob


def readJson(jsonFile):
    with open(jsonFile) as f:
        data = json.load(f)

        return data


def parallelize(inDir, outDir, nbCore, initSubFct, subFct):

    dirs = {
        "in": inDir,
        "out": outDir,
        "ongoing": os.path.join(outDir, "ongoingJobs"),
        "done": os.path.join(outDir, "doneJobs"),
    }

    processes = []
    for i in range(nbCore):
        thisProcess = Process(
            target=processWrapper,
            args=(i, dirs, initSubFct, subFct)
        )
        thisProcess.start()
        processes.append(thisProcess)
