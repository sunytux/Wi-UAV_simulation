#! /usr/bin/python2.7 -u
# -*- coding: utf-8 -*-

"""Plot the radiation pattern of a given antenna.

The input file format should be compatible with the CloudRT database.

Usage:
    plotAntenna.py [<PATH>]

Arguments:
    <PATH>      Path to the antenna json file.

Options:
    -h, --help
"""
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d
from docopt import docopt

POINTS = 36


def main(phi_re, phi_im, theta_re, theta_im):

    # phi and theta axis
    phi = np.linspace(0, 360, 2 * POINTS, endpoint=True)
    theta = np.linspace(0, 180, POINTS, endpoint=True)

    # Convert axis to 2d for plot_surface
    phi2d, theta2d = np.meshgrid(phi, theta)

    def mod_E_phi(az, el):
        return abs(phi_re[az][el] + 1j * phi_im[az][el])

    def mod_E_theta(az, el):
        return abs(theta_re[az][el] + 1j * theta_im[az][el])

    def G(az, el):
        """Return the gain given a direction.

        az: Azimuthal angle included inside [0, 360] (= phi).
        el: Elevation angle included inside [0, 180] (=theta), 0 = zenith axis.
        """

        # If the JSON file contains less than 360 entries
        az = int(math.floor((az / 360) * (len(phi_re) - 1)))
        el = int(math.floor((el / 180) * (len(phi_re[0]) - 1)))
        return mod_E_phi(az, el)**2 + mod_E_theta(az, el)**2

    r = np.array([G(p, t) for p, t in zip(np.ravel(phi2d), np.ravel(theta2d))])
    r2d = r.reshape(phi2d.shape)

    x2d = r2d * np.sin(np.deg2rad(theta2d)) * np.cos(np.deg2rad(phi2d))
    y2d = r2d * np.sin(np.deg2rad(theta2d)) * np.sin(np.deg2rad(phi2d))
    z2d = r2d * np.cos(np.deg2rad(theta2d))

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.plot_surface(x2d, y2d, z2d,
                    cmap=plt.get_cmap('jet'),
                    linewidth=100, antialiased=True, alpha=0.4)
    # Reference point
    ax.scatter(0, 0, 0, s=100, c='#000000')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()


def args():
    """Handle arguments for the main function."""
    if docopt(__doc__)['<PATH>']:
        path = docopt(__doc__)['<PATH>']
    else:
        path = "/opt/COTS/CloudRT/database/antenna/Microstripantenna.json"
        # path = "/opt/COTS/CloudRT/database/antenna/omni_vert_pol.json"
        # path = "/opt/COTS/CloudRT/database/antenna/256_cylin.json"

    with open(path, 'r') as f:
        datas = json.load(f)

        phi_re = datas["phi"]["real"]
        phi_im = datas["phi"]["imag"]

        theta_re = datas["theta"]["real"]
        theta_im = datas["theta"]["imag"]

    return [phi_re, phi_im, theta_re, theta_im]


if __name__ == '__main__':
    main(*args())
