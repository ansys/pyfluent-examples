"""
#################################
Automotive Brake Thermal Analysis
#################################

Objective:
==========

Braking surfaces get heated due to frictional heating during braking.
High temperature affects the braking performance and life of the braking system.
This example demonstrates:

* Fluent setup and simulation using PyFluent
* Post processing using PyVista (3D Viewer) and Matplotlib (2D graphs)

"""

####################################################################################
# Import required libraries/modules
# ==================================================================================

import csv
from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

###############################################################################
# PyVista
# --------------------
import ansys.fluent.visualization.pyvista as pv

##############################################################################
# Matplotlib
# --------------------
import matplotlib.pyplot as plt

###############################################################################
# Specifying save path
# ====================
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.

save_path = Path(pyfluent.EXAMPLES_PATH)

import_filename = examples.download_file(
    "brake.msh.h5",
    "pyfluent/examples/Brake-Thermal-PyVista-Matplotlib",
    save_path=save_path,
)

####################################################################################
# Fluent Solution Setup
# ==================================================================================

####################################################################################
# Launch Fluent session with solver mode
# --------------------------------------

session = pyfluent.launch_fluent(
    mode="solver", show_gui=False, precision="double", processor_count=2
)
session.health_check_service.status()

####################################################################################
# Import mesh
# ------------

session.file.read_case(file_name=import_filename)

############################
# Define models and material
# --------------------------

energy = session.setup.models.energy
energy.enabled = True
energy.viscous_dissipation = False
energy.pressure_work = False
energy.kinetic_energy = False
energy.inlet_diffusion = True

session.setup.general.solver.time = "unsteady-2nd-order-bounded"

session.setup.materials.database.copy_by_name(type="solid", name="steel")

#########################################
# Solve only energy equation (conduction)
# ---------------------------------------

equations = session.solution.controls.equations
equations["flow"] = False
equations["kw"] = False

############################################
# Define disc rotation
# --------------------
# (15.79 rps corresponds to 100 km/h car speed
# with 0.28 m of axis height from ground)

session.setup.cell_zone_conditions.solid["disc1"].solid_motion = {
    "solid_motion": True,
    "solid_omega": -15.79,
    "solid_motion_axis_origin": [-0.035, -0.821, 0.045],
    "solid_motion_axis_direction": [0, 1, 0],
}
session.setup.cell_zone_conditions.copy(from_="disc1", to="disc2")

###################################################
# Apply frictional heating on pad-disc surfaces
# ----------------------------------------------
# Wall thickness 0f 2 mm has been assumed and 2e9 w/m3 is the heat generation which
# has been calculated from kinetic energy change due to braking.

boundary_conditions = session.setup.boundary_conditions
boundary_conditions.wall["wall_pad-disc1"].thermal = {
    "wall_thickness": {
        "value": 0.002,
    },
    "q_dot": {
        "value": 2e9,
    },
}
boundary_conditions.copy(from_="wall_pad-disc1", to="wall-pad-disc2")

############################################################
# Apply convection cooling on outer surfaces due to air flow
# -----------------------------------------------------------
# Outer surfaces are applied a constant htc of 100 W/(m2 K)
# and 300 K free stream temperature

wall_disc_thermal_bcs = boundary_conditions.wall["wall-disc*"].thermal
wall_disc_thermal_bcs.thermal_bc = "Convection"
wall_disc_thermal_bcs.h.value = 100
wall_disc_thermal_bcs.tinf.value = 300

wall_geom_thermal_bcs = boundary_conditions.wall["wall-geom*"].thermal
wall_geom_thermal_bcs.thermal_bc = "Convection"
wall_geom_thermal_bcs.h.value = 100
wall_geom_thermal_bcs.tinf.value = 300

###############################################
# Initialize
# ----------
# Initialize with 300 K temperature

session.solution.initialization.standard_initialize()

###############################################
# Post processing setup
# ---------------------
# * Report definitions and monitor plots
# * Set contour plot properties
# * Set views and camera
# * Set animation object

volume_reports = session.solution.report_definitions.volume
volume_reports["max-pad-temperature"] = {
    "report_type": "volume-max",
    "cell_zones": ["geom-1-innerpad", "geom-1-outerpad"],
    "field": "temperature",
}
volume_reports["max-disc-temperature"] = {
    "report_type": "volume-max",
    "cell_zones": ["disc1", "disc2"],
    "field": "temperature",
}

session.solution.monitor.report_plots["max-temperature"] = {
    "report_defs": ["max-pad-temperature", "max-disc-temperature"],
}

report_file_path = Path(save_path) / "max-temperature.out"
session.solution.monitor.report_files["max-temperature"] = {
    "report_defs": ["max-pad-temperature", "max-disc-temperature", "flow-time"],
    "file_name": str(report_file_path),
}


session.results.graphics.contour["contour-1"] = {
    "boundary_values": True,
    "color_map": {
        "color": "field-velocity",
        "font_automatic": True,
        "font_name": "Helvetica",
        "font_size": 0.032,
        "format": "%0.2e",
        "length": 0.54,
        "log_scale": False,
        "position": 1,
        "show_all": True,
        "size": 100,
        "user_skip": 9,
        "visible": True,
        "width": 6.0,
    },
    "coloring": {"smooth": False},
    "contour_lines": False,
    "display_state_name": "None",
    "draw_mesh": False,
    "field": "temperature",
    "filled": True,
    "mesh_object": "",
    "node_values": True,
    "range_option": {"auto_range_on": {"global_range": True}},
}


session.results.graphics.contour["temperature"] = {
    "field": "temperature",
    "surfaces_list": "wall*",
    "color_map": {
        "format": "%0.1f",
    },
    "range_option": {
        "option": "auto-range-off",
        "auto_range_off": {
            "minimum": 300.0,
            "maximum": 400.0,
        },
    },
}

views = session.results.graphics.views
views.restore_view(view_name="top")
views.camera.zoom(factor=2)
views.save_view(view_name="animation-view")

session.solution.calculation_activity.solution_animations["animate-temperature"] = {
    "animate_on": "temperature",
    "frequency_of": "flow-time",
    "flow_time_frequency": 0.05,
    "view": "animation-view",
}

###############################################
# Run simulation
# ---------------
# * Run simulation for 2 seconds flow time
# * Set time step size
# * Set number of time steps and maximum number of iterations per time step

run_calculation = session.solution.run_calculation
run_calculation.transient_controls.time_step_size = 0.01
run_calculation.dual_time_iterate(
    time_step_count=200,
    max_iter_per_step=5,
)

###############################################
# Save simulation data
# --------------------
# Write case and data files
save_case_data_as = Path(save_path) / "brake-final.cas.h5"
session.file.write_case_data(file_name=save_case_data_as)

###############################################
# Post processing with PyVista (3D visualization)
# ===============================================

###############################################
# Create a graphics session
# -------------------------
graphics_session1 = pv.Graphics(session)

###############################################
# Temperature contour object
# --------------------------
contour1 = graphics_session1.Contours["temperature"]

###############################################
# Check available options for contour object
# -------------------------------------------

contour1()

###############################################
# Set contour properties
# ----------------------

contour1.field = "temperature"
contour1.surfaces_list = [
    "wall-disc1",
    "wall-disc2",
    "wall-pad-disc2",
    "wall_pad-disc1",
    "wall-geom-1-bp_inner",
    "wall-geom-1-bp_outer",
    "wall-geom-1-innerpad",
    "wall-geom-1-outerpad",
]
contour1.range.option = "auto-range-off"
contour1()
contour1.range.auto_range_off.minimum = 300
contour1.range.auto_range_off.maximum = 400

###############################################
# Display contour
# ---------------

contour1.display()

#%%
# .. image:: ../../_static/brake_surface_temperature.png
#    :align: center
#    :alt: Brake Surface Temperature Contour

#%%
#    Brake Surface Temperature

###############################################
# Post processing with Matplotlib (2D graph)
# ===============================================

###############################################
# Read monitor file
# -----------------

X = []
Y = []
Z = []
i = -1
with open(report_file_path, "r") as datafile:
    plotting = csv.reader(datafile, delimiter=" ")
    for rows in plotting:
        i = i + 1
        if i > 2:
            X.append(float(rows[3]))
            Y.append(float(rows[2]))
            Z.append(float(rows[1]))

###############################################
# Plot graph
# ----------

plt.title("Maximum Temperature", fontdict={"color": "darkred", "size": 20})
plt.plot(X, Z, label="Max. Pad Temperature", color="red")
plt.plot(X, Y, label="Max. Disc Temperature", color="blue")
plt.xlabel("Time (sec)")
plt.ylabel("Max Temperature (K)")
plt.legend(loc="lower right", shadow=True, fontsize="x-large")

###############################################
# Show graph
# ----------

plt.show()

#%%
# .. image:: ../../_static/brake_maximum_temperature.png
#    :align: center
#    :alt: Brake Maximum Temperature

#%%
#    Brake Maximum Temperature

####################################################################################
# Close the session
# ==================================================================================
session.exit()

# sphinx_gallery_thumbnail_path = '_static/brake_surface_temperature-thumbnail.png'
