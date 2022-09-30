# Import Pyfluent module
import ansys.fluent.core as pyfluent

# Pyfluent log level
pyfluent.set_log_level("DEBUG")

# Create a session object
session = pyfluent.launch_fluent(mode="solver")

# Check server status
session.check_health()

# Read a case file
session.tui.file.read_case("elbow.cas.gz")

# Initialize a workflow
session.tui.solve.initialize.initialize_flow()

# Set the number of iterations
session.tui.solve.iterate(10)

# Set contour properties
session.tui.display.contour = {
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
    "field": "pressure",
    "filled": True,
    "mesh_object": "",
    "node_values": True,
    "range_option": {"auto_range_on": {"global_range": True}},
    "surfaces_list": [2, 4],
}

# Display contour
session.tui.display.objects.display("contour-1")

# Save contour
session.tui.display.save_picture("contour.png")

# Disable model energy
session.tui.define.models.energy = False

# Check model energy status
print(session.tui.define.models.energy)

# Enable TUI
# session.solver.tui.define.parameters.enable_in_TUI("yes")

# Set velocity inlet conditions
inlet = session.setup.boundary_conditions.velocity_inlet["inlet1"]

# Set velocity magnitude
inlet.vmag.value = 1.2

# Initialize solutin mode
session.solution.initialization()

# End current session
session.exit()
