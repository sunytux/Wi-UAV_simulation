#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Simulate the 2nd block of the localisation process

Here an Unscented Kalman Filter (UKF) is implemented to help minimize
uncertainty in the localization process.

Usage:
    simBlock2.py -o DIR

Arguments:
    -o DIR          Output directory.

Options:
    -h, --help
"""
import ukflib

from myTools import plot
from myTools import DEFAULT_CONF
from myTools.simulator import *
from myTools import utils

from docopt import docopt
import matplotlib.pyplot as plt
import matplotlib.cm as cm


USER = 4
TX_GUESS_X, TX_GUESS_Y = 300, 250  # 300, 200

TRAJECTORY = "square"
TRAJECTORY_STEP = 10
# TOP, BOTTOM, LEFT, RIGHT = 450, 50, 400, 500
TOP, BOTTOM, LEFT, RIGHT = 470, 30, 30, 620

# RN = np.deg2rad(27.011)
RN = np.deg2rad(57)
RV = 10  # 0.5


EXP = DEFAULT_CONF
EXP.update({
    "drone": {"x": LEFT, "y": TOP, "z": 100, "u": 0, "v": 0, "w": 0},
    "routine-algo": "locate",  # This shouldn't be necessary
    "AoA-algo": "weighted-rss",
    "max-iteration": 4 * ((TOP - BOTTOM) // TRAJECTORY_STEP +
                          (RIGHT - LEFT) // TRAJECTORY_STEP) * 1
    # "max-iteration": 50,
})

MAX_X = 650
MAX_Y = 500

USE_FAKE_MEASURMENTS = False  # Uses Atan2 + random noise instead of CloudRT

# plt config
DPI = 500  # 300


def predict(state, noise):
    """Propagation function callback.

    Args:
        state and noise

    Returns:
        The next state.
    """

    return state + noise


def measurement(state, noise, xUav, yUav):
    """Measurement function callback.

    Args:
        state and noise.

    Returns:
        The measurement.
    """

    z = math.atan2(state[1] - yUav,
                   state[0] - xUav) + noise
    z = utils.realAngle(z)

    return z


def fakeMeasurement(uav_truth, tx_truth, Rn):
    import random
    noise = random.gauss(0, Rn**0.5)
    xUav, yUav = uav_truth
    xTx, yTx = tx_truth

    z = math.atan2(yTx - yUav, xTx - xUav) + noise
    z = ukflib.angular_fix(z)

    return [z]


def uavTrajectory(drone):
    def goRight():
        drone.x = (drone.x + TRAJECTORY_STEP) % drone.MAX_X
        drone.y = (drone.y - 0) % drone.MAX_Y

    def goDown():
        drone.x = (drone.x + 0) % drone.MAX_X
        drone.y = (drone.y - TRAJECTORY_STEP) % drone.MAX_Y

    def goUp():
        drone.x = (drone.x + 0) % drone.MAX_X
        drone.y = (drone.y + TRAJECTORY_STEP) % drone.MAX_Y

    def goLeft():
        drone.x = (drone.x - TRAJECTORY_STEP) % drone.MAX_X
        drone.y = (drone.y - 0) % drone.MAX_Y

    if TRAJECTORY == "horiz":
        goRight()
    elif TRAJECTORY == "vert":
        goDown()
    elif TRAJECTORY == "diag":
        drone.x = (drone.x + TRAJECTORY_STEP) % drone.MAX_X
        drone.y = (drone.y - TRAJECTORY_STEP) % drone.MAX_Y
    elif TRAJECTORY == "square":
        if drone.x == LEFT and drone.y > BOTTOM:
            goDown()
        elif drone.y == BOTTOM and drone.x < RIGHT:
            goRight()
        elif drone.x == RIGHT and drone.y < TOP:
            goUp()
        elif drone.y == TOP and drone.x > LEFT:
            goLeft()


def run(exp, outputDir):
    drone, terminals, env, rt, log = readConfig(exp)

    # Init ukf params
    uav_truth = [[EXP["drone"]["x"], EXP["drone"]["y"]]]
    tx_truth = [
        [EXP["terminals"][USER]["x"], EXP["terminals"][USER]["y"]]
    ]
    tx_ukf = np.array([
        [TX_GUESS_X, TX_GUESS_Y]
    ])
    L = 2  # State dimension (xTx and yTx)
    # Process noise, no physical meaning, it just represents how much you trust
    # your model
    Rv = np.diag([RV, RV])
    Rn = np.diag([RN])  # Measurmement noise

    drone.ukf = ukflib.UnscentedKalmanFilter(
        L, Rv, Rn,
        init_state=tx_ukf[0],
        kappa=0,
        alpha=1.0,
        beta=2,
        angle_mask=[0, 0],  # state xTx and yTx are not angles
        init_covariance=np.eye(2) * 250
    )

    # Errors init
    weightedRssErr = []
    ukfErr = []

    @utils.add_method(Drone)
    def routine_locate_kalman(self, time, env):
        # Step 1 prediction
        self.ukf.predict(predict)

        # Step 2 correction
        if USE_FAKE_MEASURMENTS:
            z = fakeMeasurement(uav_truth[-1], tx_truth[-1], Rn[0, 0])
        else:
            env.scan(time, USER)
            z = utils.realAngle(self.getAoA())

        self.ukf.update(measurement, z, self.x, self.y)

        # Log errors
        thetaReal = measurement(tx_truth[-1], 0, self.x, self.y)
        thetaUkf = measurement(drone.ukf.state[:2], 0, self.x, self.y)
        thetaWeiRss = utils.realAngle(drone.getAoA())
        weightedRssErr.append(abs(utils.realAngle(thetaWeiRss - thetaReal)))
        ukfErr.append(abs(utils.realAngle(thetaUkf - thetaReal)))

    for i in range(exp['max-iteration']):
        drone.routine_locate_kalman(i, env)

        # Save results
        tx_ukf = np.append(tx_ukf, [drone.ukf.state], axis=0)

        # Update UAV and TX position
        uavTrajectory(drone)
        tx_truth.append(tx_truth[-1])
        uav_truth.append([drone.x, drone.y])

    log.close()

    tx_truth = np.array(tx_truth)
    uav_truth = np.array(uav_truth)

    # Figure 1 Tx localization on map
    plotFig(tx_ukf, tx_truth, uav_truth)
    figName = "ukf-loc-user-" + str(USER) + "-traj-" + TRAJECTORY
    plt.gcf().savefig(
        os.path.join(outputDir, figName),
        bbox_inches='tight',
        dpi=DPI
    )

    plt.gcf().clear()

    # Figure 2 Localization error
    plotError(weightedRssErr, ukfErr)
    figName = "loc-error-user-" + str(USER) + "-traj-" + TRAJECTORY
    plt.gcf().savefig(
        os.path.join(outputDir, figName),
        bbox_inches='tight',
        dpi=DPI
    )


def plotError(weightedRssErr, ukfErr):
    plt.plot(range(len(weightedRssErr)), np.rad2deg(weightedRssErr),
             label="Weighted-Rss")
    plt.plot(range(len(ukfErr)), np.rad2deg(ukfErr),
             label="UKF")

    plt.title("Localization error: Weighted-RSS vs Weighted-RSS + UKF")
    plt.xlabel("iteration [#]")
    plt.ylabel("Theta error [deg]")
    plt.legend()


def plotFig(tx_ukf, tx_truth, uav_truth):
    CMAP = cm.get_cmap('Spectral')

    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals([EXP["terminals"][USER]], bsOpt={
        "marker": "*",
        "markeredgecolor": 'black',
        "color": 'white'
    })
    plot.plot_flight(uav_truth, insideOpt={
        "marker": "None",
        "color": "lightgrey"
    })

    plt.plot(tx_ukf[:, 0], tx_ukf[:, 1], color='gainsboro')
    for i in range(len(tx_ukf)):
        plt.plot(
            tx_ukf[i, 0], tx_ukf[i, 1],
            label="UKF",
            marker=".",
            markersize=3,
            color=CMAP(1 - float(i) / len(tx_ukf))
        )
    plot.plot_terminals([tx_ukf[-1, :]], bsOpt={
        "marker": "*",
        "markeredgewidth": 1,
        "markeredgecolor": "black",
        "color": "red"
    })

    plt.title("UKF")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    plt.axis([0, MAX_X, 0, MAX_Y])


def args():
    """Handle arguments for the main function."""

    exp = EXP

    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    return [exp, outputDir]


if __name__ == '__main__':
    run(*args())
