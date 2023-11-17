"""
.. _modeling_ablation:

Modeling Ablation
-------------------------------------------
"""

#######################################################################################
# Objective
# =====================================================================================
#
# Ablation is an effective treatment used to protect an atmospheric reentry vehicle from
# the damaging effects of external high temperatures caused by shock wave and viscous
# heating. The ablative material is chipped away due to surface reactions that remove a
# significant amount of heat and keep the vehicle surface temperature below the melting
# point. In this tutorial, Fluent ablation model is demonstrated for a reentry vehicle
# geometry simplified as a 3D wedge.
#
# This tutorial demonstrates how to do the following:
#
# * Define boundary conditions for a high-speed flow.
# * Set up the ablation model to model effects of a moving boundary due to ablation.
# * Initiate and solve the transient simulation using the density-based solver.
#
# Problem Description:
# ====================
#
# The geometry of the 3D wedge considered in this tutorial is shown in following figure.
# The air flow passes around a nose of a re-entry vehicle operating under high speed
# conditions. The inlet air has a temperature of 4500 K, a gauge pressure of 13500 Pa,
# and a Mach number of 3. The domain is bounded above and below by symmetry planes
# (displayed in yellow). As the ablative coating chips away, the surface of the wall
# moves. The moving of the surface is modeled using dynamic meshes. The surface moving
# rate is estimated by Vieille's empirical law:

###############################################################################
# .. math::
#
#    r = A \cdot p^n

###############################################################################
# where r is the surface moving rate, p is the absolute pressure, and A and n are model
# parameters. In the considered case, A = 5 and n = 0.1.

#%%
# .. image:: ../../_static/ablation-problem-schematic.png
#    :align: center
#    :alt: Problem Schematic

#%%

####################################################################################
# Import required libraries/modules
# ==================================================================================

from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.visualization.pyvista import Graphics

###############################################################################
# Specifying save path
# ++++++++++++++++++++++
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.
save_path = Path(pyfluent.EXAMPLES_PATH)

####################################################################################
# Download example file
# ==================================================================================
import_filename = examples.download_file(
    "ablation.msh.h5", "pyfluent/examples/Ablation-tutorial", save_path=save_path
)

####################################################################################
# Fluent Solution Setup
# ==================================================================================

from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="xz")

####################################################################################
# Launch Fluent session with solver mode
# ==================================================================================

session = pyfluent.launch_fluent(
    precision="double",
    processor_count=4,
)

####################################################################################
# Import mesh
# ==================================================================================

session.file.read_case(file_name=import_filename)

####################################################################################
# Define models
# ==================================================================================

general = session.setup.general
general.solver.type = "density-based-implicit"
general.solver.time = "unsteady-1st-order"
general.operating_conditions.operating_pressure = 0

models = session.setup.models
models.energy.enabled = True
models.ablation.enabled = True

###################################################################
# Define material
# =================================================================

session.tui.define.materials.change_create(
    "air", "air", "yes", "ideal-gas", "no", "no", "no", "no", "no", "no"
)

############################################################################
# Following is alternative Settings API method to define material properties
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
session.setup.materials.fluid["air"]()
session.setup.materials.fluid["air"] = {
    "density": {
        "option": "ideal-gas",
    },
}

############################
# Define boundary conditions
# ==========================

bc = session.setup.boundary_conditions
bc.set_zone_type(
    zone_list=["inlet"],
    new_type="pressure-far-field",
)

inlet_bc = bc.pressure_far_field["inlet"]
inlet_bc.gauge_pressure.value = 13500
inlet_bc.t.value = 4500
inlet_bc.m.value = 3
inlet_bc.turbulent_intensity = 0.001

outlet_bc = bc.pressure_outlet["outlet"]
outlet_bc.momentum.gauge_pressure.value = 13500
outlet_bc.momentum.prevent_reverse_flow = True

#############################################
# Ablation boundary condition (Vielles Model)
# ++++++++++++++++++++++++++++++++++++++++++++
# Once you have specified the ablation boundary conditions for the wall,
# Ansys Fluent automatically enables the Dynamic Mesh model with the Smoothing and
# Remeshing options, creates the wall-ablation dynamic mesh zone, and configure
# appropriate dynamic mesh settings.

session.setup.boundary_conditions.wall["wall_ablation"].ablation = {
    "ablation_select_model": "Vielle's Model",
    "ablation_vielle_a": 5,
    "ablation_vielle_n": 0.1,
}

##############################
# Define dynamic mesh controls
# ============================

session.tui.define.dynamic_mesh.dynamic_mesh("yes")
session.tui.define.dynamic_mesh.zones.create(
    "interior--flow",
    "deforming",
    "faceted",
    "no",
    "no",
    "yes",
    "no",
    "yes",
    "yes",
    "no",
    "yes",
)
session.tui.define.dynamic_mesh.zones.create(
    "outlet",
    "deforming",
    "faceted",
    "no",
    "yes",
    "no",
    "yes",
    "yes",
    "coefficient-based",
    "0.1",
    "yes",
)
session.tui.define.dynamic_mesh.zones.create(
    "symm1",
    "deforming",
    "plane",
    "0",
    "-0.04",
    "0",
    "0",
    "-1",
    "0",
    "no",
    "yes",
    "no",
    "yes",
    "yes",
    "coefficient-based",
    "0.1",
    "yes",
)
session.tui.define.dynamic_mesh.zones.create(
    "symm2",
    "deforming",
    "plane",
    "0",
    "0.04",
    "0",
    "0",
    "1",
    "0",
    "no",
    "yes",
    "no",
    "yes",
    "yes",
    "coefficient-based",
    "0.1",
    "yes",
)
session.tui.define.dynamic_mesh.zones.create(
    "wall_ablation",
    "user-defined",
    "**ablation**",
    "no",
    "no",
    "189",
    "constant",
    "0",
    "yes",
    "yes",
    "0.7",
    "no",
    "no",
)

############################################
# Define solver settings
# =======================

session.setup.general.solver.time = "unsteady-2nd-order"

session.solution.controls.limits = {
    "min_pressure": 1,
    "max_pressure": 5e10,
    "min_temperature": 1,
    "max_temperature": 25000,
    "min_tke": 1e-14,
    "min_omega": 1e-20,
    "max_turb_visc_ratio": 100000,
    "positivity_rate": 0.2,
}

eqns = session.solution.monitor.residual.equations
eqns["continuity"].absolute_criteria = 1e-3
eqns["x-velocity"].absolute_criteria = 1e-3
eqns["y-velocity"].absolute_criteria = 1e-3
eqns["z-velocity"].absolute_criteria = 1e-3
eqns["energy"].absolute_criteria = 1e-6
eqns["k"].absolute_criteria = 1e-3
eqns["omega"].absolute_criteria = 1e-3

############################################
# Create report definitions
# ==========================

report_defs = session.solution.report_definitions
report_defs.drag["drag_force_x"] = {
    "zones": ["wall_ablation"],
    "report_output_type": "Drag Force",
}
report_defs.surface["pressure_avg_abl_wall"] = {
    "report_type": "surface-areaavg",
    "field": "pressure",
    "surface_names": ["wall_ablation"],
}
report_defs.surface["recede_point"] = {
    "report_type": "surface-vertexmax",
    "field": "z-coordinate",
    "surface_names": ["wall_ablation"],
}

############################################
# Create report plots
# ===================

report_plots = session.solution.monitor.report_plots
report_plots["drag_force_x"] = {
    "report_defs": ["drag_force_x"],
    "axes": {
        "x": {
            "number_format": {
                "format_type": "float",
                "precision": 4,
            },
        },
        "y": {
            "number_format": {
                "format_type": "exponential",
                "precision": 2,
            },
        },
    },
}
report_plots["pressure_avg_abl_wall"] = {
    "report_defs": ["pressure_avg_abl_wall"],
    "axes": {
        "x": {
            "number_format": {
                "format_type": "float",
                "precision": 4,
            },
        },
        "y": {
            "number_format": {
                "format_type": "exponential",
                "precision": 2,
            },
        },
    },
}
report_plots["recede_point"] = {
    "report_defs": ["recede_point"],
    "axes": {
        "x": {
            "number_format": {
                "format_type": "float",
                "precision": 4,
            },
        },
        "y": {
            "number_format": {
                "format_type": "exponential",
                "precision": 2,
            },
        },
    },
}

############################################
# Create report files
# ===================

report_files = session.solution.monitor.report_files
report_files["drag_force_x"] = {
    "report_defs": ["drag_force_x"],
    "file_name": "drag_force_x.out",
}
report_files["pressure_avg_abl_wall"] = {
    "report_defs": ["pressure_avg_abl_wall"],
    "file_name": "pressure_avg_abl_wall.out",
}
report_files["recede_point"] = {
    "report_defs": ["recede_point"],
    "file_name": "recede_point.out",
}

############################################
# Initialize and Save case
# ========================

session.solution.initialization.compute_defaults(
    from_zone_type="pressure-far-field",
    from_zone_name="inlet",
)
session.solution.initialization.standard_initialize()
session.solution.run_calculation.transient_controls.time_step_size = 1e-6

session.file.write_case(file_name=save_path / "ablation.cas.h5")

############################################
# Run the calculation
# ===================
# Note: It may take about half an hour to finish the calculation.

session.solution.run_calculation.dual_time_iterate(
    time_step_count=100,
    max_iter_per_step=20,
)

###############################################
# Save simulation data
# ====================
# Write case and data files

session.file.write_case_data(file_name=save_path / "ablation_Solved.cas.h5")

####################################################################################
# Post Processing
# ==================================================================================

###############################################
# Display plots
# =============

#%%
# .. image:: ../../_static/ablation-residual.png
#    :align: center
#    :alt: residual

#%%
#    Scaled residual plot

#%%
# .. image:: ../../_static/ablation-drag_force_x.png
#    :align: center
#    :alt: Drag force in x direction

#%%
#    History of the drag force on the ablation wall

#%%
# .. image:: ../../_static/ablation-avg_pressure.png
#    :align: center
#    :alt: Average pressure on the ablation wall

#%%
#    History of the averaged pressure on the ablation wall

#%%
# .. image:: ../../_static/ablation-recede_point.png
#    :align: center
#    :alt: Recede point (ablation)

#%%
#    Recede point (deformation due to ablation)

###############################################
# Display contour
# ================
# Following contours are displayed in the Fluent GUI:

results = session.results

results.surfaces.plane_surface["mid_plane"] = {
    "method": "zx-plane",
    "y": 0,
}

results.graphics.contour["contour_pressure"] = {
    "field": "pressure",
    "surfaces_list": ["mid_plane"],
}
results.graphics.contour.display(object_name="contour_pressure")

results.graphics.contour["contour_mach"] = {
    "field": "mach-number",
    "surfaces_list": ["mid_plane"],
}
results.graphics.contour.display(object_name="contour_mach")

###############################################
# Post processing with PyVista (3D visualization)
# ===============================================
# Following graphics is displayed in the a new window/notebook

graphics_session1 = Graphics(session)
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "pressure"
contour1.surfaces_list = ["mid_plane"]
contour1.display()
#%%
# .. image:: ../../_static/ablation-pressure.png
#    :align: center
#    :alt: Static Pressure Contour

#%%
#    Static Pressure Contour

contour1.field = "mach-number"
contour1.range.option = "auto-range-off"
contour1.range.auto_range_off.minimum = 0.5
contour1.range.auto_range_off.maximum = 3.0
contour1.display()

#%%
# .. image:: ../../_static/ablation-mach-number.png
#    :align: center
#    :alt: Mach Number Contour

#%%
#    Mach Number Contour

####################################################################################
# Close the session
# ==================================================================================

session.exit()

# sphinx_gallery_thumbnail_path = '_static/ablation-mach-number-thumbnail.png'
