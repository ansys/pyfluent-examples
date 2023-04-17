"""
Separator-Collection-Efficiency
===============================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

from pathlib import Path

# Oil Separator: Plot Collection Efficiency
# Import pyfluent module
import ansys.fluent.core as pyfluent

# Set log level to info
# pyfluent.set_log_level("INFO")

# Create a session
session = pyfluent.launch_fluent(version="3d", precision="double", processor_count=6)

from ansys.fluent.core import examples

import_filename = examples.download_file(
    "oil_separator.msh.h5",
    "pyfluent/examples/Separator-Collection-Efficiency",
)  # noqa: E501

# Fluent Solver Setup
# Read case file
session.tui.file.read_case(import_filename)

# Set gravity
session.tui.define.operating_conditions.gravity("Yes", 0, -9.81, 0)

# Set viscous parameters
session.tui.define.models.viscous.ke_realizable("yes")

# Set boundary condition
session.tui.define.boundary_conditions.list_zones()

# Set velocity inlet
session.tui.define.boundary_conditions.inlet = "velocity-inlet"

session.tui.solve.set.p_v_coupling(20)

# Set all discretization scheme constants
session.tui.solve.set.discretization_scheme("pressure", 14)
session.tui.solve.set.discretization_scheme("k", 1)
session.tui.solve.set.discretization_scheme("epsilon", 1)

# Set all relaxation constants
session.tui.solve.set.under_relaxation("pressure", 0.5)
session.tui.solve.set.under_relaxation("mom", 0.3)
session.tui.solve.set.under_relaxation("k", 0.6)
session.tui.solve.set.under_relaxation("epsilon", 0.6)
session.tui.solve.set.under_relaxation("turb-viscosity", 0.6)

# Define convergence criteria
session.tui.solve.monitors.residual.convergence_criteria(
    0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001
)

# Define injection properties
session.tui.define.injections(
    "create-injection",
    "injection-0",
    "no",
    "yes",
    "surface",
    "no",
    "inlet",
    "()",
    "no",
    "yes",
    "yes",
    "yes",
    10,
    0.15,
    "no",
    "no",
    "no",
    "no",
    0.0001,
    1,
    0.2,
    "q",
)

# Setup boundary conditions
session.setup.boundary_conditions.wall["wall_trap"].dpm_bc_type = "trap"

# Add report definitions
session.tui.solve.report_definitions.add(
    "vol-avg-vel",
    "volume-average",
    "field",
    "velocity-magnitude",
    "zone-names",
    "fluid*",
    "()",
    "q",
)

# Add report plots
session.tui.solve.report_plots.add(
    "vol-avg-vel", "report-defs", "vol-avg-vel", "()", "q"
)

# Add report files
session.tui.solve.report_files.add(
    "vol-avg-vel",
    "report-defs",
    "vol-avg-vel",
    "()",
    "file-name",
    str(Path(pyfluent.EXAMPLES_PATH) / "vol-avg-vel.out"),
    "q",
)

# Run Settings
# Set number of iterations
session.tui.solve.set.number_of_iterations(25)  # 1000

# In[26]:

# Initialize solver workflow
session.tui.solve.initialize.initialize_flow()

# Start iterations
session.tui.solve.iterate()

# Postprocessing
# Define iso surface
session.tui.surface.iso_surface("z-coordinate", "zmid", "()", "()", 0, "()")

# Define plane surface
session.tui.surface.plane_surface("midplane", "xy-plane", 0)

# Set contour properties
session.results.graphics.contour["contour-1"] = {}
session.results.graphics.contour["contour-1"].surfaces_list = ["zmid"]
session.results.graphics.contour["contour-1"].surfaces_list()
session.results.graphics.contour["contour-1"].field = "velocity-magnitude"

# Display contour
session.tui.display.objects.display("contour-1")

# Set views properties
session.tui.display.views.restore_view("front")
session.tui.display.views.auto_scale()

# Set x axis resolution
session.tui.display.set.picture.x_resolution(600)

# Set y axis resolution
session.tui.display.set.picture.y_resolution(600)

# Save the contour image
session.tui.display.save_picture("vel-contour.png")

# Adding graphics properties
session.results.graphics.lic["lic-1"] = {}
session.results.graphics.lic["lic-1"].surfaces_list = ["midplane"]
session.results.graphics.lic["lic-1"].field = "velocity-magnitude"
session.results.graphics.lic["lic-1"].lic_intensity_factor = 10
session.results.graphics.lic["lic-1"].texture_size = 10

# Display graphics object
session.tui.display.objects.display("lic-1")

# Save the graphics object
session.tui.display.save_picture("lic-vel.png")

# Write and save case data
save_case_as = str(Path(pyfluent.EXAMPLES_PATH) / "oil_separator.cas.h5")
session.tui.file.write_case_data(save_case_as)


# Velocity on Mid Plane

import csv

import matplotlib.pyplot as plt

# Calculating Collection Efficiency
import numpy as np

csv.register_dialect("skip_space", skipinitialspace=True)
dia = np.array(
    [5e-6, 6e-6, 7e-6, 8e-6, 9e-6, 1e-5, 1.1e-5, 1.2e-5, 1.3e-5, 1.4e-5, 1.5e-5]
)
area = 4.82e-5
density = 900
oil_mf = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55])
eff = np.zeros((len(oil_mf), len(dia)))

for i in range(len(oil_mf)):
    for j in range(len(dia)):
        session.tui.define.injections(
            "set-injection-properties",
            "injection-0",
            "injection-0",
            "no",
            "no",
            "no",
            "inlet",
            "()",
            "no",
            "yes",
            "yes",
            "yes",
            10,
            0.15,
            "no",
            "no",
            "no",
            "no",
            dia[j],
            (oil_mf[i] / density * area),
            oil_mf[i],
        )
        session.tui.report.dpm_sample("injection-0", "()", "outlet", "()", "()", "no")
        data = 0
        k = -1
        with open("outlet.dpm", "r") as datafile:
            plotting = csv.reader(datafile, delimiter=" ", dialect="skip_space")
            for rows in plotting:
                k = k + 1
                if k > 1:
                    data = data + eval(rows[8])
        eff[i][j] = 100.0 * (1.0 - data / oil_mf[i])


# 2D Plot using Matplotlib
plt.scatter(dia, eff[0], label="mass flow=0.05kg/s")
plt.scatter(dia, eff[-1], label="mass flow=0.55kg/s")
plt.title("Collection Efficiency Curve")
plt.xlabel("Droplet Diameter (m)")
plt.ylabel("Collection Efficiency(%)")
plt.legend()
plt.show()

# 3D Surface Plot using Plotly
import plotly.graph_objects as go

fig = go.Figure(data=[go.Surface(z=eff, x=dia, y=oil_mf)])
fig.update_layout(
    title="Separator Collection Efficiency",
    autosize=False,
    width=700,
    height=700,
    margin=dict(l=80, r=80, b=80, t=80),
)
fig.update_layout(
    scene=dict(
        xaxis_title="Droplet Diameter (m)",
        yaxis_title="Oil Mass Flow Rate (Kg/s)",
        zaxis_title="Collection Efficiency (%)",
    )
)
fig.show()