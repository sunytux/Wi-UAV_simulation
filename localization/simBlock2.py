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
from __future__ import print_function
import ukflib

from myTools import plot
from myTools import DEFAULT_CONF
from myTools.simulator import *
from myTools import utils

from docopt import docopt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Ellipse
from matplotlib.collections import LineCollection
import operator

# ffmpeg -framerate 4 -pattern_type glob -i '*.png' out.mp4

USER = 3
TX_GUESS_X, TX_GUESS_Y = 300, 250  # 300, 200

TRAJECTORY = "control"
TRAJECTORY_STEP = 50
LAPS = 2
X_UAV, Y_UAV = 20, 470
X_DISTANCE, Y_DISTANCE = 600, 440
if TRAJECTORY == "control":
    X_UAV, Y_UAV = 100, 350
    MAX_IT = 80
else:
    MAX_IT = (X_DISTANCE + Y_DISTANCE) * 2 * LAPS // TRAJECTORY_STEP


RN = np.deg2rad(57)  # np.deg2rad(27.011)
RV = 10  # 0.5
sigma0 = 200  # m

EXP = DEFAULT_CONF
# EXP.update({
#     "drone": {"x": X_UAV, "y": Y_UAV, "z": 100, "u": 0, "v": 0, "w": 0},
#     "routine-algo": "locate",  # This shouldn't be necessary
#     "AoA-algo": "weighted-rss",
#     "max-iteration": MAX_IT,
# })
EXP.update({
    "drone": {"x": X_UAV, "y": Y_UAV, "z": 100, "u": 0, "v": 0, "w": 0},
    "routine-algo": "locate_kalman",
    "routineKwargs": {
        "processNoise": 10,
        "measurementNoise": np.deg2rad(57),
        "sigma0": 200,
        "firstGuess": [300, 250],
        "user": USER
    },
    "AoA-algo": "weighted-rss",
    "max-iteration": MAX_IT,

})

MAX_X = 650
MAX_Y = 500

USE_FAKE_MEASURMENTS = False  # Uses Atan2 + random noise instead of CloudRT

# plt config
DPI = 500  # 300

PLT_STEP = 10
PLT_CMAP = 'Spectral_r'
PLT_ZOOMOUT = False


def predict(state, noise):
    """Propagation function callback.

    Args
        state and noise

    Returns
        The next state.

    """

    return state + noise


def measurement(state, noise, xUav, yUav):
    """Measurement function callback.

    Args
        state and noise.

    Returns
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


def squareTrajectory():

    for i in range(LAPS):
        x = X_UAV + i * TRAJECTORY_STEP
        y = Y_UAV - i * TRAJECTORY_STEP

        for y in range(y, y - Y_DISTANCE, -TRAJECTORY_STEP):
            yield x, y

        for x in range(x, x + X_DISTANCE, TRAJECTORY_STEP):
            yield x, y

        for y in range(y, y + Y_DISTANCE, TRAJECTORY_STEP):
            yield x, y

        for x in range(x, x - X_DISTANCE, -TRAJECTORY_STEP):
            yield x, y


def verticalTrajectory():
    x, y = X_UAV, Y_UAV

    for y in range(y, y - Y_DISTANCE - 1, -TRAJECTORY_STEP):
        yield x, y


def horizontalTrajectory():
    x, y = X_UAV, Y_UAV

    for x in range(x, x + X_DISTANCE + 1, TRAJECTORY_STEP):
        yield x, y


def run(exp, outputDir):
    drone, terminals, env, rt, log = readConfig(exp)

    # Init ukf params
    uav_truth = np.atleast_2d([[EXP["drone"]["x"], EXP["drone"]["y"]]])
    tx_truth = np.atleast_2d([
        [EXP["terminals"][USER]["x"], EXP["terminals"][USER]["y"]]
    ])
    tx_ukf = np.array([
        [TX_GUESS_X, TX_GUESS_Y]
    ])
    P_ukf = np.array([
        np.eye(2) * sigma0 ** 2
    ])

    tmp_pnt_x = []
    tmp_pnt_y = []

    L = 2  # State dimension (xTx and yTx)
    # Process noise, no physical meaning, it just represents how much you trust
    # your model
    Rv = np.diag([RV, RV])
    Rn = np.diag([RN])  # Measurmement noise

    # drone.ukf = ukflib.UnscentedKalmanFilter(
    #     L, Rv, Rn,
    #     init_state=tx_ukf[0],
    #     kappa=0,
    #     alpha=1.0,
    #     beta=2,
    #     angle_mask=[0, 0],  # state xTx and yTx are not angles
    #     init_covariance=P_ukf[0]
    # )

    # @utils.add_method(Drone)
    # def routine_locate_kalman(self, time, env):
    #     # Step 1 prediction
    #     self.ukf.predict(predict)

    #     # Step 2 correction
    #     if USE_FAKE_MEASURMENTS:
    #         z = fakeMeasurement(uav_truth[-1], tx_truth[-1], Rn[0, 0])
    #     else:
    #         env.scan(time, USER)
    #         z = utils.realAngle(self.getAoA())

    #     self.ukf.update(measurement, z, self.x, self.y)

    @utils.add_method(Drone)
    def localizeControl(self):
        P = np.atleast_2d(drone.ukf.covariance)
        lambda_, v = np.linalg.eig(P)
        lambda_ = np.sqrt(lambda_)

        sigma2X = P[0, 0]
        sigma2Y = P[1, 1]
        if sigma2X > sigma2Y:
            idxGreaterIncertitude = 0
        else:
            idxGreaterIncertitude = 1  # TODO this is not correct

        alpha = np.arctan2(*v[idxGreaterIncertitude])
        # print(lambda_)
        # print(np.rad2deg(np.arctan2(*v[0])), np.rad2deg(np.arctan2(*v[1])))
        # print(np.rad2deg(alpha))

        x2, y2 = self.x, self.y
        x1, y1 = self.x + np.cos(alpha), self.y + np.sin(alpha)
        x3, y3 = self.ukf.state[0:2]
        k = ((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1)) / ((y2-y1)**2 + (x2-x1)**2)
        x4 = x3 - k * (y2-y1)
        y4 = y3 + k * (x2-x1)
        tmp_pnt_x.append(x4)
        tmp_pnt_y.append(y4)
        alpha2 = np.arctan2(x4-x1, y4-y1)

        beta = utils.realAngle(math.atan2(self.ukf.state[1] - self.y,
                                          self.ukf.state[0] - self.x))

        phi1, rss1 = alpha2, 1
        phi2, rss2 = beta, 2

        # When phi1 and phi2 are separated by more than 180° their mean is on
        # the wrong side of the circle
        if max([phi1, phi2]) - min([phi1, phi2]) > np.deg2rad(180):
            if phi1 > phi2:
                phi2 += np.deg2rad(360)
            else:
                phi1 += np.deg2rad(360)

        gamma = (rss1 * phi1 + rss2 * phi2) / (rss1 + rss2)

        # print(np.rad2deg([beta, alpha2, gamma]))

        self.x += np.cos(gamma) * TRAJECTORY_STEP
        self.y += np.sin(gamma) * TRAJECTORY_STEP

    if TRAJECTORY == "square":
        trajectory = list(squareTrajectory())
    elif TRAJECTORY == "vert":
        trajectory = list(verticalTrajectory())
    elif TRAJECTORY == "horiz":
        trajectory = list(horizontalTrajectory())

    for time in range(EXP["max-iteration"]):
        print(
            "{:2.0f} % \r".format(float(time) * 100 / EXP["max-iteration"]),
            end=''
        )

        # Update UAV and TX position
        if TRAJECTORY == "control":
            drone.localizeControl()
        else:
            drone.x, drone.y = trajectory[time]

        drone.routine_locate_kalman(time, env)

        # Save results
        tx_ukf = np.append(tx_ukf, [drone.ukf.state], axis=0)
        P_ukf = np.append(P_ukf, [drone.ukf.covariance], axis=0)
        uav_truth = np.append(uav_truth, [[drone.x, drone.y]], axis=0)
        tx_truth = np.append(tx_truth, [tx_truth[-1, :]], axis=0)

        if time % PLT_STEP == 0:
            # Figure 1 Tx localization on map
            plotFig(tx_ukf, P_ukf, tx_truth, uav_truth)
            # plt.scatter(tmp_pnt_x[-1], tmp_pnt_y[-1], zorder=10, s=4)
            figName = "ukf-loc-user-{}-traj-{}-t{:03d}" \
                .format(USER, TRAJECTORY, time)
            plt.gcf().savefig(
                os.path.join(outputDir, figName),
                bbox_inches='tight',
                dpi=DPI
            )

            plt.gcf().clear()

    # Figure 1 Tx localization on map
    plotFig(tx_ukf, P_ukf, tx_truth, uav_truth)
    figName = "ukf-loc-user-{}-traj-{}-t{:03d}" \
        .format(USER, TRAJECTORY, time)
    plt.gcf().savefig(
        os.path.join(outputDir, figName),
        bbox_inches='tight',
        dpi=DPI
    )

    plt.gcf().clear()

    # Figure 2 errors
    plotErrors(tx_ukf, tx_truth)
    figName = "error-user-" + \
        str(USER) + "-traj-" + TRAJECTORY + "-t" + str(time)
    plt.gcf().savefig(
        os.path.join(outputDir, figName),
        bbox_inches='tight',
        dpi=DPI
    )

    log.close()


def plotFig(tx_ukf, P_ukf, tx_truth, uav_truth):

    plot.plot_scenario(edge='gainsboro', face='whitesmoke')
    plot.plot_terminals([EXP["terminals"][USER]], bsOpt={
        "marker": "*",
        "markeredgecolor": 'black',
        "color": 'white'
    })

    plot.plot_flight(uav_truth, insideOpt={
        "marker": ".",
        "color": "grey",
        "linewidth": 0.8,
    }, iOpt={
        # "marker": "None",
        "markersize": 3,
        "markeredgewidth": 1,
    }, fOpt={
        # "marker":"None",
        "markersize": 3,
        "markeredgewidth": 1,
    })

    lc = colorline(
        tx_ukf[:, 0], tx_ukf[:, 1],
        cmap=PLT_CMAP,
        opt={
            "linewidth": 0.5,
            "zorder": 3,
            "alpha": 0.3,
        }
    )
    plt.gca().add_collection(lc)

    for i in range(len(tx_ukf)):
        plt.plot(
            tx_ukf[i, 0], tx_ukf[i, 1],
            label="UKF",
            marker=".",
            markersize=3,
            markeredgewidth=0,
            markeredgecolor=cm.get_cmap(PLT_CMAP)(float(i) / len(tx_ukf)),
            markerfacecolor=cm.get_cmap(PLT_CMAP)(float(i) / len(tx_ukf)),
            zorder=3,
            alpha=0.4,
        )
    plot.plot_terminals([tx_ukf[-1, :]], bsOpt={
        "marker": "*",
        "markeredgewidth": 1,
        "markeredgecolor": "black",
        "color": "red",
        "zorder": 4
    })

    # Covariance ellipse
    IDX = -1
    P = np.atleast_2d(P_ukf[IDX])
    lambda_, v = np.linalg.eig(P)
    lambda_ = np.sqrt(lambda_)
    idxGreaterIncert = 0  # TODO check that
    alpha = np.rad2deg(np.arctan2(*v[idxGreaterIncert]))
    sigmaX = np.sqrt(P[0, 0])
    sigmaY = np.sqrt(P[1, 1])
    ell1 = Ellipse(
        xy=tx_ukf[IDX],
        width=2 * sigmaX,
        height=2 * sigmaY,
        angle=alpha,
        zorder=3,
        facecolor='None',
        edgecolor='gray',
        linewidth=0.9,
    )
    ell2 = Ellipse(
        xy=tx_ukf[IDX],
        width=2 * 2 * sigmaX,
        height=2 * 2 * sigmaY,
        angle=alpha,
        zorder=3,
        facecolor='None',
        edgecolor='gray',
        linewidth=0.5,
    )
    plt.gca().add_artist(ell1)
    plt.gca().add_artist(ell2)

    plt.title("UKF")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.grid(linestyle=':', linewidth=1, color='gainsboro')
    plt.axis('equal')
    if PLT_ZOOMOUT:
        plt.axis([-MAX_X * 0.5, MAX_X * 1.5, -MAX_Y * 0.5, MAX_Y * 1.5])
    else:
        plt.axis([0, MAX_X, 0, MAX_Y])


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def plotErrors(tx_ukf, tx_truth):
    dist_error = [dist(a, b) for a, b in zip(tx_ukf, tx_truth)]
    x_error = [abs(a[0] - b[0]) for a, b in zip(tx_ukf, tx_truth)]
    y_error = [abs(a[1] - b[1]) for a, b in zip(tx_ukf, tx_truth)]

    iterations = range(len(tx_truth))
    ax1 = plt.subplot(311)
    plt.plot(iterations, y_error)
    plt.ylabel("y axis error [m]")
    plt.setp(ax1.get_xticklabels(), visible=False)

    ax2 = plt.subplot(312, sharex=ax1)
    plt.plot(iterations, x_error)
    plt.ylabel("x axis error [m]")
    plt.setp(ax2.get_xticklabels(), visible=False)

    plt.subplot(313, sharex=ax1)
    plt.plot(iterations, dist_error)
    plt.ylabel("Distance error [m]")

    plt.gcf().suptitle("Errors")
    plt.xlabel("Iteration [#]")


def args():
    """Handle arguments for the main function."""

    exp = EXP

    outputDir = docopt(__doc__)['-o']
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    return [exp, outputDir]


def colorline(
    x, y, z=None, cmap='copper', norm=plt.Normalize(0.0, 1.0), opt={}):
    """
    http://nbviewer.ipython.org/github/dpsanders/matplotlib-examples/blob/master/colorline.ipynb
    http://matplotlib.org/examples/pylab_examples/multicolored_line.html
    Plot a colored line with coordinates x and y
    Optionally specify colors in the array z
    Optionally specify a colormap, a norm function and a line width
    """

    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))

    # Special case if a single number:
    # to check for numerical input -- this is a hack
    if not hasattr(z, "__iter__"):
        z = np.array([z])

    z = np.asarray(z)

    def make_segments(x, y):
        """
        Create list of line segments from x and y coordinates, in the correct
        format for LineCollection: an array of the form numlines x (points per
        line) x 2 (x and y) array
        """

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        return segments

    segments = make_segments(x, y)
    lc = LineCollection(segments, array=z, cmap=cmap, norm=norm, **opt)

    ax = plt.gca()
    ax.add_collection(lc)

    return lc


if __name__ == '__main__':
    run(*args())