"""
Ablation-tutorial
=================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

from pathlib import Path

# Import modules
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

###############################################################################
# Specifying save path
# ~~~~~~~~~~~~~~~~~~~~
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.
save_path = Path(pyfluent.EXAMPLES_PATH)

# Download example file
import_filename = examples.download_file(
    "ablation.msh.h5", "pyfluent/examples/Ablation-tutorial", save_path=save_path
)

from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="isometric")

# Launch fluent
session = pyfluent.launch_fluent(version="3d", precision="double", processor_count=4)

# Read Mesh
session.tui.file.read_case(import_filename)

# Setup
session.tui.define.models.solver.density_based_implicit("yes")
session.tui.define.models.unsteady_1st_order("yes")
session.tui.define.operating_conditions.operating_pressure("0")
session.tui.define.models.energy("yes")
session.tui.define.models.ablation("yes")

# TUI API vs. Settings API
session.tui.define.materials.change_create(
    "air", "air", "yes", "ideal-gas", "no", "no", "no", "no", "no", "no"
)

session.setup.materials.fluid["air"]()
session.setup.materials.fluid["air"] = {"density": {"option": "ideal-gas"}}

# Boundary Conditions with Settings API
session.setup.boundary_conditions.change_type(
    zone_list=["inlet"], new_type="pressure-far-field"
)

session.setup.boundary_conditions.wall["wall_ablation"] = {
    "ablation_select_model": "Vielle's Model",
    "ablation_vielle_a": 5,
    "ablation_vielle_n": 0.1,
}


# Dynamic Mesh Controls
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

# Solver Settings
session.tui.define.models.unsteady_2nd_order("yes")

session.tui.solve.set.limits(
    "1", "5e+10", "1", "25000", "1e-14", "1e-20", "100000", "0.2"
)
session.tui.solve.monitors.residual.convergence_criteria(
    "1e-3", "1e-3", "1e-3", "1e-3", "1e-6", "1e-3", "1e-3"
)

# Report Definitions
session.tui.solve.report_definitions.add(
    "drag_force_x", "drag", "thread-names", "wall_ablation", "()", "scaled?", "no", "q"
)
session.tui.solve.report_plots.add(
    "drag_force_x", "report-defs", "drag_force_x", "()", "q"
)
session.tui.solve.report_plots.axes(
    "drag_force_x", "numbers", "float", "4", "exponential", "2", "q"
)
session.tui.solve.report_files.add(
    "drag_force_x",
    "report-defs",
    "drag_force_x",
    "()",
    "file-name",
    "drag_force_x.out",
    "q",
)
session.tui.solve.report_definitions.add(
    "pressure_avg_abl_wall",
    "surface-areaavg",
    "field",
    "pressure",
    "surface-names",
    "wall_ablation",
    "()",
    "q",
)
session.tui.solve.report_plots.add(
    "pressure_avg_abl_wall", "report-defs", "pressure_avg_abl_wall", "()", "q"
)
session.tui.solve.report_plots.axes(
    "pressure_avg_abl_wall", "numbers", "float", "4", "exponential", "2", "q"
)
session.tui.solve.report_files.add(
    "pressure_avg_abl_wall",
    "report-defs",
    "pressure_avg_abl_wall",
    "()",
    "file-name",
    "pressure_avg_abl_wall.out",
    "q",
)
session.tui.solve.report_definitions.add(
    "recede_point",
    "surface-vertexmax",
    "field",
    "z-coordinate",
    "surface-names",
    "wall_ablation",
    "()",
    "q",
)
session.tui.solve.report_plots.add(
    "recede_point", "report-defs", "recede_point", "()", "q"
)
session.tui.solve.report_plots.axes(
    "recede_point", "numbers", "float", "4", "exponential", "2", "q"
)
session.tui.solve.report_files.add(
    "recede_point",
    "report-defs",
    "recede_point",
    "()",
    "file-name",
    "recede_point.out",
    "q",
)

# Initialize and Save
session.tui.solve.initialize.compute_defaults.pressure_far_field("inlet")

# Save case file
save_case_data_as = Path(save_path) / "ablation.cas.h5"
session.tui.file.write_case(save_case_data_as)

# Post-Process
import_data_filename = examples.download_file(
    "ablation_Solved.dat.h5", "pyfluent/examples/Ablation-tutorial", save_path=save_path
)

session.tui.file.read_data(import_data_filename)

session.tui.display.surface.plane_surface("mid_plane", "zx-plane", "0")

# Define contour properties
session.results.graphics.contour["contour_pressure"] = {
    "field": "pressure",
    "surfaces_list": ["mid_plane"],
}

# Display contour
session.results.graphics.contour.display(object_name="contour_pressure")

# Define contour properties
session.results.graphics.contour["contour_mach"] = {
    "field": "mach-number",
    "surfaces_list": ["mid_plane"],
}

# Display contour
session.results.graphics.contour.display(object_name="contour_mach")

# Post-Process with PyVista
from ansys.fluent.visualization.pyvista import Graphics

graphics_session1 = Graphics(session)
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "pressure"
contour1.surfaces_list = ["mid_plane"]
contour1.display()

# Properly close open Fluent session
session.exit()
