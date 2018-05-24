import logging
import datetime
import os

LOGGER = logging.getLogger(__name__)
# LOGGER = logging.getLogger("hello")
thisTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logFile = os.path.join(os.getenv("HOME"), 'output_' + thisTime + '.log')
hdlr = logging.FileHandler(logFile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
LOGGER.addHandler(hdlr)
LOGGER.setLevel(logging.DEBUG)
