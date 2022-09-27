# Prediction of Vortex Depth in a Stirred Tank
# Import pyfluent module
import ansys.fluent.core as pyfluent

# set log level to info
pyfluent.set_log_level("INFO")

# Create a session
session = pyfluent.launch_fluent(
    version="3d", precision="double", processor_count=6, show_gui=True
)

# Read case file
session.solver.tui.file.read_case("vortex-mixingtank.msh.h5")

root = session.solver.root

# Get active objects in root class
root.setup.get_active_child_names()

# Copy air and set density and viscosity
# root.setup.materials.copy_database_material_by_name.fluid='air'
mat1 = root.setup.materials.fluid["air"]
mat1.density.value = 1000
mat1.viscosity.value = 0.001

# Turn on Gravity and Create Input Parameter Expression for Agitation Speed
session.solver.tui.define.operating_conditions.gravity("Yes", 0, 0, -9.81)
session.solver.tui.define.parameters.enable_in_TUI("yes")
session.solver.tui.define.named_expressions.add(
    "agitation_speed", "definition", '"240 [rev/min]"', "input-parameter", "yes", "q"
)

# Set MRF zone parameters
root.setup.cell_zone_conditions.fluid["mrf"].mrf_motion = True
cell_zc = root.setup.cell_zone_conditions.fluid["mrf"]
cell_zc.mrf_omega.value = "agitation_speed"

# Following mrf_ak is not available in latest API, hence it is commented out.
# root.setup.cell_zone_conditions.fluid['mrf'].mrf_ak = {
#    'option': 'constant or expression',
#    'constant': -1 }

# Set Rotating Wall BC parameters
# Set wall boundary conditions
root.setup.boundary_conditions.wall["shaft_mrf"].motion_bc = "Moving Wall"
root.setup.boundary_conditions.wall["shaft_mrf"].relative = False
root.setup.boundary_conditions.wall["shaft_mrf"].rotating = True
wall_bc = root.setup.boundary_conditions.wall["shaft_mrf"]
wall_bc.omega.value = "agitation_speed"
# root.setup.boundary_conditions.wall['shaft_mrf'].ak=-1

# Set Physical Models: VOF & Turbulence Parameters
root.setup.models.viscous.options.curvature_correction = "yes"
root.setup.models.multiphase.models = "vof"

# Define models and phases properties
session.solver.tui.define.models.multiphase.volume_fraction_parameters = (
    "implicit",
    1e-6,
)
session.solver.tui.define.models.multiphase.body_force_formulation("yes")
session.solver.tui.define.phases.set_domain_properties.phase_domains = (
    "phase-2",
    "material",
    "yes",
    "air",
    "q",
    "q",
)
session.solver.tui.define.phases.set_domain_properties.change_phases_names(
    "water", "air"
)
session.solver.tui.define.models.steady("yes")

# Set initial solve conditions
solve = session.solver.tui.solve
solve.set.multiphase_numerics.solution_stabilization.execute_settings_optimization(
    "yes"
)
session.solver.tui.solve.initialize.reference_frame("absolute")
session.solver.tui.solve.initialize.set_defaults("mixture", "k", 0.001)
session.solver.tui.solve.initialize.mp_localized_turb_init.enable("no")
session.solver.tui.solve.cell_registers.add(
    "liquid_patch",
    "type",
    "hexahedron",
    "min-point",
    -100,
    -100,
    -100,
    "max-point",
    100,
    100,
    0.19,
    "q",
    "q",
)
session.solver.tui.solve.initialize.initialize_flow()
session.solver.tui.solve.patch("water", "()", "liquid_patch", "()", "mp", 1)

# Setting up objects for postprocessing
session.solver.tui.surface.iso_surface(
    "water", "vof", "freesurface", "()", "()", 0.5, "()"
)
session.solver.tui.surface.iso_surface(
    "mixture", "y-coordinate", "ymid", "()", "()", 0, "()"
)

# set graphics mesh properties
root.results.graphics.mesh["internals"] = {}
root.results.graphics.mesh["internals"].surfaces_list = [
    "wall_impeller",
    "shaft_mrf",
    "shaft_tank",
]
root.results.graphics.mesh["internals"].surfaces_list()
root.results.graphics.mesh["tank"] = {}
root.results.graphics.mesh["tank"].surfaces_list = ["wall_tank"]
root.results.graphics.mesh["tank"].surfaces_list()

# set graphics contour properties
root.results.graphics.contour["contour-1"] = {}
root.results.graphics.contour["contour-1"].surfaces_list = ["ymid"]
root.results.graphics.contour["contour-1"].surfaces_list()
root.results.graphics.contour["contour-1"].field = "water-vof"

# set graphics mesh properties
root.results.graphics.mesh["fs"] = {}
root.results.graphics.mesh["fs"].surfaces_list = ["freesurface"]
root.results.graphics.mesh["fs"].surfaces_list()

# Create graphic object
session.solver.tui.display.objects.create(
    "scene",
    "scene-1",
    "graphics-objects",
    "add",
    "tank",
    "transparency",
    75,
    "q",
    "add",
    "internals",
    "transparency",
    20,
    "q",
    "add",
    "fs",
    "transparency",
    20,
    "q",
    "q",
    "q",
)

# Create animations
session.solver.tui.solve.animate.objects.create(
    "animation-2",
    "animate-on",
    "scene-1",
    "frequency",
    20,
    "storage-type",
    "png",
    "view",
    "top",
    "q",
    "q",
)

# # Set views properties
session.solver.tui.display.views.restore_view("top")
session.solver.tui.display.views.auto_scale()

# Set windows resolution
session.solver.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.solver.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.solver.tui.display.set.picture.y_resolution(600)

# Save Initial Files & Run Calculation
session.solver.tui.file.write_case_data("vortex_init.cas.h5")

# Set number of iterations
session.solver.tui.solve.set.number_of_iterations(25)  # 1500

# Stat iterations
session.solver.tui.solve.iterate()


# LIC Setup
session.solver.tui.surface.plane_surface("midplane", "zx-plane", 0)

# Set lic properties
root.results.graphics.lic["lic-1"] = {}
root.results.graphics.lic["lic-1"].surfaces_list = ["midplane"]
root.results.graphics.lic["lic-1"].surfaces_list()
root.results.graphics.lic["lic-1"].field = "velocity-magnitude"
# root.results.graphics.lic['lic-1'].lic_image_filter='Strong Sharpen'
root.results.graphics.lic["lic-1"].lic_intensity_factor = 10
root.results.graphics.lic["lic-1"].texture_size = 10

# Display object
session.solver.tui.display.objects.display("lic-1")

# Set views properties
session.solver.tui.display.views.restore_view("top")
session.solver.tui.display.views.auto_scale()

# Set windows resolution
session.solver.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.solver.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.solver.tui.display.set.picture.y_resolution(600)

# Save vortex picture
session.solver.tui.display.save_picture("lic-1.png")

# Save Final Vortex Shape
# Display vortex
session.solver.tui.display.objects.display("scene-1")

# Set views properties
session.solver.tui.display.views.restore_view("top")
session.solver.tui.display.views.auto_scale()

# Set windows resolution
session.solver.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.solver.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.solver.tui.display.set.picture.y_resolution(600)

# Save vortex picture
session.solver.tui.display.save_picture("vortex.png")

# Save and write case data
session.solver.tui.file.write_case_data("vortex_final.cas.h5")

# End current session
session.exit()


# GIF Animation: Vortex Formation
import os

import imageio

png_dir = os.getcwd()
images = []
for file_name in sorted(os.listdir(png_dir)):
    if file_name.startswith("animation") and file_name.endswith(".png"):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave("vortex.gif", images)

# Load animation
from IPython.display import Image

Image(filename="vortex.gif")
