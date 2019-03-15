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

DEFAULT_CONF = {
    # Setup
    "scenario": "subrealcity.json",
    "drone": {"x": 325, "y": 250, "z": 100, "u": 0, "v": 0, "w": 0},
    "antenna-offsets": [0, 90, 180, 270],
    "terminals": [
        {"x": 55, "y": 77, "z": 76, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 244, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 386, "y": 272, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 536, "y": 144, "z": 1.8, "u": 0, "v": 0, "w": 0},
        {"x": 308, "y": 121, "z": 1.8, "u": 0, "v": 0, "w": 0}
    ],

    # Algorithm options
    "use-database": "/home/sami/docs/phd/projects/04_wireless_UAV_simulator/"\
                    "data/ground-truth/ground-truth-map.csv",
    "routine-algo": "optimize",
    "AoA-algo": "weighted-rss",
    "max-iteration": 12,

    # Output files
    "simulation-output-csv": "/tmp/sim/flight.csv",
    "CloudRT-output-dir": "/tmp/sim/CloudRT",

    # Logs flags
    "matlab-quite-mode": True
}
