# Ahmed Body Simulation using PyFluent
# This example demonstrate pyfluent api for Ahmed Body Simulation

# Import the pyfluent, std libraries etc
import ansys.fluent.core as pyfluent
from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="isometric")
# Launch the session

# session = pyfluent.launch_fluent(version='3d', precision='double',
# processor_count=6, meshing_mode=True)
session = pyfluent.launch_fluent(mode="meshing", show_gui=True)

"""
This api command used to connect live session of fluent on cluster or local
    To generate server_info-XXXX.txt file,
    Follow Fluent menubar File-->Applications-->Server-->Start

    copy paste this file to program directory and refer as follows
        session = pyfluent.Session('server_info-98073.txt')

"""
# session = pyfluent.Session('server_info-98073.txt')

# Check server status
session.check_health()

# Meshing
# This is meshing workflow using existing .wft file.
# session.tui.solver.switch_to_meshing_mode("Yes")
workflow = session.workflow
workflow.LoadWorkflow(FilePath="ahmed_standard_poly_boi.wft")
workflow.TaskObject["Import Geometry"].Execute()
workflow.TaskObject["Add Local Sizing"].Execute()
workflow.TaskObject["Generate the Surface Mesh"].Execute()
workflow.TaskObject["Improve Surface Mesh"].Execute()
workflow.TaskObject["Describe Geometry"].Execute()
workflow.TaskObject["Update Boundaries"].Execute()
workflow.TaskObject["Update Regions"].Execute()
workflow.TaskObject["Add Boundary Layers"].Execute()
workflow.TaskObject["Generate the Volume Mesh"].Execute()
workflow.TaskObject["Improve Volume Mesh"].Execute()
session = session.switch_to_solver()

# ### Solver Setup
# Enable parameters in TUI
session.tui.define.parameters.enable_in_TUI("yes")

# Define constants
density = 1.225
inlet_velocity = 30
inlet_area = 0.11203202

# Change create materials
session.tui.define.materials.change_create("air", "air", "yes", "constant", "density")
session.tui.define.models.viscous.ke_realizable("yes")
session.tui.define.models.viscous.curvature_correction("yes")

# These objects are also instances of ‘settings’ objects and
# roughly mirror the outline view in Fluent.
# Set velocity inlet boundary conditions
inlet = session.setup.boundary_conditions.velocity_inlet["inlet"]
inlet.turb_intensity = 0.05
inlet.vmag.value = inlet_velocity
inlet.turb_viscosity_ratio = 5

# Set velocity outlet boundary conditions
outlet = session.setup.boundary_conditions.pressure_outlet["outlet"]
outlet.turb_intensity = 0.05

# Set reference values
session.tui.report.reference_values.area(inlet_area)
session.tui.report.reference_values.density(density)
session.tui.report.reference_values.velocity(inlet_velocity)

# Set p_v_coupling
session.tui.solve.set.p_v_coupling(24)

# Set discretization scheme
session.tui.solve.set.discretization_scheme("pressure", 12)
session.tui.solve.set.discretization_scheme("k", 1)
session.tui.solve.set.discretization_scheme("epsilon", 1)
session.tui.solve.initialize.set_defaults("k", 0.000001)

# Define convergence criteria
session.tui.solve.monitors.residual.convergence_criteria(
    0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001
)

# session.tui.define.operating_conditions

# # Add report definitions
session.tui.solve.report_definitions.add(
    "cd-mon1",
    "drag",
    "thread-names",
    "*ahmed*",
    "()",
    "scaled?",
    "yes",
    "force-vector",
    "0 0 1",
    "q",
)

# Create output parameters
session.tui.define.parameters.output_parameters.create("report-definition", "cd-mon1")

# Add report plots
session.tui.solve.report_plots.add("cd-mon1", "report-defs", "cd-mon1", "()", "q")

# set number of iterations
session.tui.solve.set.number_of_iterations(3)  # 600

# Initialize solver workflow
session.tui.solve.initialize.initialize_flow()

# Start iterations
session.tui.solve.iterate()

# Post Processing

# mid-palne for post-processing
session.tui.surface.iso_surface("x-coordinate", "xmid", "()", "()", 0, "()")

try:
    import ansys.fluent.visualization.pyvista as pv
except ImportError:
    import ansys.fluent.post.pyvista as pv

# Plot - contour field - velocity-magnitude
graphics_session1 = pv.Graphics(session)
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "velocity-magnitude"
contour1.surfaces_list = ["xmid"]
contour1.display("window-1")

# Plot - contour field - pressure-coefficient
contour2 = graphics_session1.Contours["contour-2"]
contour2.field.allowed_values
contour1.field = "pressure-coefficient"
contour1.surfaces_list = ["xmid"]
contour1.display("window-2")

# Write and save the case file
session.tui.file.write_case_data("ahmed_body_final.cas.h5")

# End current session
session.exit()
