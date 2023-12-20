"""
.. _conjugate_heat_transfer:

Conjugate Heat Transfer
-----------------------
"""

#######################################################################################
# Objective
# =====================================================================================
#
# This tutorial demonstrates how to model forced convection in a louvered fin heat
# exchanger. This case solves equations for both Fluid and Solid domain.
# As a result, temperature field evolved together.
#
# This tutorial demonstrates how to perform the following tasks:
#
# * Calculate the fin heat transfer rate.
# * Use periodic boundaries to reduce the size of the computational domain.
# * Use a convective thermal boundary condition to represent heat transfer.
# * Examine and understand the relationship between flow and temperature.

# sphinx_gallery_thumbnail_path = '_static/cht_xy_pressure.png'

###################################
# Import required libraries/modules
# =================================

import csv
from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.visualization import set_config
from ansys.fluent.visualization.matplotlib import Plots  # noqa: F401
from ansys.fluent.visualization.pyvista import Graphics
import matplotlib.pyplot as plt

###########################################################################
# Configure PyFluent Visualization
# ================================
# Set the following options:
#
# * ``blocking=True``: Block the execution thread when a plot is displayed.
#   This will allow you to inspect it before proceeding. To proceed, close the
#   plot.
# * ``set_view_on_display="isometric"``: Set the default view in a plot to
#   isometric.

set_config(blocking=True, set_view_on_display="isometric")

###########################################################################
# Specifying save path
# ====================
# * save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# * Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# * Path("~/pyfluent-examples-tests") in Linux.

save_path = Path(pyfluent.EXAMPLES_PATH)

geom_filename = examples.download_file(
    "cht_fin_htc_new.scdoc",
    "pyfluent/examples/CHT",
    save_path=save_path,
)

#######################
# Fluent Solution Setup
# =====================

#########################################
# Launch Fluent session with meshing mode
# =======================================

meshing = pyfluent.launch_fluent(
    mode="meshing",
    precision="double",
    show_gui=True,
    processor_count=4,
    cwd=save_path,
)

meshing.health_check_service.check_health()

#############################################################################
# Start Watertight Geometry Meshing Workflow
# ==========================================

meshing.workflow.InitializeWorkflow(WorkflowType=r"Watertight Geometry")

meshing.workflow.TaskObject["Import Geometry"].Arguments.update_dict(
    {"FileName": geom_filename}
)
meshing.workflow.TaskObject["Import Geometry"].Execute()

meshing.workflow.TaskObject["Add Local Sizing"].Execute()

meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments.update_dict(
    {
        "CFDSurfaceMeshControls": {
            "MinSize": 0.3,
            "MaxSize": 1,
            "ScopeProximityTo": "faces",
        },
    }
)
meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)
meshing.workflow.TaskObject["Describe Geometry"].Arguments.setState(
    {
        r"CappingRequired": r"No",
        r"InvokeShareTopology": r"No",
        r"NonConformal": r"Yes",
        r"SetupType": r"The geometry consists of both fluid and solid regions and/or voids",  # noqa: E501
    }
)

meshing.workflow.TaskObject["Describe Geometry"].Execute()

#############################################################################
# Update Interface Boundaries; Create Region
# ==========================================

meshing.workflow.TaskObject["Update Boundaries"].Arguments.setState(
    {
        r"BoundaryLabelList": [
            r"interface-out-solid-a",
            r"interface-out-high-a",
            r"interface-out-low-a",
            r"interface-4-solid-sweep",
            r"interface-4-high-sweep",
            r"interface-4-low-sweep",
            r"interface-3-solid-sweep",
            r"interface-3-high-sweep",
            r"interface-3-low-sweep",
            r"interface-2-solid-sweep",
            r"interface-2-high-sweep",
            r"interface-2-low-sweep",
            r"interface-1-solid-sweep",
            r"interface-1-high-sweep",
            r"interface-1-low-sweep",
            r"interface-solid-in-a",
            r"interface-in-high-a",
            r"interface-in-low-a",
            r"interface-tube-2-solid-a",
            r"interface-tube-2-high-a",
            r"interface-tube-2-low-a",
            r"interface-tube-1-solid-a",
            r"interface-tube-1-high-a",
            r"interface-tube-1-low-a",
            r"interface-4-fluid-high-tet",
            r"interface-4-fluid-low-tet",
            r"interface-3-fluid-low-tet",
            r"interface-3-fluid-high-tet",
            r"interface-2-fluid-high-tet",
            r"interface-2-fluid-low-tet",
            r"interface-1-fluid-high-tet",
            r"interface-1-fluid-low-tet",
            r"interface-1-solid-tet-4",
            r"interface-1-solid-tet-3",
            r"interface-1-solid-tet-2",
            r"interface-1-solid-tet-1",
        ],
        r"BoundaryLabelTypeList": [
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
            r"interface",
        ],
        r"OldBoundaryLabelList": [
            r"interface-out-solid-a",
            r"interface-out-high-a",
            r"interface-out-low-a",
            r"interface-4-solid-sweep",
            r"interface-4-high-sweep",
            r"interface-4-low-sweep",
            r"interface-3-solid-sweep",
            r"interface-3-high-sweep",
            r"interface-3-low-sweep",
            r"interface-2-solid-sweep",
            r"interface-2-high-sweep",
            r"interface-2-low-sweep",
            r"interface-1-solid-sweep",
            r"interface-1-high-sweep",
            r"interface-1-low-sweep",
            r"interface-solid-in-a",
            r"interface-in-high-a",
            r"interface-in-low-a",
            r"interface-tube-2-solid-a",
            r"interface-tube-2-high-a",
            r"interface-tube-2-low-a",
            r"interface-tube-1-solid-a",
            r"interface-tube-1-high-a",
            r"interface-tube-1-low-a",
            r"interface-4-fluid-high-tet",
            r"interface-4-fluid-low-tet",
            r"interface-3-fluid-low-tet",
            r"interface-3-fluid-high-tet",
            r"interface-2-fluid-high-tet",
            r"interface-2-fluid-low-tet",
            r"interface-1-fluid-high-tet",
            r"interface-1-fluid-low-tet",
            r"interface-1-solid-tet-4",
            r"interface-1-solid-tet-3",
            r"interface-1-solid-tet-2",
            r"interface-1-solid-tet-1",
        ],
        r"OldBoundaryLabelTypeList": [
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
            r"wall",
        ],
        r"OldLabelZoneList": [
            r"interface-out-solid-a",
            r"interface-out-high-a",
            r"interface-out-low-a",
            r"interface-4-solid-sweep",
            r"interface-4-high-sweep",
            r"interface-4-low-sweep",
            r"interface-3-solid-sweep",
            r"interface-3-high-sweep",
            r"interface-3-low-sweep",
            r"interface-2-solid-sweep",
            r"interface-2-high-sweep",
            r"interface-2-low-sweep",
            r"interface-1-solid-sweep",
            r"interface-1-high-sweep",
            r"interface-1-low-sweep",
            r"interface-solid-in-a",
            r"interface-in-high-a",
            r"interface-in-low-a",
            r"interface-tube-2-solid-a.2",
            r"interface-tube-2-solid-a.1",
            r"interface-tube-2-solid-a",
            r"interface-tube-2-high-a.2",
            r"interface-tube-2-high-a.1",
            r"interface-tube-2-high-a",
            r"interface-tube-2-low-a.2",
            r"interface-tube-2-low-a.1",
            r"interface-tube-2-low-a",
            r"interface-tube-1-solid-a.2",
            r"interface-tube-1-solid-a.1",
            r"interface-tube-1-solid-a",
            r"interface-tube-1-high-a.2",
            r"interface-tube-1-high-a.1",
            r"interface-tube-1-high-a",
            r"interface-tube-1-low-a.2",
            r"interface-tube-1-low-a.1",
            r"interface-tube-1-low-a",
            r"interface-4-fluid-high-tet",
            r"interface-4-fluid-low-tet",
            r"interface-3-fluid-low-tet",
            r"interface-3-fluid-high-tet",
            r"interface-2-fluid-high-tet",
            r"interface-2-fluid-low-tet",
            r"interface-1-fluid-high-tet",
            r"interface-1-fluid-low-tet",
            r"interface-1-solid-tet-4",
            r"interface-1-solid-tet-3",
            r"interface-1-solid-tet-2",
            r"interface-1-solid-tet-1",
        ],
    }
)

meshing.workflow.TaskObject["Update Boundaries"].Execute()

meshing.workflow.TaskObject["Create Regions"].Execute()

#############################################################################
# Custom Journal for Creating Periodicity due to Non-Conformal Objects
# ====================================================================

meshing.workflow.TaskObject["Describe Geometry"].InsertNextTask(
    CommandName=r"RunCustomJournal"
)
meshing.workflow.TaskObject["Run Custom Journal"].Rename(NewName=r"set-periodicity")
meshing.workflow.TaskObject["set-periodicity"].Arguments.update_dict(
    {
        r"JournalString": r"""/bo rps translational semi-auto periodic-1-high """
        + r"""periodic-2-high periodic-3-high periodic-4-high , 0 0 -2.3
            /bo rps translational semi-auto periodic-5* , 0 0 -2.3
            /bo rps translational semi-auto periodic-6-high , 0 0 -2.3
            /bo rps translational semi-auto periodic-7-high , 0 0 -2.3
            """,
    }
)

meshing.workflow.TaskObject["set-periodicity"].Execute()

#############################################################################
# Update Boundary Layer Task
# ==========================

meshing.workflow.TaskObject["Update Regions"].Execute()
meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
meshing.workflow.TaskObject["smooth-transition_1"].Rename(NewName=r"aspect-ratio_1")

meshing.workflow.TaskObject["aspect-ratio_1"].Arguments.setState(
    {
        "BLControlName": r"aspect-ratio_1",
        "BLRegionList": [
            r"fluid-tet-4",
            r"fluid-tet-3",
            r"fluid-tet-2",
            r"fluid-tet-1",
            r"fluid-sweep-fin2",
            r"fluid-sweep-fin1",
            r"fluid-sweep-fin5",
            r"fluid-sweep-fin3",
            r"fluid-sweep-fin6",
            r"fluid-sweep-fin4",
            r"fluid-in",
            r"fluid-out",
        ],
        r"BLZoneList": [
            r"wall-fluid-tet-4-solid-tet-4",
            r"wall-fluid-tet-3-solid-tet-3",
            r"wall-fluid-tet-2-solid-tet-2",
            r"wall-fluid-tet-2-solid-tet-2-wall-fluid-tet-3-solid-tet-3-fluid-tet-2-solid-tet-2",  # noqa: E501
            r"wall-fluid-tet-1-solid-tet-1",
            r"wall-fluid-sweep-fin-solid-sweep-fin.1",
            r"wall-fluid-sweep-fin-solid-sweep-fin",
            r"wall-fluid-sweep-fin-solid-sweep-fin.5",
            r"wall-fluid-sweep-fin-solid-sweep-fin.4",
            r"wall-fluid-sweep-fin-solid-sweep-fin.3",
            r"wall-fluid-sweep-fin-solid-sweep-fin.2",
        ],
        r"BlLabelList": r"wall*",
        r"CompleteBlLabelList": [
            r"wall-fluid-sweep-fin-solid-sweep-fin",
            r"wall-fluid-tet-1-solid-tet-1",
            r"wall-fluid-tet-2-solid-tet-2",
            r"wall-fluid-tet-3-solid-tet-3",
            r"wall-fluid-tet-4-solid-tet-4",
        ],
        r"FaceScope": {
            r"GrowOn": r"selected-labels",
        },
        r"OffsetMethodType": r"aspect-ratio",
    }
)

meshing.workflow.TaskObject["aspect-ratio_1"].Execute()

#############################################################################
# Generate Mesh
# =============

meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()

#############################################################################
# Improve Volume Mesh
# ===================

meshing.workflow.TaskObject["Generate the Volume Mesh"].InsertNextTask(
    CommandName=r"ImproveVolumeMesh"
)

meshing.workflow.TaskObject["Improve Volume Mesh"].Arguments.setState(
    {
        r"CellQualityLimit": 0.05,
        r"VMImprovePreferences": {
            r"ShowVMImprovePreferences": False,
            r"VIQualityIterations": 5,
            r"VIQualityMinAngle": 0,
            r"VIgnoreFeature": r"yes",
        },
    }
)

meshing.workflow.TaskObject["Improve Volume Mesh"].Execute()

#############################################################################
# Save Mesh File
# ==============

save_mesh_as = str(Path(pyfluent.EXAMPLES_PATH) / "hx-fin-2mm.msh.h5")
meshing.tui.file.write_mesh(save_mesh_as)

#############################################################################
# Switch to Solution Mode
# =======================

solver = meshing.switch_to_solver()

#############################################################################
# Auto-create Mesh Interfaces
# ===========================

solver.tui.define.mesh_interfaces.create("int", "yes", "no")

#############################################################################
# Mesh Check; Review Fluent transcript for errors
# ===============================================

solver.mesh.check()

#############################################################################
# Create a few boundary list for display and post-processing
# ==========================================================

graphics_session1 = Graphics(solver)
mesh1 = graphics_session1.Meshes["mesh-1"]

wall_list = []
periodic_list = []
symmetry_list = []

for item in mesh1.surfaces_list.allowed_values:
    if len(item.split("wall")) > 1:
        wall_list.append(item)
    if len(item.split("periodic")) > 1:
        periodic_list.append(item)
    if len(item.split("symmetry")) > 1:
        symmetry_list.append(item)

#############################################################################
# Display Mesh
# ============

mesh1.show_edges = True
mesh1.surfaces_list = wall_list
mesh1.display("window-1")

#%%
# .. image:: ../../_static/cht_mesh.png
#    :align: center
#    :alt: Mesh

#%%
#    Mesh

###############################################################################
# Temperature, Energy, Laminar Viscous Model
# ==========================================
# * Enable Energy Equation
# * Enable Laminar Viscous Model

solver.setup.models.energy.enabled = True
solver.setup.models.viscous.model = "laminar"

#############################################################################
# Change a few material properties of default Air
# ===============================================

air_matl = solver.setup.materials.fluid["air"]
air_matl.density.value = 1.2
air_matl.viscosity.value = 1.5e-5
air_matl.thermal_conductivity.value = 0.026
air_matl.specific_heat.value = 1006.0

#############################################################################
# Change a few material properties of default Aluminum
# ====================================================

al_matl = solver.setup.materials.solid["aluminum"]
al_matl.density.value = 2719.0
al_matl.thermal_conductivity.value = 200.0
al_matl.specific_heat.value = 871.0

#############################################################################
# Copy Copper and change a few material properties of default Copper
# ==================================================================

solver.setup.materials.database.copy_by_name(
    type="solid",
    name="copper",
)

cu_matl = solver.setup.materials.solid["copper"]
cu_matl.density.value = 8978.0
cu_matl.thermal_conductivity.value = 340.0
cu_matl.specific_heat.value = 381.0

#############################################################################
# Set Tube Cell Zone Material as Copper
# =====================================

solid_cellzone_conds = solver.setup.cell_zone_conditions.solid
solid_cellzone_conds["solid-tube-1"].material = "copper"
solid_cellzone_conds["solid-tube-2"].material = "copper"

#############################################################################
# Set Boundary Condition for Inlet and Outlet
# ===========================================

bc = solver.setup.boundary_conditions

bc.velocity_inlet["inlet"].momentum.velocity.value = 4.0
bc.velocity_inlet["inlet"].thermal.t.value = 293.15  # Need to specify in Kelvin

bc.pressure_outlet["outlet"].thermal.t0.value = 293.15

#############################################################################
# Set Thermal Boundary Condition for Wall Inner Tube
# ==================================================

inner_tube_bc = solver.setup.boundary_conditions.wall["wall-inner-tube-1"]
inner_tube_bc.thermal.thermal_bc = "Convection"
inner_tube_bc.thermal.h.value = 1050.0
inner_tube_bc.thermal.tinf.value = 353.15

solver.setup.boundary_conditions.copy(
    from_="wall-inner-tube-1",
    to="wall-inner-tube-2",
)

#############################################################################
# Enable HOTR
# ===========

solver.solution.methods.high_order_term_relaxation.enable = True

#############################################################################
# Define Report Definitions
# =========================

report_defs = solver.solution.report_definitions

report_defs.surface["outlet-enthalpy-flow"] = {
    "report_type": "surface-flowrate",
    "field": "enthalpy",
    "surface_names": ["outlet"],
}
report_defs.surface["avg-pressure-inlet"] = {
    "report_type": "surface-areaavg",
    "field": "pressure",
    "surface_names": ["inlet"],
}
report_defs.volume["max-vel-louvers4"] = {
    "report_type": "volume-max",
    "field": "velocity-magnitude",
    "cell_zones": ["fluid-tet-4"],
}
report_defs.surface["wall-shear-int"] = {
    "report_type": "surface-integral",
    "field": "wall-shear",
    "surface_names": [
        "wall-fluid-sweep-fin-solid-sweep-fin-shadow",
        "wall-fluid-tet-1-solid-tet-1",
        "wall-fluid-tet-2-solid-tet-2",
        "wall-fluid-tet-3-solid-tet-3",
        "wall-fluid-tet-4-solid-tet-4",
    ],
}

#############################################################################
# Define Report Plots
# ===================

report_plots = solver.solution.monitor.report_plots

report_plots["outlet-enthalpy-flow-plot"] = {
    "report_defs": ["outlet-enthalpy-flow"],
}
report_plots["avg-pressure-inlet-plot"] = {
    "report_defs": ["avg-pressure-inlet"],
}
report_plots["max-vel-louvers4-plot"] = {
    "report_defs": ["max-vel-louvers4"],
}
report_plots["wall-shear-int-plot"] = {
    "report_defs": ["wall-shear-int"],
}

#############################################################################
# Define Report Files
# ===================

report_files = solver.solution.monitor.report_files

report_files["outlet-enthalpy-flow-file"] = {
    "report_defs": ["outlet-enthalpy-flow"],
    "file_name": "outlet-enthalpy-flow.out",
}
report_files["avg-pressure-inlet-file"] = {
    "report_defs": ["avg-pressure-inlet"],
    "file_name": "avg-pressure-inlet.out",
}
report_files["max-vel-louvers4-file"] = {
    "report_defs": ["max-vel-louvers4"],
    "file_name": "max-vel-louvers4.out",
}
report_files["wall-shear-int-file"] = {
    "report_defs": ["wall-shear-int"],
    "file_name": "wall-shear-int.out",
}

#############################################################################
# Hybrid Initialization; Slit Interior between Solid Zones; Save Case
# ===================================================================

solver.solution.initialization.hybrid_initialize()
solver.setup.boundary_conditions.slit_interior_between_diff_solids()
save_case_as = Path(pyfluent.EXAMPLES_PATH) / "hx-fin-2mm.cas.h5"
solver.file.write_case(file_name=save_case_as)

#############################################################################
# Set Aggressive Length Scale Method; Run Calculation & Save Data
# ===============================================================

time_step_method = solver.solution.run_calculation.pseudo_time_settings.time_step_method

time_step_method.time_step_method = "automatic"
time_step_method.length_scale_methods = "aggressive"

solver.solution.run_calculation.iterate(iter_count=250)
solver.file.write_case_data(file_name=save_case_as)

#############################################################################
# Post-Processing Mass Balance Report
# ===================================

fluxes = solver.results.report.fluxes

inlet_mfr = fluxes.mass_flow(
    all_boundary_zones=False,
    zones=["inlet"],
    write_to_file=False,
)
outlet_mfr = fluxes.mass_flow(
    all_boundary_zones=False,
    zones=["outlet"],
    write_to_file=False,
)
net_mfr = fluxes.mass_flow(
    all_boundary_zones=False,
    zones=["inlet", "outlet"],
    write_to_file=False,
)

print("Mass Balance Report\n")
print("Inlet (kg/s): ", inlet_mfr)
print("Outlet (kg/s): ", outlet_mfr)
print("Net (kg/s): ", net_mfr)

#############################################################################
# Heat Balance Report
# ===================

htr = fluxes.heat_transfer(
    all_boundary_zones=True,
    write_to_file=False,
)

print("Heat Balance Report\n")
print("Net Imbalance (Watt): ", htr)

#############################################################################
# Plot Monitors
# =============

fig, axs = plt.subplots(2, 2, figsize=(10, 8))
fig.suptitle("Monitor Plots")

rFilesList = [
    "avg-pressure-inlet.out",
    "max-vel-louvers4.out",
    "outlet-enthalpy-flow.out",
    "wall-shear-int.out",
]

# Append current working directory to each filename
outFilesList = [save_path / fName for fName in rFilesList]

index = 0
for ax in axs.flat:
    X = []
    Y = []
    i = -1
    with open(outFilesList[index], "r") as datafile:
        plotting = csv.reader(datafile, delimiter=" ")
        for rows in plotting:
            i += 1
            if i == 1:
                var = rows[1]
            if i > 2:
                X.append(int(rows[0]))
                Y.append(float(rows[1]))

    ax.plot(X, Y)
    ax.set(xlabel="Iteration", ylabel=var, title=var)
    index += 1

plt.tight_layout()

#############################################################################
# Show graph
# ==========

plt.show()

#%%
# .. image:: ../../_static/cht_avg_pressure.png
#    :align: center
#    :alt: Average Pressure

#%%
#    Average Pressure

#############################################################################
# Contour Plot
# ============

graphics_session1 = Graphics(solver)
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "temperature"
contour1.surfaces_list = wall_list
contour1.display("window-2")

#%%
# .. image:: ../../_static/cht_temp_contour.png
#    :align: center
#    :alt: Temperature Contour

#%%
#    Temperature Contour

#############################################################################
# Create Iso-Surface of X=0.012826 m
# ==================================

solver.results.surfaces.iso_surface["x=0.012826"] = {
    "field": "x-coordinate",
    "iso_values": [0.012826],
}

#############################################################################
# Vector Plot
# ===========

graphics_session1 = Graphics(solver)
vector1 = graphics_session1.Vectors["vector-1"]
vector1.surfaces_list = ["x=0.012826"]
vector1.scale = 2.0
vector1.skip = 5
vector1.display("window-3")

#%%
# .. image:: ../../_static/cht_vector.png
#    :align: center
#    :alt: Vector Plot

#%%
#    Vector Plot

#############################################################################
# XY Plot of Pressure
# ===================

plots_session1 = Plots(solver)
p1 = plots_session1.XYPlots["p1"]
p1.surfaces_list = ["x=0.012826"]
p1.y_axis_function = "pressure"
p1.x_axis_function = "direction-vector"
p1.direction_vector.set_state([0, 1, 0])

#############################################################################
# Show graph
# ==========

p1.plot("p1")

#%%
# .. image:: ../../_static/cht_xy_pressure.png
#    :align: center
#    :alt: XY Plot of Pressure

#%%
#    XY Plot of Pressure

#############################################################################
# Exit Fluent Session
# ===================

solver.exit()
