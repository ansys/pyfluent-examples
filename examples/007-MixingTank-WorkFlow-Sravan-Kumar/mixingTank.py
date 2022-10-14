"""
007-MixingTank-WorkFlow
=========================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

from pathlib import Path

# Stirred Tank: Fluent Meshing, Fluent Solver and Postprocessing
import ansys.fluent.core as pyfluent

# pyfluent.set_log_level("INFO")

# Fluent Meshing
session = pyfluent.launch_fluent(
    version="3d", precision="double", processor_count=6, mode="meshing"
)

# Check server status
session.check_health()

# Initialize Workflow
session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
session.workflow.TaskObject["Import Geometry"].Arguments = dict(
    FileName="StirredTank.scdoc"
)
session.workflow.TaskObject["Import Geometry"].Execute()
session.workflow.TaskObject["Generate the Surface Mesh"].Execute()
session.workflow.TaskObject["Describe Geometry"].Arguments = dict(
    SetupType="The geometry consists of only fluid regions with no voids",
    wall_to_internal="Yes",
)
session.workflow.TaskObject["Describe Geometry"].Execute()
session.workflow.TaskObject["Update Boundaries"].Execute()
session.workflow.TaskObject["Update Regions"].Execute()
session.workflow.TaskObject["Generate the Volume Mesh"].Execute()
session = session.switch_to_solver()

# Fluent Solver Setup
session.tui.define.operating_conditions.gravity("Yes", 0, 0, -9.81)
session.tui.define.parameters.enable_in_TUI("yes")

# Material with density and viscosity as input parameters
session.tui.define.materials.copy("fluid", "water-liquid")
session.tui.define.materials.change_create(
    "water-liquid",
    "water-liquid",
    "yes",
    "yes",
    "density",
    1000,
    "no",
    "no",
    "yes",
    "yes",
    "viscosity",
    0.001,
    "no",
    "no",
    "no",
)

# Solution Methods & Controls
session.tui.solve.set.p_v_coupling(20)
session.tui.solve.set.discretization_scheme("pressure", 14)
session.tui.solve.set.under_relaxation("pressure", 0.5)
session.tui.solve.set.under_relaxation("mom", 0.3)
session.tui.solve.set.under_relaxation("k", 0.6)
session.tui.solve.set.under_relaxation("omega", 0.6)
session.tui.solve.set.under_relaxation("turb-viscosity", 0.6)

# Initialization Settings & Residual Criteria
session.tui.solve.initialize.reference_frame("absolute")
session.tui.solve.initialize.set_defaults("k", 0.001)
session.tui.solve.monitors.residual.convergence_criteria(
    0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001
)

# Setup MRF with agitation speed as parameter
session.tui.define.boundary_conditions.set.fluid(
    ["fluid_mrf*"],
    "mrf-motion?",
    "yes",
    "mrf-ak",
    "no",
    "no",
    -1,
    "mrf-omega",
    "yes",
    "agitation_speed",
    10,
    "material",
    "yes",
    "water-liquid",
    "q",
)
session.tui.define.boundary_conditions.set.fluid(
    "fluid_tank", "()", "material", "yes", "water-liquid", "q"
)
session.tui.define.boundary_conditions.set.wall(
    ["wall_shaft*"],
    "motion-bc",
    "yes",
    "motion-bc-moving",
    "relative?",
    "no",
    "rotating",
    "yes",
    "ak",
    "no",
    -1,
    "omega",
    "yes",
    "yes",
    "agitation_speed",
    "q",
)
session.tui.define.boundary_conditions.set.wall(
    "wall_liquid_level", "()", "shear-bc", "yes", "shear-bc-spec-shear", "q"
)

# Report Definitions
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
session.tui.solve.report_definitions.add(
    "torque", "moment", "thread-names", "wall_impeller*", "()", "scaled?", "no", "q"
)
session.tui.solve.report_plots.add("torque", "report-defs", "torque", "()", "q")
session.tui.solve.report_plots.add(
    "vol-avg-vel", "report-defs", "vol-avg-vel", "()", "q"
)
session.tui.solve.report_files.add(
    "torque", "report-defs", "torque", "()", "file-name", "torque.out", "q"
)
session.tui.solve.report_files.add(
    "vol-avg-vel",
    "report-defs",
    "vol-avg-vel",
    "()",
    "file-name",
    "vol-avg-vel.out",
    "q",
)
session.tui.solve.report_definitions.add(
    "average-dissipation-rate",
    "volume-average",
    "field",
    "turb-diss-rate",
    "zone-names",
    "fluid*",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "maximum-dissipation-rate",
    "volume-max",
    "field",
    "turb-diss-rate",
    "zone-names",
    "fluid*",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "average-strain-rate",
    "volume-average",
    "field",
    "strain-rate",
    "zone-names",
    "fluid*",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "maximum-strain-rate",
    "volume-max",
    "field",
    "strain-rate",
    "zone-names",
    "fluid*",
    "()",
    "q",
)
session.tui.solve.report_definitions.add(
    "fluid-volume", "volume-zonevol", "zone-names", "fluid*", "()", "q"
)

# Creating Output Parameters
session.tui.define.parameters.output_parameters.create("report-definition", "torque")
session.tui.define.parameters.output_parameters.create(
    "report-definition", "fluid-volume"
)
session.tui.define.parameters.output_parameters.create(
    "report-definition", "average-dissipation-rate"
)
session.tui.define.parameters.output_parameters.create(
    "report-definition", "maximum-dissipation-rate"
)
session.tui.define.parameters.output_parameters.create(
    "report-definition", "average-strain-rate"
)
session.tui.define.parameters.output_parameters.create(
    "report-definition", "maximum-strain-rate"
)


# Run Settings
# Initialize workflow and set itertaions
session.tui.solve.set.number_of_iterations(50)  # 500
session.tui.solve.initialize.initialize_flow()
session.tui.solve.iterate()


# Postprocessing

# Define iso surface
session.tui.surface.iso_surface("y-coordinate", "ymid", "()", "()", 0, "()")


# Add contour properties
session.results.graphics.contour["contour-1"] = {}
session.results.graphics.contour["contour-1"].surfaces_list = ["ymid"]
session.results.graphics.contour["contour-1"].surfaces_list()
session.results.graphics.contour["contour-1"].field = "velocity-magnitude"

# Display and save contour
session.tui.display.objects.display("contour-1")
session.tui.display.views.restore_view("top")
session.tui.display.views.auto_scale()
session.tui.display.set.picture.use_window_resolution("no")
session.tui.display.set.picture.x_resolution(600)
session.tui.display.set.picture.y_resolution(600)
session.tui.display.save_picture("vel-contour.png")

# Velocity Contour on Mid Plane

# Postprocessing with PyVista
# import ansys.fluent.post.pyvista as pv
# graphics_session1 = pv.Graphics(session)
# contour1 = graphics_session1.Contours["contour-1"]
# contour1.field = "velocity-magnitude"
# contour1.surfaces_list = ['ymid']
# contour1.display()

# Write and save case data
save_case_as = str(Path(pyfluent.EXAMPLES_PATH) / "final.cas.h5")
session.tui.file.write_case_data(save_case_as)


import csv

# Plotting the saved monitors using matplotlib
import matplotlib.pyplot as plt

X = []
Y = []
i = -1
with open("vol-avg-vel.out", "r") as datafile:
    plotting = csv.reader(datafile, delimiter=" ")
    for rows in plotting:
        i = i + 1
        if i > 2:
            X.append(int(rows[0]))
            Y.append(float(rows[1]))
    plt.plot(X, Y)
    plt.title("Average Velocity Monitor")
    plt.xlabel("Iterations")
    plt.ylabel("Average Velocity (m/s)")
    # plt.show()

# End current session
# session.exit()
