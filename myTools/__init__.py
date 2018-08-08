import logging
import datetime

LOGGER = logging.getLogger(__name__)
# LOGGER = logging.getLogger("hello")
thisTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
hdlr = logging.FileHandler('output_' + thisTime + '.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
LOGGER.addHandler(hdlr)
LOGGER.setLevel(logging.DEBUG)
