"""
Simulation Examples
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Start by importing PyFluent

import ansys.fluent.core as fluent
from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="isometric")

# Find out what's available

dir(fluent)

dir_filtered = lambda obj: list(
    filter(lambda entry: not entry.startswith("_"), dir(obj))
)

dir_filtered(fluent)

# Check the version

fluent.version_info

fluent.version_info()

# Set the log level for all PyFluent

# help(fluent.set_log_level)

fluent.set_log_level("DEBUG")

# Find out about launch_fluent and call it
from ansys.fluent.core import launch_fluent

# help(launch_fluent)

session = launch_fluent()

# Run a health check on the Fluent connection
session.check_health()

# Exit the first session
# session.exit()

# Run another health check after exiting
session.check_health()

# Revert log level to the default
fluent.set_log_level("ERROR")

dir_filtered(session)

# help(session)

# # More about the structure of session objects
# ```
# session
# │
# └───meshing
# │   │
# │   └───meshing
# │   │
# │   └───workflow
# │   │
# │   └───PartManagement
# │   │
# │   └───tui
# │
# └───solver
#     │
#     └───root
#     │
#     └───tui
# ```

# Find out about the solver object
# help(session.solver)

# Launch fluent in meshing mode
meshing_session = launch_fluent(meshing_mode=True)

# help(meshing_session)

meshing = meshing_session.meshing

dir_filtered(meshing)

# help(meshing)

# Use the workflow object for task-based meshing
workflow = meshing.workflow

assert workflow is meshing_session.meshing.workflow

# help(workflow)

dir_filtered(workflow)

# Initialize the workflow

# help(workflow.InitializeWorkflow)

workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

# Look at the workflow tasks

# tasks = workflow.TaskObject

# task_list = [task for task in tasks]

# len(task_list)

# dir_filtered(task_list[0])

# task_names = [task._name_() for task in tasks]

# task_names

# task_name_iter = iter(task_names)

# task_name = next(task_name_iter)

# task_name

# Import the geometry

import_geometry = workflow.TaskObject["Import Geometry"]

import_geometry.State()

import_geometry.State.getAttribValue("allowedValues")

import_geometry.help()

import_geometry()

import_geometry.Arguments.update_dict(
    {"FileName": "demo_geometry.scdoc.pmdb", "AppendMesh": False}
)

import_geometry.Execute()

import_geometry.State()

# Add local sizing

# task_name = next(task_name_iter)

# task_name

add_local_sizing = workflow.TaskObject["Add Local Sizing"]

add_local_sizing.help()

dir_filtered(add_local_sizing)

add_local_sizing.Arguments = {
    "AddChild": "yes",
    "BOIControlName": "face",
    "BOIExecution": "Body Size",
    "BOIFaceLabelList": "farfield",
    "BOIZoneorLabel": "label",
}

add_local_sizing.Execute()

add_local_sizing.InsertCompoundChildTask()

add_local_sizing.Arguments.update_dict({"AddChild": "yes"})

face = workflow.TaskObject["face"]

face.Arguments.update_dict(
    {
        "AddChild": "yes",
        "BOIControlName": "refinementzone",
        "BOIExecution": "Body Size",
        "BOIFaceLabelList": "meshrefinement",
        "BOISize": 60,
    }
)

# Generate the surface mesh
generate_surface_mesh = workflow.TaskObject["Generate the Surface Mesh"]
status = generate_surface_mesh.Execute()

# Describe geometry
describe_geometry = workflow.TaskObject["Describe Geometry"]
describe_geometry.Arguments.updateDict(
    {
        "CappingRequired": "No",
        "InvokeShareTopology": "No",
        "SetupInternalTypes": None,
        "SetupInternals": None,
        "SetupType": "The geometry consists of both fluid and solid regions and/or voids",  # noqa: E501
        "WallToInternal": "Yes",
    }
)
describe_geometry.Execute()

# Create and update regions
create_regions = workflow.TaskObject["Create Regions"]
create_regions.Arguments.updateDict({"NumberOfFlowVolumes": 2})
create_regions.Execute(create_regions)
update_regions = workflow.TaskObject["Update Regions"]
update_regions.Execute()

# Update boundaries
workflow.TaskObject["Update Boundaries"].Execute()

# Add boundary layers
add_boundary_layers = workflow.TaskObject["Add Boundary Layers"]
add_boundary_layers.AddChildToTask()
add_boundary_layers.InsertCompoundChildTask()
workflow.TaskObject["smooth-transition_1"].Arguments.update_dict(
    {
        "BLControlName": "smooth-transition_1",
        "NumberOfLayers": 10,
        "OffsetMethodType": "smooth-transition",
        "TransitionRatio": 0.272,
    }
)
add_boundary_layers.Execute()

# Generate the volume mesh
generate_volume_mesh = workflow.TaskObject["Generate the Volume Mesh"]
generate_volume_mesh.Arguments.update_dict({"VolumeFill": "polyhedra"})
generate_volume_mesh.Execute()

# Write case and exit meshing session
case_file = "demo.cas"

# help(meshing_session.meshing.tui.file.write_case)

meshing_session.meshing.tui.file.write_case(case_file)

# End meshing session
# meshing_session.exit()

# Launch fluent in solvution mode
solver_session = launch_fluent()

# Access the underlying solver API objects
solver = solver_session.solver.root
tui = solver_session.solver.tui

# Access the file object and read case

dir_filtered(solver.file)

# help(solver.file.read)

solver.file.read_case(file_name="demo.cas.h5")

# Assign air density two ways

# TUI API

density = 1.1

tui.define.materials.change_create("air", "air", "yes", "constant", density)

# Solver settings API

dir_filtered(solver.setup.materials)

dir_filtered(solver.setup.materials.fluid)

print(len(solver.setup.materials.fluid.items()))

print(solver.setup.materials.fluid.items())

dir_filtered(solver.setup.materials.fluid["air"])

solver.setup.materials.fluid["air"].density

solver.setup.materials.fluid["air"].density()

solver.setup.materials.fluid["air"].density.get_state()

density = 1.25

solver.setup.materials.fluid["air"].density = {"option": "constant", "value": density}

solver.setup.materials.fluid["air"].density()

solver.setup.materials.fluid["air"]()

# Set up turbulence model

solver.setup.models.viscous

# help(solver.setup.models.viscous)

# help(solver.setup.models.viscous.model)

dir_filtered(solver.setup.models.viscous.model)

solver.setup.models.viscous.model.get_attr("allowed-values")

solver.setup.models.viscous.model()

dir_filtered(solver.solution)

dir_filtered(solver.solution.methods)

# Observe effects of changing turbulence model

dir_filtered(solver.solution.methods.discretization_scheme)

solver.solution.methods.discretization_scheme()

solver.setup.models.viscous.model = "k-epsilon"

solver.solution.methods.discretization_scheme()

solver.setup.models.viscous.model()

# Set up boundary conditions
inlet_velocity = 41.67
hydraulic_diameter = 1.25
reynolds = (density * inlet_velocity * hydraulic_diameter) / 1.7894e-5
turb_intensity = 0.16 * pow(reynolds, -0.125)
inlet = solver.setup.boundary_conditions.velocity_inlet["velocityinlet"]
inlet.turb_intensity = turb_intensity
inlet.vmag.value = inlet_velocity

outlet = solver.setup.boundary_conditions.pressure_outlet["pressureoutlet"]
outlet.turb_intensity = turb_intensity

outlet.turb_intensity()

inlet.vmag.value()

# Observe effects
energy_is_active = solver.setup.models.energy.enabled()

energy_is_active

"t" in inlet()

solver.setup.models.energy.enabled = True

"t" in inlet()

solver.setup.models.energy.enabled = False

# Set report reference values
unit_length = 0.001
unit_width = 0.001
tui.report.reference_values.area(unit_length * unit_width)
tui.report.reference_values.density(density)
tui.report.reference_values.velocity(inlet_velocity)
tui.report.reference_values.zone("farfield")

# # Set discretization scheme two ways

solver.solution.methods.discretization_scheme()

tui.solve.set.discretization_scheme("k", 1)
tui.solve.set.discretization_scheme("epsilon", 1)

solver.solution.methods.discretization_scheme()

tui.solve.set.discretization_scheme("epsilon", 4)

solver.solution.methods.discretization_scheme()

solver.solution.methods.discretization_scheme = {
    "k": "second-order-upwind",
    "mom": "second-order-upwind",
    "pressure": "second-order",
    "epsilon": "second-order-upwind",
}

solver.solution.methods.discretization_scheme()

# Set up report definition

dir(solver.solution.report_definitions)

dir(solver.solution.report_definitions.drag)

# help(solver.solution.report_definitions.drag.create)

solver.solution.report_definitions()

solver.solution.report_definitions.lift.create(name="drag_unit_lift")

solver.solution.report_definitions()

drag_unit_lift = solver.solution.report_definitions.lift["drag_unit_lift"]

drag_unit_lift.set_state(
    {
        "scaled": False,
        "average_over": 1,
        "per_zone": False,
        "thread_names": ["wallunit"],
        "force_vector": [0, 1, 0],
    }
)

drag_unit_lift()

# Initialize

dir(solver.solution)

dir(solver.solution.initialization)

# help(solver.solution.initialization.hybrid_initialize)

solver.solution.initialization.hybrid_initialize()

# Solve
tui.solve.iterate

# help(tui.solve.iterate)

dir(solver.solution.run_calculation)

# help(solver.solution.run_calculation.iterate)

# Set and start iterations
solver.solution.run_calculation.iterate(iter_count=10)

# Toggle transcript
solver_session.stop_transcript()

# Set and start iterations
solver.solution.run_calculation.iterate(iter_count=10)

solver_session.start_transcript()

# Set and start iterations
solver.solution.run_calculation.iterate(iter_count=10)

# Compute report definition and exit the session
results_dict = solver.solution.report_definitions.compute(
    report_defs=["drag_unit_lift"]
)

results_dict

# End solver session
# solver_session.exit()

# Launch another solver
new_solver_session = launch_fluent()

solver = new_solver_session.solver.root

case_file = "elbow1.cas"

# Read case file
solver.file.read_case(file_name=case_file)

# Initialize iterations
solver.solution.initialization.hybrid_initialize()

# Set and start iterations
solver.solution.run_calculation.iterate(iter_count=50)

# Import the required visualization modules
try:
    import ansys.fluent.visualization.matplotlib as plt
    from ansys.fluent.visualization.matplotlib import Plots, matplot_windows_manager
    import ansys.fluent.visualization.pyvista as pv
    from ansys.fluent.visualization.pyvista import Graphics, pyvista_windows_manager
except ImportError:
    import ansys.fluent.post.matplotlib as plt  # noqa: F401
    from ansys.fluent.post.matplotlib import (  # noqa: F401
        Plots,
        matplot_windows_manager,
    )
    import ansys.fluent.post.pyvista as pv
    from ansys.fluent.post.pyvista import (  # noqa: F401
        Graphics,
        pyvista_windows_manager,
    )

# Instantiate graphics and plots objects - with the session as context
graphics_session1 = pv.Graphics(new_solver_session)
xyplots_session1 = Plots(new_solver_session)

# Instantiate some contours, list them and
# get the state of one contour
contour1 = graphics_session1.Contours["contour-1"]
contour2 = graphics_session1.Contours["contour-2"]
contour3 = graphics_session1.Contours["contour-3"]

list(graphics_session1.Contours)

contour1()

contour1(True)

# Find out what's allowed
contour1.surfaces_list.allowed_values
contour1.field.allowed_values

# Set up and display the contour
contour1.field = "temperature"
contour1.surfaces_list = ["symmetry"]
contour1.display("plotter-1")

# Set up and display more objects
# Iso surface
surface1 = graphics_session1.Surfaces["surface-1"]
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.3
# surface1.display("plotter-2")

# Mesh
mesh1 = graphics_session1.Meshes["mesh-1"]
mesh1.show_edges = True
mesh1.surfaces_list = ["symmetry", "wall"]
mesh1.display("plotter-3")

# Vectors
vector1 = graphics_session1.Vectors["vector-1"]
vector1.surfaces_list = ["symmetry"]
vector1.scale = 4.0
vector1.skip = 4
vector1.display("plotter-4")

# Display an x-y plot
# get_ipython().run_line_magic('matplotlib', 'notebook')
plots_session1 = Plots(new_solver_session)

# Create a plot object
p1 = plots_session1.XYPlots["p1"]

# Surface list
p1.surfaces_list.allowed_values

# Plot velocity magnitude
p1 = plots_session1.XYPlots["p1"]
p1.surfaces_list = ["z=0_out"]
p1.y_axis_function = "velocity-magnitude"
p1.plot("p1")

# Exit new solver_ession
# new_solver_session.exit()
