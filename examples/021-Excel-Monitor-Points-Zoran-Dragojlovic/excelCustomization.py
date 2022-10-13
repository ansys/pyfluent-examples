"""
021-Excel-Monitor-Points
==========================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Load Settings from Excel Spreadsheet
# Import modules
# get_ipython().run_line_magic('matplotlib', 'inline')
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_case_filename = examples.download_file(
    "glycerol_filling_mixing_init.cas.h5",
    "pyfluent/examples/021-Excel-Monitor-Points-Zoran-Dragojlovic",
)  # noqa: E501

import_data_filename = examples.download_file(
    "glycerol_filling_mixing_init.dat.h5",
    "pyfluent/examples/021-Excel-Monitor-Points-Zoran-Dragojlovic",
)  # noqa: E501


# sphinx_gallery_thumbnail_number = -5
from ansys.fluent.visualization import set_config

# from ansys.fluent.visualization.matplotlib import Plots
from ansys.fluent.visualization.pyvista import Graphics
import pandas as pd

set_config(blocking=True, set_view_on_display="isometric")

# Import Excel Into Notebook
dataset = pd.read_excel("Setup.xlsx")

# Convert Columns Into Variables
listNames = dataset["Monitor Name"]
listCoordX = dataset["X"]
listCoordY = dataset["Y"]
listCoordZ = dataset["Z"]

# Launch fluent
session = pyfluent.launch_fluent(mode="solver")

# Set server status
session.check_health()

# Read case file
session.tui.file.read_case(import_case_filename)

# Read case data
session.tui.file.read_data(import_data_filename)

# for index in range(len(listNames)):
#     session.tui.surface.point_surface(name=
#     listNames[index], x=listCoordX[index], y=listCoordY[index], z=listCoordZ[index])

# Display tank slice
graphics = Graphics(session=session)
tankSlice = graphics.Meshes["tank-slice"]
tankSlice.show_edges = True
tankSlice.surfaces_list = ["tank-slice"]
# tankSlice.display("window-1")

# Display contour
graphics_session = Graphics(session)
contourVF = graphics_session.Contours["contour-vf"]
contourVF.field = "liquid-vof"
contourVF.surfaces_list = ["tank-slice"]
# contourVF.display("window-2")

# End current session
# session.exit()
