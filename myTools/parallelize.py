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


class Job(object):
    """docstring for Job"""
    def __init__(self, path, dirs):
        self.dirs = dirs
        self.status = 'free'
        self.path = path
        self.initPath = path
        self.baseName = os.path.basename(path)
        self.ID = int(self.baseName.strip('.json'))

    def isFree(self):
        return not os.path.exists(os.path.join(self.dirs['ongoing'],
                                               self.baseName))

    def isDone(self):
        return os.path.exists(os.path.join(self.dirs['done'],
                                           self.baseName))

    def remove(self):
        os.remove(self.path)

    def changeStatusTo(self, status):
        if status == 'busy':
            newPath = os.path.join(self.dirs['ongoing'], self.baseName)
        elif status == 'done':
            newPath = os.path.join(self.dirs['done'], self.baseName)
        elif status == "free":
            newPath = self.initPath

        os.rename(self.path, newPath)
        self.status = status
        self.path = newPath

    def getJson(self):
        return utils.readJson(self.path)


class Core(object):
    """docstring for Core"""
    def __init__(self, ID, dirs, initSubFct, subFct):

        self.ID = ID
        self.dirs = dirs
        self.initSubFct = initSubFct
        self.subFct = subFct

        self._newProcess()

    def _processWrapper(self, procID, dirs, initSubFct, subFct):
        LOGGER.info("Starting process %d", procID)

        job = nextJob(dirs)
        if job is not False:
            context = initSubFct()

            while job is not False and self.isAvailable():

                LOGGER.debug("Start of job %d on process %d", job.ID, procID)
                startTime = time.time()

                subFct(job.getJson(), *context)

                job.changeStatusTo('done')

                LOGGER.debug("End of job %d on process %d in %d s", job.ID,
                             procID, int(time.time() - startTime))

                job = nextJob(dirs)

        LOGGER.info("End of process %d", procID)
        if str(procID) in os.listdir(dirs['proc']):
            os.remove(os.path.join(dirs['proc'], str(procID)))

    def _newProcess(self):
        self.process = Process(
            target=self._processWrapper,
            args=(self.ID, self.dirs, self.initSubFct, self.subFct)
        )

    def isAvailable(self):
        return str(self.ID) in os.listdir(self.dirs['proc'])

    def isRunning(self):
        return self.process.is_alive()

    def makeAvailable(self):
        open(os.path.join(self.dirs['proc'], str(self.ID)), 'w').close()

    def start(self):
        if self.process.is_alive():
            self.process.start()
        else:
            self._newProcess()
            self.process.start()


def nextJob(dirs):
    chosenJob = False

    # This run through all files included inside the input directory starting
    # with the one inside a subdirectory.
    for inputDir, d, jobs in list(os.walk(dirs['in']))[-1::-1]:
        if len(jobs) > 0:
            thisJob = random.choice(jobs)
            thisJob = Job(os.path.join(inputDir, thisJob), dirs)

            if thisJob.isFree() and not thisJob.isDone():
                thisJob.changeStatusTo("busy")
                chosenJob = thisJob
                break

            else:
                try:
                    thisJob.remove()
                except OSError:
                    pass
                chosenJob = nextJob(dirs)
                break

    return chosenJob


def jobLeft(dirs):
    n = 0
    for r, d, files in os.walk(dirs['in']):
        n += len(files)

    return n


def ongoingJobs(dirs):
    return len(os.listdir(dirs['ongoingJobs']))


def availableCores(dirs):
    return len(os.listdir(dirs['proc']))


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

    cores = [Core(i, dirs, initSubFct, subFct) for i in range(20)]
    for core in cores[:nbCore]:
        core.makeAvailable()

    while jobLeft(dirs) + ongoingJobs(dirs) >= 0 and availableCores(dirs) > 0:
        time.sleep(3)
        for core in cores:
            if core.isAvailable() and not core.isRunning():
                core.start()

    if jobLeft(dirs) == 0:
        LOGGER.info('End of simulation: no more jobs')
    elif len(os.listdir(dirs['proc'])) == 0:
        LOGGER.info('End of simulation: no core available')
