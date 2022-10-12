"""
011-Gravity-Separator-PID
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# PID Controller for Gravity Separator

import ansys.fluent.core as pyfluent
import numpy as np

# Create a session and launch the fluent
session = pyfluent.launch_fluent(
    version="2d", precision="double", processor_count=6, mode="solver"
)

# Read a case file
session.tui.file.read_case_data("2d-separator.cas.h5")

pid_kp = 2.0
pid_ti = 0.01
pid_td = 1
desired_water_level = 6
pid_update_frequency = 5
total_iterations = 50  # 5000

# Initial Conditions

initial_outlet_pressure = eval(
    session.scheme_eval.exec(
        (
            "(ti-menu-load-string "
            '"/define/named-expressions/compute '
            'water_outlet_pressure")',
        )
    ).split(" ")[-4]
)
initial_water_level = eval(
    session.scheme_eval.exec(
        (
            "(ti-menu-load-string "
            '"/solve/report-definitions/compute '
            'freesurfacelevel ()")',
        )
    ).split(" ")[-1]
)

print(
    "Outlet Pressure is: "
    + str(initial_outlet_pressure)
    + " Pa and Water Level is: "
    + str(initial_water_level)
    + " m"
)

# Solver Update with PID Control
deriv_error = 0
integral_error = 0
error_old = 0
delta_t = 1
n = int(total_iterations / pid_update_frequency)
water_level = np.zeros(int(total_iterations / pid_update_frequency))
water_pressure = np.zeros(int(total_iterations / pid_update_frequency))
for i in range(n):
    session.tui.solve.iterate(pid_update_frequency)
    current_water_level = eval(
        session.scheme_eval.exec(
            (
                "(ti-menu-load-string "
                '"/solve/report-definitions/compute '
                'freesurfacelevel ()")',
            )
        ).split(" ")[-1]
    )
    water_level[i] = current_water_level
    error = desired_water_level - current_water_level
    integral_error += error * delta_t
    deriv_error = (error - error_old) / delta_t
    control_value = initial_outlet_pressure + pid_kp * (
        error + (1.0 / pid_ti) * integral_error + pid_td * deriv_error
    )
    water_pressure[i] = control_value
    error_old = error
    session.setup.boundary_conditions.pressure_outlet["water_outlet"].phase[
        "mixture"
    ].gauge_pressure = control_value

# Plot - Water Outlet Pressure vs Iterations
import matplotlib.pyplot as plt

X = np.linspace(pid_update_frequency, n * pid_update_frequency, num=n)
plt.plot(X, water_level)
plt.title("Water Level vs Iterations")
plt.ylabel("Water Level (m)")
plt.xlabel("Iterations")
# plt.show()

plt.plot(X, water_pressure)
plt.title("Water Outlet Pressure vs Iterations")
plt.ylabel("Pressure (Pa)")
plt.xlabel("Iterations")
# plt.show()

# Write and save the case file
session.tui.file.write_case_data("2d-separator-final.cas.h5")

# End current session
# session.exit()
