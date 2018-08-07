#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Start multiple instances of a given code.

"""
import logging
import os
import random
from multiprocessing import Process
import time
import utils

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
    priorDir = os.path.join(dirs['in'], "prior")

    listOfJobs = [os.path.join(dirs['in'], d) for d in os.listdir(dirs['in']) if d != "prior"]

    if os.path.isdir(priorDir) and len(os.listdir(priorDir)) > 0:
        listOfJobs = [os.path.join(priorDir, d) for d in os.listdir(priorDir)]

    if len(listOfJobs) == 0:
        return False

    nextJob = random.choice(listOfJobs)
    nextJobBasename = os.path.basename(nextJob)

    isBeingProcessed = nextJobBasename in os.listdir(dirs['ongoing'])
    isAlreadyDone = nextJobBasename in os.listdir(dirs['out'])

    if isBeingProcessed or isAlreadyDone:
        os.remove(nextJob)
        nextJob = findNextJob(dirs)
    else:
        nextJobProcessPath = os.path.join(dirs['ongoing'], nextJobBasename)
        os.rename(nextJob, nextJobProcessPath)
        nextJob = utils.readJson(nextJobProcessPath)
        nextJob['file'] = nextJobBasename

    return nextJob


def nextJob2(dirs):
    jobBaseName = findNextJob(dirs)

    if jobBaseName is not False:
        jobInputPath = os.path.join(dirs['in'], jobBaseName)
        jobProcessPath = os.path.join(dirs['ongoing'], jobBaseName)

        os.rename(jobInputPath, jobProcessPath)
        job = utils.readJson(jobProcessPath)
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
            os.remove(os.path.join(inputDirContent, nextJob))
            nextJob = findNextJob(dirs)

    else:
        nextJob = False

    return nextJob


def parallelize(inDir, outDir, nbCore, initSubFct, subFct):

    dirs = {
        "in": inDir,
        "out": outDir,
        "ongoing": os.path.join(outDir, "ongoingJobs"),
        "done": os.path.join(outDir, "doneJobs"),
    }
    for _, thisDir in dirs.items():
        if not os.path.exists(thisDir):
            print(thisDir)
            os.makedirs(thisDir)

    processes = []
    for i in range(nbCore):
        thisProcess = Process(
            target=processWrapper,
            args=(i, dirs, initSubFct, subFct)
        )
        thisProcess.start()
        processes.append(thisProcess)
