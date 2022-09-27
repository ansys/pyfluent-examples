# Import modules
import ansys.fluent.core as pyfluent
from ansys.fluent.visualization import set_config

set_config(blocking=True, set_view_on_display="isometric")

# Launch fluent
session = pyfluent.launch_fluent(
    version="3d", precision="double", processor_count=4, show_gui=True
)

# Read Mesh
session.solver.tui.file.read_case("ablation.msh.h5")

# Setup
session.solver.tui.define.models.solver.density_based_implicit("yes")
session.solver.tui.define.models.unsteady_1st_order("yes")
session.solver.tui.define.operating_conditions.operating_pressure("0")
session.solver.tui.define.models.energy("yes")
session.solver.tui.define.models.ablation("yes")

# TUI API vs. Settings API
session.solver.tui.define.materials.change_create(
    "air", "air", "yes", "ideal-gas", "no", "no", "no", "no", "no", "no"
)
root = session.solver.root
root.setup.materials.fluid["air"]()
root.setup.materials.fluid["air"] = {"density": {"option": "ideal-gas"}}

# Boundary Conditions with Settings API
root.setup.boundary_conditions.change_type(
    zone_list=["inlet"], new_type="pressure-far-field"
)

# root.setup.boundary_conditions.pressure_far_field['inlet']={
#  'p': {'option': 'constant or expression', 'constant': 13500.0},
#  'm': {'option': 'constant or expression', 'constant': 3},
#  't': {'option': 'constant or expression', 'constant': 4500.0},
#  'coordinate_system': 'Cartesian (X, Y, Z)',
#  'flow_direction_component': [
#   {'option': 'constant or expression','constant': 1},
#   {'option': 'constant or expression', 'constant': 0},
#   {'option': 'constant or expression', 'constant': 0}],
#  'ke_spec': 'Intensity and Viscosity Ratio',
#  'turb_intensity': 0.05,
#  'turb_viscosity_ratio': 10}

# root.setup.boundary_conditions.pressure_outlet['outlet'] = {
#  'p': {'option': 'constant or expression', 'constant': 13500},
#  't0': {'option': 'constant or expression', 'constant': 300},
#  'prevent_reverse_flow': True,}

root.setup.boundary_conditions.wall["wall_ablation"] = {
    "ablation_select_model": "Vielle's Model",
    "ablation_vielle_a": 5,
    "ablation_vielle_n": 0.1,
}


# Dynamic Mesh Controls
session.solver.tui.define.dynamic_mesh.zones.create(
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
session.solver.tui.define.dynamic_mesh.zones.create(
    "outlet",
    "deforming",
    "faceted",
    "no",
    "yes",
    "no",
    "yes",
    "yes",
    "yes",
    "yes",
    "no",
    "yes",
)
session.solver.tui.define.dynamic_mesh.zones.create(
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
    "yes",
    "yes",
    "no",
    "yes",
)
session.solver.tui.define.dynamic_mesh.zones.create(
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
    "yes",
    "yes",
    "no",
    "yes",
)
session.solver.tui.define.dynamic_mesh.zones.create(
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
session.solver.tui.define.models.unsteady_2nd_order("yes")

session.solver.tui.solve.set.limits(
    "1", "5e+10", "1", "25000", "1e-14", "1e-20", "100000", "0.2"
)
session.solver.tui.solve.monitors.residual.convergence_criteria(
    "1e-3", "1e-3", "1e-3", "1e-3", "1e-6", "1e-3", "1e-3"
)

# Report Definitions
session.solver.tui.solve.report_definitions.add(
    "drag_force_x", "drag", "thread-names", "wall_ablation", "()", "scaled?", "no", "q"
)
session.solver.tui.solve.report_plots.add(
    "drag_force_x", "report-defs", "drag_force_x", "()", "q"
)
session.solver.tui.solve.report_plots.axes(
    "drag_force_x", "numbers", "float", "4", "exponential", "2", "q"
)
session.solver.tui.solve.report_files.add(
    "drag_force_x",
    "report-defs",
    "drag_force_x",
    "()",
    "file-name",
    "drag_force_x.out",
    "q",
)
session.solver.tui.solve.report_definitions.add(
    "pressure_avg_abl_wall",
    "surface-areaavg",
    "field",
    "pressure",
    "surface-names",
    "wall_ablation",
    "()",
    "q",
)
session.solver.tui.solve.report_plots.add(
    "pressure_avg_abl_wall", "report-defs", "pressure_avg_abl_wall", "()", "q"
)
session.solver.tui.solve.report_plots.axes(
    "pressure_avg_abl_wall", "numbers", "float", "4", "exponential", "2", "q"
)
session.solver.tui.solve.report_files.add(
    "pressure_avg_abl_wall",
    "report-defs",
    "pressure_avg_abl_wall",
    "()",
    "file-name",
    "pressure_avg_abl_wall.out",
    "q",
)
session.solver.tui.solve.report_definitions.add(
    "recede_point",
    "surface-vertexmax",
    "field",
    "z-coordinate",
    "surface-names",
    "wall_ablation",
    "()",
    "q",
)
session.solver.tui.solve.report_plots.add(
    "recede_point", "report-defs", "recede_point", "()", "q"
)
session.solver.tui.solve.report_plots.axes(
    "recede_point", "numbers", "float", "4", "exponential", "2", "q"
)
session.solver.tui.solve.report_files.add(
    "recede_point",
    "report-defs",
    "recede_point",
    "()",
    "file-name",
    "recede_point.out",
    "q",
)

# Initialize and Save
session.solver.tui.solve.initialize.compute_defaults.pressure_far_field("inlet")

# Initialize solver workflow
session.solver.tui.solve.initialize.initialize_flow()

# Save case file
session.solver.tui.file.write_case("ablation.cas.h5")

# Solve

# session.solver.tui.solve.set.transient_controls.time_step_size('1e-6')
# session.solver.tui.solve.dual_time_iterate('100','20')

# Post-Process
session.solver.tui.file.read_case_data("ablation_Solved.cas.h5")

session.solver.tui.display.surface.plane_surface("mid_plane", "zx-plane", "0")

# Define contour properties
root.results.graphics.contour["contour_pressure"] = {
    "field": "pressure",
    "surfaces_list": ["mid_plane"],
}

# Display contour
root.results.graphics.contour.display(object_name="contour_pressure")

# Define contour properties
root.results.graphics.contour["contour_mach"] = {
    "field": "mach-number",
    "surfaces_list": ["mid_plane"],
}

# Display contour
root.results.graphics.contour.display(object_name="contour_mach")


# Post-Process with PyVista
try:
    from ansys.fluent.visualization.pyvista import Graphics
except ImportError:
    from ansys.fluent.post.pyvista import Graphics

graphics_session1 = Graphics(session)
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "pressure"
contour1.surfaces_list = ["mid_plane"]
contour1.display()

# End current session
session.exit()
