# Import Python Packages
# get_ipython().run_line_magic('matplotlib', 'notebook')
from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="isometric")

import csv  # noqa: F401
import os

import ansys.fluent.core as pyfluent

# from ansys.fluent.visualization.matplotlib import Plots, matplot_windows_manager
from ansys.fluent.visualization.pyvista import (  # noqa: F401
    Graphics,
    pyvista_windows_manager,
)
from ansys.fluent.visualization.pyvista.pyvista_windows_manager import (  # noqa: F401
    PyVistaWindow,
)
import matplotlib.pyplot as plt  # noqa: F401
import pyvista as pv  # noqa: F401

# PyFluent Core Version
pyfluent.__version__

# PyFluent Visualization Version
import ansys.fluent.visualization as viz

viz.__version__

# Streaming of Transcript to this Notebook
pyfluent.set_log_level("INFO")

# Set Working Directory; Launch Fluent on 4 Cores; Meshing Mode

# workDir = r"D:\ExamplesNew\Examples\020 CHT - Shitanshu Gohel"

geomName = "cht_fin_htc_new.scdoc"

geomFilePath = os.path.join(os.getcwd(), geomName)

os.chdir(os.path.join(os.getcwd()))

session = pyfluent.launch_fluent(mode="meshing", processor_count=4, show_gui=False)

# PyFluent Session Health
session.check_health()

# Start Watertight Geometry Meshing Workflow
# Read Geometry File; Create Surface Mesh; Describe Geometry
session.workflow.InitializeWorkflow(WorkflowType=r"Watertight Geometry")

session.workflow.TaskObject["Import Geometry"].Arguments.update_dict(
    {"FileName": geomFilePath}
)
session.workflow.TaskObject["Import Geometry"].Execute()

session.workflow.TaskObject["Add Local Sizing"].Execute()

session.workflow.TaskObject["Generate the Surface Mesh"].Arguments.update_dict(
    {
        "CFDSurfaceMeshControls": {
            "MinSize": 0.3,
            "MaxSize": 1,
            "ScopeProximityTo": "faces",
        },
    }
)
session.workflow.TaskObject["Generate the Surface Mesh"].Execute()

session.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)
session.workflow.TaskObject["Describe Geometry"].Arguments.setState(
    {
        r"CappingRequired": r"No",
        r"InvokeShareTopology": r"No",
        r"NonConformal": r"Yes",
        r"SetupType": r"The geometry consists of both fluid and solid regions and/or voids",  # noqa: E501
    }
)

session.workflow.TaskObject["Describe Geometry"].Execute()

# Update Interface Boundaries; Create Region
session.workflow.TaskObject["Update Boundaries"].Arguments.setState(
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

session.workflow.TaskObject["Update Boundaries"].Execute()

session.workflow.TaskObject["Create Regions"].Execute()

# Custom Journal for Creating Periodicity due to Non-Conformal Objects
session.workflow.TaskObject["Describe Geometry"].InsertNextTask(
    CommandName=r"RunCustomJournal"
)
session.workflow.TaskObject["Run Custom Journal"].Rename(NewName=r"set-periodicity")
session.workflow.TaskObject["set-periodicity"].Arguments.update_dict(
    {
        r"JournalString": r"""/bo rps translational semi-auto
            periodic-1-high periodic-2-high
            periodic-3-high periodic-4-high , 0 0 -2.3
/bo rps translational semi-auto periodic-5* , 0 0 -2.3
/bo rps translational semi-auto periodic-6-high , 0 0 -2.3
/bo rps translational semi-auto periodic-7-high , 0 0 -2.3
""",
    }
)

session.workflow.TaskObject["set-periodicity"].Execute()

# Update Boundary Layer Task
session.workflow.TaskObject["Update Regions"].Execute()
session.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
session.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
session.workflow.TaskObject["smooth-transition_1"].Rename(NewName=r"aspect-ratio_1")

session.workflow.TaskObject["aspect-ratio_1"].Arguments.setState(
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

session.workflow.TaskObject["aspect-ratio_1"].Execute()

# Generate Mesh
session.workflow.TaskObject["Generate the Volume Mesh"].Execute()

# Improve Volume Mesh
session.workflow.TaskObject["Generate the Volume Mesh"].InsertNextTask(
    CommandName=r"ImproveVolumeMesh"
)

session.workflow.TaskObject["Improve Volume Mesh"].Arguments.setState(
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

session.workflow.TaskObject["Improve Volume Mesh"].Execute()

# Save Mesh File
session.tui.file.write_mesh("hx-fin-2mm.msh.h5")

# Switch to Solution / solver Mode
session = session.switch_to_solver()

# If starting from a Mesh File
# caseName = 'hx-fin-2mm.msh.h5'
# caseFilePath = os.path.join(os.getcwd(), caseName)
# session.solver.tui.file.read_case(case_file_name=caseFilePath)

# Auto-create Mesh Interfaces
session.tui.define.mesh_interfaces.create("int", "yes", "no")

# Mesh Check; Review Fluent transcript for errors
session.tui.mesh.check()

# Create a few boundary list for display and post-processing
graphics_session1 = Graphics(session)
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

# # Display Mesh
# mesh1.show_edges = True
# mesh1.surfaces_list = wall_list
# # mesh1.display("window-1")
# p = pyvista_windows_manager.get_plotter("window-1")
# p.view_isometric()
# p.add_axes()
# p.add_floor(offset=1, show_edges=False)
# light = pv.Light(light_type="headlight")
# p.add_light(light)

# Set Temperature Unit; Enable Energy Equation; Enable Laminar Viscous Model
session.tui.define.units("temperature", "C")
session.setup.models.energy.enabled = True
session.setup.models.viscous.model.set_state("laminar")

# Change a few material properties of default Air
air_dict = session.setup.materials.fluid["air"].get_state()
air_dict["density"]["value"] = 1.2
air_dict["viscosity"]["value"] = 1.5e-5
air_dict["thermal_conductivity"]["value"] = 0.026
air_dict["specific_heat"]["value"] = 1006.0
session.setup.materials.fluid["air"].set_state(air_dict)

# Change a few material properties of default Aluminum
al_dict = session.setup.materials.solid["aluminum"].get_state()
al_dict["density"]["value"] = 2719.0
al_dict["thermal_conductivity"]["value"] = 200.0
al_dict["specific_heat"]["value"] = 871.0
session.setup.materials.solid["aluminum"].set_state(al_dict)

# Copy Copper and change a few material properties
session.tui.define.materials.copy("solid", "copper")
cu_dict = session.setup.materials.solid["copper"].get_state()
cu_dict["density"]["value"] = 8978.0
cu_dict["thermal_conductivity"]["value"] = 340.0
cu_dict["specific_heat"]["value"] = 381.0
session.setup.materials.solid["copper"].set_state(cu_dict)

# Set Tube Cell Zone Material as Copper
tube_dict = session.setup.cell_zone_conditions.solid["solid-tube-1"].get_state()
tube_dict["material"] = "copper"
session.setup.cell_zone_conditions.solid["solid-tube-1"].set_state(tube_dict)

tube_dict = session.setup.cell_zone_conditions.solid["solid-tube-2"].get_state()
tube_dict["material"] = "copper"
session.setup.cell_zone_conditions.solid["solid-tube-2"].set_state(tube_dict)

# Set Boundary Condition for Inlet and Outlet
inlet_dict = session.setup.boundary_conditions.velocity_inlet["inlet"].get_state()
inlet_dict["vmag"]["value"] = 4.0
inlet_dict["t"]["value"] = 293.15  # Need to specify in Kelvin
session.setup.boundary_conditions.velocity_inlet["inlet"].set_state(inlet_dict)

outlet_dict = session.setup.boundary_conditions.pressure_outlet["outlet"].get_state()
outlet_dict["t0"]["value"] = 293.15
session.setup.boundary_conditions.pressure_outlet["outlet"].set_state(outlet_dict)

# Set Thermal Boundary Condition for Wall Inner Tube
wall_dict = session.setup.boundary_conditions.wall["wall-inner-tube-1"].get_state()
wall_dict["thermal_bc"] = "Convection"
# This step is necessary as 'h' is not available in Adiabatic Dictionary
session.setup.boundary_conditions.wall["wall-inner-tube-1"].set_state(wall_dict)

wall_dict = session.setup.boundary_conditions.wall["wall-inner-tube-1"].get_state()
wall_dict["h"]["value"] = 1050.0
wall_dict["tinf"]["value"] = 353.15
session.setup.boundary_conditions.wall["wall-inner-tube-1"].set_state(wall_dict)

session.tui.define.boundary_conditions.copy_bc(
    "wall-inner-tube-1", "wall-inner-tube-2", "()"
)

# Enable HOTR
session.solution.methods.high_order_term_relaxation.enable = True

# Define Report Definitions
session.tui.solve.report_definitions.add(
    "outlet-enthalpy-flow",
    "surface-flowrate",
    "field",
    "enthalpy",
    "surface-names",
    "outlet",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "avg-pressure-inlet",
    "surface-areaavg",
    "field",
    "pressure",
    "surface-names",
    "inlet",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "max-vel-louvers4",
    "volume-max",
    "field",
    "velocity-magnitude",
    "zone-names",
    "fluid-tet-4",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "wall-shear-int",
    "surface-integral",
    "field",
    "wall-shear",
    "surface-names",
    "wall-fluid-sweep-fin-solid-sweep-fin-shadow",
    "wall-fluid-tet-1-solid-tet-1",
    "wall-fluid-tet-2-solid-tet-2",
    "wall-fluid-tet-3-solid-tet-3",
    "wall-fluid-tet-4-solid-tet-4",
    "()",
    "q",
)

session.tui.solve.report_plots.add(
    "outlet-enthalpy-flow-plot", "report-defs", "outlet-enthalpy-flow", "()", "q"
)
session.tui.solve.report_files.add(
    "outlet-enthalpy-flow-file",
    "report-defs",
    "outlet-enthalpy-flow",
    "()",
    "file-name",
    "outlet-enthalpy-flow.out",
    "q",
)

session.tui.solve.report_plots.add(
    "avg-pressure-inlet-plot", "report-defs", "avg-pressure-inlet", "()", "q"
)
session.tui.solve.report_files.add(
    "avg-pressure-inlet-file",
    "report-defs",
    "avg-pressure-inlet",
    "()",
    "file-name",
    "avg-pressure-inlet.out",
    "q",
)

session.tui.solve.report_plots.add(
    "max-vel-louvers4-plot", "report-defs", "max-vel-louvers4", "()", "q"
)
session.tui.solve.report_files.add(
    "max-vel-louvers4-file",
    "report-defs",
    "max-vel-louvers4",
    "()",
    "file-name",
    "max-vel-louvers4.out",
    "q",
)

session.tui.solve.report_plots.add(
    "wall-shear-int-plot", "report-defs", "wall-shear-int", "()", "q"
)
session.tui.solve.report_files.add(
    "wall-shear-int-file",
    "report-defs",
    "wall-shear-int",
    "()",
    "file-name",
    "wall-shear-int.out",
    "q",
)

# Hybrid Initialization; Slit Interior between Solid Zones; Save Case
session.tui.solve.initialize.hyb_initialization()
session.tui.mesh.modify_zones.slit_interior_between_diff_solids()
session.tui.file.write_case("hx-fin-2mm.cas.h5")
session.tui.solve.initialize.hyb_initialization()

# Set Aggressive Length Scale Method; Run Calculation & Save Data
session.tui.solve.set.pseudo_time_method.global_time_step_settings(
    "yes", "0", "1", "yes", "1"
)
session.tui.solve.iterate(10)  # 250
session.tui.file.write_case_data("hx-fin-2mm.dat.h5")

# Post-Processing
# dataName = 'hx-fin-2mm.dat.h5'
# session.solver.tui.file.read_case_data(dataName)

# Mass Balance Report
inlet_mfr = session.scheme_eval.exec(
    ('(ti-menu-load-string "/report/fluxes/mass-flow no inlet () no")',)
).split(" ")[-1]
outlet_mfr = session.scheme_eval.exec(
    ('(ti-menu-load-string "/report/fluxes/mass-flow no outlet () no")',)
).split(" ")[-1]
net_mfr = session.scheme_eval.exec(
    ('(ti-menu-load-string "/report/fluxes/mass-flow no inlet outlet () no")',)
).split(" ")[-1]
print("Mass Balance Report\n")
print("Inlet (kg/s): ", inlet_mfr)
print("Outlet (kg/s): ", outlet_mfr)
print("Net (kg/s): ", net_mfr)

# Heat Balance Report
htr = session.scheme_eval.exec(
    ('(ti-menu-load-string "/report/fluxes/heat-transfer yes no")',)
).split(" ")[-1]
print("Heat Balance Report\n")
print("Net Imbalance (Watt): ", htr)

# # Plot Monitors
# fig, axs = plt.subplots(2, 2, figsize=(10, 8))
# fig.suptitle("Monitor Plots")
#
# outFilesList = []
# fileList = os.listdir(os.getcwd())
# for tempFile in fileList:
#     fName, ext = os.path.splitext(tempFile)
#     if ext == ".out":
#         outFilesList.append(tempFile)
# outFilesList.sort()

# index = 0
# for ax in axs.flat:
#     X = []
#     Y = []
#     i = -1
#     with open(outFilesList[index], "r") as datafile:
#         plotting = csv.reader(datafile, delimiter=" ")
#         for rows in plotting:
#             i += 1
#             if i == 1:
#                 var = rows[1]
#             if i > 2:
#                 X.append(int(rows[0]))
#                 Y.append(float(rows[1]))
#
#     ax.plot(X, Y)
#     ax.set(xlabel="Iteration", ylabel=var, title=var)
#     index += 1
#
# plt.tight_layout()
# plt.show()

# # Contour Plot
# graphics_session1 = Graphics(session)
# contour1 = graphics_session1.Contours["contour-1"]
# contour1.field = "temperature"
# contour1.surfaces_list = wall_list
# # contour1.display("window-2")
#
# p = pyvista_windows_manager.get_plotter("window-2")
# p.view_isometric()
# p.add_axes()
# p.add_floor(offset=1, show_edges=False)
# p.add_title(
#     "Contour of Temperature on Walls", font="courier", color="grey", font_size=10
# )
# light = pv.Light(light_type="headlight")
# p.add_light(light)
#
# p.remove_scalar_bar()
# p.add_scalar_bar(
#     "Temperature [K]",
#     interactive=True,
#     vertical=False,
#     title_font_size=20,
#     label_font_size=15,
#     outline=False,
#     position_x=0.5,
#     fmt="%10.1f",
# )
# pyvista_windows_manager.save_graphic("window-2", "svg" )

# Create Iso-Surface of X=0.012826 m
session.tui.surface.iso_surface(
    "x-coordinate", "x=0.012826", "()", "()", "0.012826", "()"
)

# # Vecotor Plot
# vector1 = graphics_session1.Vectors["vector-1"]
# vector1.surfaces_list = ["x=0.012826"]
# # vector1.surfaces_list  = symmetry_list
# vector1.scale = 2.0
# vector1.skip = 5
# # vector1.display("window-3")
#
# p = pyvista_windows_manager.get_plotter("window-3")
# p.view_isometric()
# p.add_axes()
# # p.add_floor( offset=1, show_edges=False)
# p.add_title("Vector Plot", font="courier", color="grey", font_size=10)
# light = pv.Light(light_type="headlight")
# p.add_light(light)

# p.remove_scalar_bar()
# p.add_scalar_bar(
#     "Velocity [m/s]",
#     interactive=True,
#     vertical=False,
#     title_font_size=20,
#     label_font_size=15,
#     outline=False,
#     position_x=0.5,
#     fmt="%10.1f",
# )
#
# PyVistaWindow(None, None)._display_mesh(mesh1, p)
#
# # XY Plot of Pressure
# plots_session1 = Plots(session)
# p1 = plots_session1.XYPlots["p1"]
# p1.surfaces_list = ["x=0.012826"]
# p1.y_axis_function = "pressure"
# p1.x_axis_function = "direction-vector"
# p1.direction_vector.set_state([0, 1, 0])
# p1.plot("p1")

# Exit Fluent Session
session.exit()
