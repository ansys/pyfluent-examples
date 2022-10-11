"""
Simulation Examples
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Brake Thermal Example

# Objective
# Demonstrate:
# Fluent setup and simulation using PyFluent
# Post processing using PyVista and Matplotlib

# Problem Description
# Braking surface temperature assessment is vey important for safety
# Brake fade, Vapor lock
# Brake pad wear
# Braking performance

# import modules
import ansys.fluent.core as pyfluent

# Set log level
# pyfluent.set_log_level("DEBUG")

# Open Fluent in GUI mode
session = pyfluent.launch_fluent(
    version="3ddp", precision="double", processor_count=2, mode="solver"
)

# Check server status
session.check_health()


# Read mesh file
session.tui.file.read_case("brake.msh")


# Define models and material
session.tui.define.models.energy("yes", "no", "no", "no", "yes")
session.tui.define.models.unsteady_2nd_order_bounded("Yes")
session.tui.define.materials.copy("solid", "steel")


# Solve only energy equation (conduction)
session.tui.solve.set.equations("flow", "no", "kw", "no")


# Define disc rotation
# (15.79 rps corresponds to 100 km/h car speed
# with 0.28 m of axis height from ground)
session.tui.define.boundary_conditions.set.solid(
    "disc1",
    "disc2",
    "()",
    "solid-motion?",
    "yes",
    "solid-omega",
    "no",
    -15.79,
    "solid-x-origin",
    "no",
    -0.035,
    "solid-y-origin",
    "no",
    -0.821,
    "solid-z-origin",
    "no",
    0.045,
    "solid-ai",
    "no",
    0,
    "solid-aj",
    "no",
    1,
    "solid-ak",
    "no",
    0,
    "q",
)

# ### Apply frictional heating on pad-disc surfaces
# (wall thickness 0f 2 mm has been assumed and
# 2e9 w/m3 is the heat generation which has been
# calculated from kinetic energy change due to braking)
session.tui.define.boundary_conditions.set.wall(
    "wall_pad-disc1",
    "wall-pad-disc2",
    "()",
    "wall-thickness",
    0.002,
    "q-dot",
    "no",
    2e9,
    "q",
)


# Outer surfaces are applied a constant htc of 100 W/(m2 K)
# and 300 K free stream temperature
session.tui.define.boundary_conditions.set.wall(
    "wall-disc*",
    "wall-geom*",
    "()",
    "thermal-bc",
    "yes",
    "convection",
    "convective-heat-transfer-coefficient",
    "no",
    100,
    "q",
)

# Initialize with 300 K temperature
session.tui.solve.initialize.initialize_flow()


# ### Report definitions, monitor plots and animation setup
session.tui.solve.report_definitions.add(
    "max-pad-temperature",
    "volume-max",
    "field",
    "temperature",
    "zone-names",
    "geom-1-innerpad",
    "geom-1-outerpad",
)
session.tui.solve.report_definitions.add(
    "max-disc-temperature",
    "volume-max",
    "field",
    "temperature",
    "zone-names",
    "disc1",
    "disc2",
)

session.tui.solve.report_plots.add(
    "max-temperature",
    "report-defs",
    "max-pad-temperature",
    "max-disc-temperature",
    "()",
)
session.tui.solve.report_files.add(
    "max-temperature",
    "report-defs",
    "max-pad-temperature",
    "max-disc-temperature",
    "()",
)

# Set contour properties
session.results.graphics.contour["contour-1"] = {
    "boundary_values": True,
    "color_map": {
        "color": "field-velocity",
        "font_automatic": True,
        "font_name": "Helvetica",
        "font_size": 0.032,
        "format": "%0.2e",
        "length": 0.54,
        "log_scale": False,
        "position": 1,
        "show_all": True,
        "size": 100,
        "user_skip": 9,
        "visible": True,
        "width": 6.0,
    },
    "coloring": {"smooth": False},
    "contour_lines": False,
    "display_state_name": "None",
    "draw_mesh": False,
    "field": "temperature",
    "filled": True,
    "mesh_object": "",
    "node_values": True,
    "range_option": {"auto_range_on": {"global_range": True}},
}


# Create a graphic object
session.tui.display.objects.create(
    "contour",
    "temperature",
    "field",
    "temperature",
    "surface-list",
    "wall*",
    "()",
    "color-map",
    "format",
    "%0.1f",
    "q",
    "range-option",
    "auto-range-off",
    "minimum",
    300,
    "maximum",
    400,
    "q",
    "q",
)

# Select property to display
session.tui.display.objects.display("temperature")

# Set views properties
session.tui.display.views.restore_view("top")
session.tui.display.views.camera.zoom_camera(2)

# Save the animation
session.tui.display.views.save_view("animation-view")

# Create animation
session.tui.solve.animate.objects.create(
    "animate-temperature",
    "animate-on",
    "temperature",
    "frequency-of",
    "flow-time",
    "flow-time-frequency",
    0.05,
    "view",
    "animation-view",
    "q",
)

# Run simulation for 2 seconds flow time
# Set time step
session.tui.solve.set.transient_controls.time_step_size(0.01)

# Set number of iterations
session.tui.solve.dual_time_iterate(10, 5)  # 200, 5

# Write and save case file data
session.tui.file.write_case_data("brake-final")


# PyVista post processing
try:
    import ansys.fluent.visualization.pyvista as pv
except ImportError:
    import ansys.fluent.post.pyvista as pv


# Create a graphics session
graphics_session1 = pv.Graphics(session)

# Temperature contour
contour1 = graphics_session1.Contours["temperature"]


# Following command shows setting/control options available
contour1()

# Setting contour properties
contour1.field = "temperature"
contour1.surfaces_list = [
    "wall-disc1",
    "wall-disc2",
    "wall-pad-disc2",
    "wall_pad-disc1",
    "wall-geom-1-bp_inner",
    "wall-geom-1-bp_outer",
    "wall-geom-1-innerpad",
    "wall-geom-1-outerpad",
]
contour1.range.option = "auto-range-off"
contour1()
contour1.range.auto_range_off.minimum = 300
contour1.range.auto_range_off.maximum = 400
# contour1.display()


import csv

# Matplotlib: Reads Fluent monitor file and shows imbeded plot
import matplotlib.pyplot as plt

X = []
Y = []
Z = []
i = -1
with open("report-file-0.out", "r") as datafile:
    plotting = csv.reader(datafile, delimiter=" ")
    for rows in plotting:
        i = i + 1
        if i > 2:
            X.append(float(rows[3]))
            Y.append(float(rows[2]))
            Z.append(float(rows[1]))
    plt.title("Maximum Temperature", fontdict={"color": "darkred", "size": 20})
    plt.plot(X, Z, label="Max. Pad Temperature", color="red")
    plt.plot(X, Y, label="Max. Disc Temperature", color="blue")
    plt.xlabel("Time (sec)")
    plt.ylabel("Max Temperature (K)")
    plt.legend(loc="lower right", shadow=True, fontsize="x-large")
    plt.show()

# End current session
# session.exit()
