"""
003-Tyler-Sofrin-Modes-Compressor
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Tyler/Sofrin Mode Calculator

# Background
# Tyler and Sofrin (1961) showed that rotor/stator interactions
# produce an infinite collection of spinning modes
# Each TS mode has an m-lobed pattern and rotates at a speed of BnΩ/m where:
#         m = nB+kV (m is the Tyler/Sofrin mode number)
#         n = impeller frequency harmonic
#         k = vane harmonic
#         B = # rotating blades
#         V = # stationary vanes
#
# Example:
#         8-blade rotor interacting with a 6-vane stator
#         2-lobed pattern turning at (8)(1)/(2) = 4 times shaft speed
#
# ![Exampletable](ExampleTable.jpg)
#
# ![TSmode](TSmode.jpg)

# Discrete Fourier Transform (DFT)
# To determine the pressure associated
# with each TS-mode,
# extend the simulation and compute the DFT of pressure
# @ desired blade passing frequency harmonics
# Disable (Hanning) windowing (for periodic flows such as this).
# Failure to do this will result in ½ expected magnitudes (for periodic flows)
#     `(rpsetvar 'rtdft/window "none")`
# Ensure that sampling period corresponds to
# a multiple of the period of the lowest frequency.
# It can be a single period but
# it’s better to run for multiple periods (e.g. 1 revolution)
# The DFT data is only valid if
# sampling is performed across entire specified sampling period
# Nyquist criteria: Ensure that DFT sampling frequency is
# greater than 2*highest frequency

# Please note that the cas/dat file
# included with this notebook is for demonstration purposes.
# A finer mesh is required for proper acoustic analysis.

# This line is needed at the beginning of the notebook to allow for an interactive plot
# get_ipython().run_line_magic("matplotlib", "widget")

# Import Pyfluent module
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_filename = examples.download_file(
    "axial_comp_fullWheel_DFT.cas.h5",
    "pyfluent/examples/003-Tyler-Sofrin-Modes-Compressor-Ryan-OConnor",
)  # noqa: E501

# Create a session object
session = pyfluent.launch_fluent(mode="solver")

# Check server status
session.check_health()

# User Inputs
#
# The varnames should correspond to the variables writted from the DFT and
# can be determined by manually inspecting the solution variables as depicted below:
# ![Varnames](varnames.jpg)

n_mode = [0, 1, 2, 3]  # Impeller frequency harmonics
varname = [
    "static-pressure-1_0.00mHz-ta1",
    "static-pressure-1_9.80kHz-ta2",
    "static-pressure-1_20.20kHz-ta3",
    "static-pressure-1_30.00kHz-ta4",
]  # Variable names from DFT analysis. Ensure len(n_mode)=len(varname)
r = 0.082  # meters
z = -0.037  # meters
dtheta = 5  # degrees
m_max = 50  # maximum TS mode number

# TS mode number increment.
# Plot will be from -m_max to +m_max, incremented by m_inc
m_inc = 2

# CAS/DAT Files
# The dat file should correspond to the already completed DFT simulation.

# Read a case file
session.tui.file.read_case_data(
    "axial_comp_fullWheel_DFT.cas.h5"
)  # The dat file containing the DFT results


# Create Monitor Points
import math

for angle in range(0, 360, dtheta):
    x = math.cos(math.radians(angle)) * r
    y = math.sin(math.radians(angle)) * r
    session.tui.surface.point_surface("point-" + str(angle), x, y, z)


# Compute An and Bn at each monitor point
import numpy as np

An = np.zeros((len(varname), int(360 / dtheta)))
Bn = np.zeros((len(varname), int(360 / dtheta)))

session.solution.report_definitions.surface["mag-report"] = {
    "report_type": "surface-vertexmax"
}
session.solution.report_definitions.surface["phase-report"] = {
    "report_type": "surface-vertexmax"
}

for angle_ind, angle in enumerate(range(0, 360, dtheta)):
    for n_ind, variable in enumerate(varname):
        session.solution.report_definitions.surface["mag-report"] = {
            "surface_names": ["point-" + str(angle)],
            "field": str(variable) + "-mag",
        }
        mag = session.solution.report_definitions.compute(report_defs=["mag-report"])
        mag = mag[0]["mag-report"][0]
        session.solution.report_definitions.surface["phase-report"] = {
            "surface_names": ["point-" + str(angle)],
            "field": str(variable) + "-phase",
        }
        phase = session.solution.report_definitions.compute(
            report_defs=["phase-report"]
        )
        phase = phase[0]["phase-report"][0]
        An[n_ind][angle_ind] = mag * math.cos(phase)
        Bn[n_ind][angle_ind] = -mag * math.sin(phase)


# Write Fourier Coefficients to File
#
# This step is only required if data is to be processed outside of this script.
file1 = open("FourierCoefficients.txt", "w")
file1.write("n theta An Bn \n")

for n_ind, variable in enumerate(varname):
    for ind, x in enumerate(An[n_ind, :]):
        file1.write(
            str(n_mode[n_ind])
            + ","
            + str(ind * dtheta)
            + ","
            + str(An[n_ind, ind])
            + ","
            + str(Bn[n_ind, ind])
            + "\n"
        )


# Calculating Pnm
#
# ![TS_formulas](TS_formulas.jpg)
# Create list of m values based on m_max and m_inc
m_mode = range(-m_max, m_max + m_inc, m_inc)

# Initialize solution matrices with zeros
Anm = np.zeros((len(varname), len(m_mode)))
Bnm = np.zeros((len(varname), len(m_mode)))
Pnm = np.zeros((len(varname), len(m_mode)))

for n_ind, variable in enumerate(varname):  # loop over n modes
    for m_ind, m in enumerate(m_mode):  # loop over m modes
        for angle_ind, angle in enumerate(
            np.arange(0, math.radians(360), math.radians(dtheta))
        ):  # loop over all angles, in radians
            Anm[n_ind][m_ind] += An[n_ind][angle_ind] * math.cos(m * angle) - Bn[n_ind][
                angle_ind
            ] * math.sin(m * angle)
            Bnm[n_ind][m_ind] += An[n_ind][angle_ind] * math.sin(m * angle) + Bn[n_ind][
                angle_ind
            ] * math.cos(m * angle)
        Anm[n_ind][m_ind] = Anm[n_ind][m_ind] / (2 * math.pi) * math.radians(dtheta)
        Bnm[n_ind][m_ind] = Bnm[n_ind][m_ind] / (2 * math.pi) * math.radians(dtheta)
        Pnm[n_ind][m_ind] = math.sqrt(Anm[n_ind][m_ind] ** 2 + Bnm[n_ind][m_ind] ** 2)

# P_00 is generally orders of magnitude larger than that of other modes.
# Giving focus to other modes by setting P_00 equal to zero
Pnm[0][int(len(m_mode) / 2)] = 0

# get_ipython().run_line_magic("matplotlib", "inline")
# from mpl_toolkits import mplot3d
import random

# Tyler/Sofrin Mode Plot
import matplotlib.pyplot as plt

fig = plt.figure()
ax = plt.axes(projection="3d")
ax.set_xlabel("TS mode, m")
ax.set_ylabel("Imp Freq Harmonic, n")
ax.set_zlabel("Pnm [Pa]")
plt.yticks(n_mode)
for n_ind, n in enumerate(n_mode):
    x = m_mode
    y = np.full(Pnm.shape[1], n)
    z = Pnm[n_ind]
    rgb = (random.random(), random.random(), random.random())
    ax.plot3D(x, y, z, c=rgb)

# End current session
# session.exit()
