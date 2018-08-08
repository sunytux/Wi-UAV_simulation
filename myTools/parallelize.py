#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Start multiple instances of a given code.

"""
import os
import random
from multiprocessing import Process
import time
import utils

from myTools import LOGGER

# LOGGER = logging.getLogger(__name__)


def processWrapper(procID, dirs, initSubFct, subFct):
    LOGGER.info("Starting process %d", procID)

    job = nextJob(dirs)
    if job is not False:
        context = initSubFct()

        while job is not False and str(procID) in os.listdir(dirs['proc']):
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
    if str(procID) in os.listdir(dirs['proc']):
        os.remove(os.path.join(dirs['proc'], str(procID)))


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
        nextJob = nextJob(dirs)
    else:
        nextJobProcessPath = os.path.join(dirs['ongoing'], nextJobBasename)
        os.rename(nextJob, nextJobProcessPath)
        nextJob = utils.readJson(nextJobProcessPath)
        nextJob['file'] = nextJobBasename

    return nextJob


def parallelize(inDir, outDir, nbCore, initSubFct, subFct):

    dirs = {
        "in": inDir,
        "out": outDir,
        "proc": os.path.join(outDir, "proc"),
        "ongoing": os.path.join(outDir, "ongoingJobs"),
        "done": os.path.join(outDir, "doneJobs"),
    }
    for _, thisDir in dirs.items():
        if not os.path.exists(thisDir):
            os.makedirs(thisDir)

    processes = []
    for i in range(nbCore):
        open(os.path.join(dirs['proc'], str(i)), 'w').close()
        thisProcess = Process(
            target=processWrapper,
            args=(i, dirs, initSubFct, subFct)
        )
        thisProcess.start()
        processes.append(thisProcess)

    while nextJob(dirs) is not False and len(os.listdir(dirs['proc'])) > 0:
        time.sleep(3)
        for thisProcId in range(len(processes)):
            isFilePresent = str(thisProcId) in os.listdir(dirs['proc'])

            if isFilePresent and not processes[thisProcId].is_alive():
                processes[thisProcId] = Process(
                    target=processWrapper,
                    args=(thisProcId, dirs, initSubFct, subFct)
                )
                processes[thisProcId].start()
