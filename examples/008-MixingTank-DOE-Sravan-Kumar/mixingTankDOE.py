"""
008-MixingTank-DOE
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Stirred Tank: DOE and Plotting 3D Surface Plot using Plotly
import ansys.fluent.core as pyfluent
import numpy as np

# Defining constants
density = 998.2
imp_dia = 0.36
visc = np.array([0.001, 0.003, 0.006, 0.01, 0.025, 0.05])
omega = np.array([1, 2.5, 6.0, 10.0, 15.0, 20.0])
torq = np.zeros((len(omega), len(visc)))
power = np.zeros((len(omega), len(visc)))
power_number = np.zeros((len(omega), len(visc)))
reynolds_number = np.zeros((len(omega), len(visc)))

# Create a session
session = pyfluent.launch_fluent(
    version="3d", precision="double", processor_count=6, mode="solver"
)

# Read case file
session.tui.file.read_case("test-laminar-visc.cas.h5")

# DOE
for i in range(len(omega)):
    for j in range(len(visc)):
        session.tui.define.materials.change_create(
            "water-liquid",
            "water-liquid",
            "no",
            "no",
            "no",
            "yes",
            "constant",
            visc[j],
            "no",
            "no",
            "no",
        )
        session.tui.define.boundary_conditions.set.fluid(
            ["fluid_mrf*"], "mrf-omega", "no", omega[i], "q"
        )
        session.tui.define.boundary_conditions.set.wall(
            ["wall_shaft*"], "omega", "no", omega[i], "q"
        )
        session.tui.solve.set.number_of_iterations(2)  # 5000
        session.tui.solve.initialize.initialize_flow()
        session.tui.solve.iterate()
        results_list = session.solution.report_definitions.compute(
            report_defs=["torque"]
        )
        val = results_list[0]["torque"][0]
        torq[i][j] = val
        power[i][j] = omega[i] * val
        reynolds_number[i][j] = (
            density * (omega[i] * 0.159154943) * imp_dia * imp_dia / visc[j]
        )
        power_number[i][j] = power[i][j] / (
            density * pow(omega[i] * 0.159154943, 3) * pow(imp_dia, 5)
        )

# End current session
# session.exit()

# Torque and power list
print(torq)
print(power)

# 3D Surface Plot using Plotly

# import plotly.io as pio
# pio.renderers
# pio.renderers.default = "notebook_connected"

import plotly.graph_objects as go

fig = go.Figure(data=[go.Surface(z=power, x=omega, y=visc)])
fig.update_layout(
    title="Mixing Tank Power Response Surface",
    autosize=False,
    width=700,
    height=700,
    margin=dict(l=80, r=80, b=80, t=80),
)
fig.update_layout(
    scene=dict(
        xaxis_title="Agitation Speed (rad/s)",
        yaxis_title="Fluid Viscosity (Pa s)",
        zaxis_title="Power (W)",
    )
)
# fig.show()

# Plot Power Number vs Re
import matplotlib.pyplot as plt

re = reynolds_number.flatten()
np = power_number.flatten()
plt.scatter(re, np)
plt.title("Power Number vs Re")
plt.xlabel("Impeller Reynolds Number")
plt.ylabel("Power Number")
# plt.show()
