"""
Steady-Vortex-VOF
=================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

from pathlib import Path

# Prediction of Vortex Depth in a Stirred Tank
# Import pyfluent module
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

###############################################################################
# Specifying save path
# ~~~~~~~~~~~~~~~~~~~~
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.
save_path = Path(pyfluent.EXAMPLES_PATH)

# Downloading example files
import_filename = examples.download_file(
    "vortex-mixingtank.msh.h5",
    "pyfluent/examples/Steady-Vortex-VOF",
    save_path=save_path,
)  # noqa: E501

# Create a session
session = pyfluent.launch_fluent(version="3d", precision="double", processor_count=12)

# Read case file
session.tui.file.read_case(import_filename)

# Get active objects in session class
session.setup.get_active_child_names()

# Copy air and set density and viscosity
# session.setup.materials.copy_database_material_by_name.fluid='air'
mat1 = session.setup.materials.fluid["air"]
mat1.density.value = 1000
mat1.viscosity.value = 0.001

# Turn on Gravity and Create Input Parameter Expression for Agitation Speed
session.tui.define.operating_conditions.gravity("Yes", 0, 0, -9.81)
session.tui.define.parameters.enable_in_TUI("yes")
session.tui.define.named_expressions.add(
    "agitation_speed", "definition", '"240 [rev/min]"', "input-parameter", "yes", "q"
)

# Set MRF zone parameters
session.setup.cell_zone_conditions.fluid["mrf"].mrf_motion = True
cell_zc = session.setup.cell_zone_conditions.fluid["mrf"]
# cell_zc.mrf_omega.value = "agitation_speed"

# Set Rotating Wall BC parameters
# Set wall boundary conditions
session.setup.boundary_conditions.wall["shaft_mrf"].motion_bc = "Moving Wall"
session.setup.boundary_conditions.wall["shaft_mrf"].relative = False
session.setup.boundary_conditions.wall["shaft_mrf"].rotating = True
wall_bc = session.setup.boundary_conditions.wall["shaft_mrf"]
# wall_bc.omega.value = "agitation_speed"
# session.setup.boundary_conditions.wall['shaft_mrf'].ak=-1

# Set Physical Models: VOF & Turbulence Parameters
session.setup.models.viscous.options.curvature_correction = "yes"
session.setup.models.multiphase.models = "vof"

# Define models and phases properties
session.tui.define.models.multiphase.volume_fraction_parameters = (
    "implicit",
    1e-6,
)
session.tui.define.models.multiphase.body_force_formulation("yes")
session.tui.define.phases.set_domain_properties.phase_domains = (
    "phase-2",
    "material",
    "yes",
    "air",
    "q",
    "q",
)
session.tui.define.phases.set_domain_properties.change_phases_names("water", "air")
session.tui.define.models.steady("yes")

# Set initial solve conditions
solve = session.tui.solve
solve.set.multiphase_numerics.solution_stabilization.execute_settings_optimization(
    "yes"
)
session.tui.solve.initialize.reference_frame("absolute")
session.tui.solve.initialize.set_defaults("mixture", "k", 0.001)
session.tui.solve.initialize.mp_localized_turb_init.enable("no")
session.tui.solve.cell_registers.add(
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
session.tui.solve.initialize.initialize_flow()
session.tui.solve.patch("water", "()", "liquid_patch", "()", "mp", 1)

# Setting up objects for postprocessing
session.tui.surface.iso_surface("water", "vof", "freesurface", "()", "()", 0.5, "()")
session.tui.surface.iso_surface("mixture", "y-coordinate", "ymid", "()", "()", 0, "()")

# set graphics mesh properties
session.results.graphics.mesh["internals"] = {}
session.results.graphics.mesh["internals"].surfaces_list = [
    "wall_impeller",
    "shaft_mrf",
    "shaft_tank",
]
session.results.graphics.mesh["internals"].surfaces_list()
session.results.graphics.mesh["tank"] = {}
session.results.graphics.mesh["tank"].surfaces_list = ["wall_tank"]
session.results.graphics.mesh["tank"].surfaces_list()

# set graphics contour properties
session.results.graphics.contour["contour-1"] = {}
session.results.graphics.contour["contour-1"].surfaces_list = ["ymid"]
session.results.graphics.contour["contour-1"].surfaces_list()
session.results.graphics.contour["contour-1"].field = "water-vof"

# set graphics mesh properties
session.results.graphics.mesh["fs"] = {}
session.results.graphics.mesh["fs"].surfaces_list = ["freesurface"]
session.results.graphics.mesh["fs"].surfaces_list()

# Create graphic object
session.tui.display.objects.create(
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
session.tui.solve.animate.objects.create(
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
session.tui.display.views.restore_view("top")
session.tui.display.views.auto_scale()

# Set windows resolution
# session.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.tui.display.set.picture.y_resolution(600)

# Save Initial Files & Run Calculation
save_case_data_as = str(save_path / "vortex_init.cas.h5")
session.tui.file.write_case_data(save_case_data_as)

# Set number of iterations
session.tui.solve.set.number_of_iterations(100)  # 1500

# Stat iterations
session.tui.solve.iterate()


# LIC Setup
session.tui.surface.plane_surface("midplane", "zx-plane", 0)

# Set lic properties
session.results.graphics.lic["lic-1"] = {}
session.results.graphics.lic["lic-1"].surfaces_list = ["midplane"]
session.results.graphics.lic["lic-1"].surfaces_list()
session.results.graphics.lic["lic-1"].field = "velocity-magnitude"
session.results.graphics.lic["lic-1"].lic_intensity_factor = 10
session.results.graphics.lic["lic-1"].texture_size = 10

# Display object
session.tui.display.objects.display("lic-1")

# Set views properties
session.tui.display.views.restore_view("top")
session.tui.display.views.auto_scale()

# Set windows resolution
session.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.tui.display.set.picture.y_resolution(600)

# Save vortex picture
session.tui.display.save_picture("lic-1.png")

# Save Final Vortex Shape
# Display vortex
session.tui.display.objects.display("scene-1")

# Set views properties
session.tui.display.views.restore_view("top")
session.tui.display.views.auto_scale()

# Set windows resolution
session.tui.display.set.picture.use_window_resolution("no")

# Set x-axis resolution
session.tui.display.set.picture.x_resolution(600)

# Set y-axis resolution
session.tui.display.set.picture.y_resolution(600)

# Save vortex picture
session.tui.display.save_picture("vortex.png")

# Save and write case data
save_case_data_as = str(save_path / "vortex_final.cas.h5")
session.tui.file.write_case_data(save_case_data_as)

# GIF Animation: Vortex Formation
import os

import imageio

png_dir = save_path
images = []
for file_name in sorted(os.listdir(png_dir)):
    if file_name.startswith("animation") and file_name.endswith(".png"):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave("vortex.gif", images)

# Load animation
# from IPython.display import Image
# Image(filename="vortex.gif")

# Properly close open Fluent session
session.exit()
