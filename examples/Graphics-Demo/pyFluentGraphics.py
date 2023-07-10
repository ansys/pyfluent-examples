"""
Graphics-Demo
=============
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
    "elbow1.cas", "pyfluent/examples/Graphics-Demo"
)  # noqa: E501

set_config(blocking=True, set_view_on_display="isometric")

# Connect to session
session = pyfluent.launch_fluent()

# Read case and Data
session.tui.file.read_case(import_filename)

# Initialize workflow
session.tui.solve.initialize.initialize_flow()

try:
    from ansys.fluent.visualization.matplotlib import Plots, matplot_windows_manager
    from ansys.fluent.visualization.pyvista import Graphics, pyvista_windows_manager
except ImportError:
    from ansys.fluent.post.matplotlib import Plots, matplot_windows_manager
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

# Create and set iso surface properties
surface1 = graphics_session1.Surfaces["surface-1"]
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.3

# Create Mesh
mesh1 = graphics_session1.Meshes["mesh-1"]
mesh1.show_edges = True
mesh1.surfaces_list = ["wall"]

# Create and set iso vector properties
vector1 = graphics_session1.Vectors["vector-1"]
vector1.surfaces_list = ["symmetry"]
vector1.scale = 4.0
vector1.skip = 4

# plot sessions
# get_ipython().run_line_magic("matplotlib", "notebook")
plots_session1 = Plots(session)
p1 = plots_session1.XYPlots["p1"]
p1.surfaces_list = ["symmetry"]
p1.y_axis_function = "temperature"
p1.plot("p1")

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

# Specify plotters id to animate
pyvista_windows_manager.animate_windows("", ["contour-1", "contour-2"])

from ansys.fluent.core.utils.execution import asynchronous


@asynchronous
def iterate(count):
    session.tui.solve.iterate(count)


iterate(100)

# Close plotter to write animations
pyvista_windows_manager.close_windows()
