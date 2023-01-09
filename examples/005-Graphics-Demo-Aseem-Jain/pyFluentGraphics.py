"""
005-Graphics-Demo
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Post processing in PyFluent

# Fluent data post processing can be categorised in two parts
# Graphics
# Plotting

# Graphics
# At present following graphics objects are supported
# Contour
# Vector
# Iso surface
# Mesh

# For graphics pyVista Library is used.

# Plots
# At present only XY plots are supported.
# For plots matplotlib Library is used.
# In addition animationS are also supported

# Import modules
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.visualization import set_config

import_filename = examples.download_file(
    "elbow1.cas", "pyfluent/examples/005-Graphics-Demo-Aseem-Jain"
)  # noqa: E501

set_config(blocking=True, set_view_on_display="isometric")

# Connect to session
session = pyfluent.launch_fluent(mode="solver")

# Read case and Data
session.tui.file.read_case(import_filename)

# session.tui.file.read_case(case_file_name='elbow1').result()

# Initialize workflow
session.tui.solve.initialize.initialize_flow()

# Import modules

# postprocessing module reside under ansys.fluent.postprocessing

# pyvista [pyvista library]
# plotter [graphics plotter]
# matplotlib [matplot library]
# xyplotter [xyplotter]

try:
    # import ansys.fluent.visualization.matplotlib as plt
    from ansys.fluent.visualization.matplotlib import Plots, matplot_windows_manager

    # import ansys.fluent.visualization.pyvista as pv
    from ansys.fluent.visualization.pyvista import Graphics, pyvista_windows_manager
except ImportError:
    # import ansys.fluent.post.matplotlib as plt
    from ansys.fluent.post.matplotlib import Plots, matplot_windows_manager

    # import ansys.fluent.post.pyvista as pv
    from ansys.fluent.post.pyvista import Graphics, pyvista_windows_manager

# Get Graphics/XYPlots for session
graphics_session1 = Graphics(session)
xyplots_session1 = Plots(session)

# Create, inquire and set contour properties
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "temperature"
contour1.surfaces_list = ["symmetry"]

# Inquire Properties
list(graphics_session1.Contours)
contour1()
contour1(True)

contour1.surfaces_list.allowed_values

contour1.field.allowed_values

# contour1.surfaces_list._type

try:
    contour1.surfaces_list = 1
except Exception as e:
    print(e)


try:
    contour1.surfaces_list = [bool]
except Exception as e:
    print(e)

try:
    contour1.surfaces_list = ["x"]
except Exception as e:
    print(e)

# Set Properties
contour2 = graphics_session1.Contours["contour-2"]
contour2.field = "velocity-magnitude"
contour2.surfaces_list = ["symmetry"]

# Display contour
# contour1.display("contour-1")

# contour2.display("contour-2")

# Plot properties
# p = pyvista_windows_manager.get_plotter("contour-1")
# p.view_isometric()
# # p.add_axes()
# p.add_floor(offset=1, show_edges=True)
# p.add_title("Contour Velocity on Solid", font="courier", color="grey", font_size=10)

# # contour1.display("contour-1_2")
# p2 = pyvista_windows_manager.get_plotter("contour-1_2")
# # p2.add_axes(box=True)
# p2.view_isometric()

# Save the plot
# pyvista_windows_manager.save_graphic("contour-1", "svg")

# Create and set iso surface properties
surface1 = graphics_session1.Surfaces["surface-1"]
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.3

# Display surface
# surface1.display("surface-1")

# Create Mesh
mesh1 = graphics_session1.Meshes["mesh-1"]
mesh1.show_edges = True
mesh1.surfaces_list = ["wall"]

# Display Mesh
# mesh1.display("mesh-1")

# Create and set iso vector properties
vector1 = graphics_session1.Vectors["vector-1"]
vector1.surfaces_list = ["symmetry"]
vector1.scale = 4.0
vector1.skip = 4

# Display vector
# vector1.display("vector-1")

# plot sessions
# get_ipython().run_line_magic("matplotlib", "notebook")
plots_session1 = Plots(session)
p1 = plots_session1.XYPlots["p1"]
p1.surfaces_list = ["symmetry"]
p1.y_axis_function = "temperature"
p1.plot("p1")

# Save plot
# matplot_windows_manager.save_graphic("p1", "png")

p1.surfaces_list = ["symmetry"]
p1.y_axis_function = "pressure"
matplot_windows_manager.refresh_windows("", ["p1"])

from ansys.fluent.visualization.matplotlib import matplot_windows_manager

# Define functions to plot
p1.y_axis_function = "pressure"
matplot_windows_manager.open_window("p2")
matplot_windows_manager.set_object_for_window(p1, "p2")
matplot_windows_manager.refresh_windows("", ["p1", "p2"])

# Change function
plots_session1 = Plots(session)
p1 = plots_session1.XYPlots["p1"]
p1.surfaces_list = ["symmetry"]
p1.y_axis_function = "velocity-magnitude"
p1.plot("p3")

# Postprocessing / Animation during solve
# Event manager provide functionality to execute callbacks during run time.
# This callback can refresh graphics and create animations.
# Callbacks are invoked with session id and event info.
session.events_manager.events_list

# Define callbacks
from ansys.fluent.core.utils.generic import execute_in_event_loop_threadsafe


@execute_in_event_loop_threadsafe
def auto_refersh_call_back_iteration(session_id, event_info):
    if event_info.index % 5 == 0:
        pyvista_windows_manager.refresh_windows(session_id, ["contour-1", "contour-2"])
        matplot_windows_manager.refresh_windows("", ["residual"])


@execute_in_event_loop_threadsafe
def initialize_call_back(session_id, event_info):
    pyvista_windows_manager.refresh_windows(session_id, ["contour-1", "contour-2"])
    matplot_windows_manager.refresh_windows("", ["residual"])


# Register callbacks
cb_init_id = session.events_manager.register_callback(
    "InitializedEvent", initialize_call_back
)
cb_data_read_id = session.events_manager.register_callback(
    "DataReadEvent", initialize_call_back
)
cb_itr_id = session.events_manager.register_callback(
    "IterationEndedEvent", auto_refersh_call_back_iteration
)
# cb_time_step_id = session.events_manager.register_callback(
#                   'TimestepEndedEvent', auto_refersh_call_back_time_step
#                   )

# Un Register callbacks
# session.events_manager.unregister_callback(cb_init_id)
# session.events_manager.unregister_callback(cb_data_read_id)
# session.events_manager.unregister_callback(cb_itr_id)

# Monitors
# Monitor manager manages solver monitors/residuals.
# It shall plot data on registered plotter.

# plots_session1 = Plots(session)
# residual=plots_session1.Monitors["p1"]
# residual.monitor_set_name = "residual"

# session.monitors_manager.stop()

# Animations

# Specify plotters id to animate
pyvista_windows_manager.animate_windows("", ["contour-1", "contour-2"])

from ansys.fluent.core.utils.async_execution import asynchronous


@asynchronous
def iterate(count):
    session.tui.solve.iterate(count)


iterate(100)

# session.tui.solve.iterate(100)
# session.tui.solver.solve.dual_time_iterate(20, 20).result()

# Close plotter to write animations
pyvista_windows_manager.close_windows()

# Play animation by loading gif file
# from IPython.display import Image

# Image(filename="contour-1.gif")

# Image(filename="contour-2.gif")

# End current session
# session.exit()
