# Import modules
try:
    from ansys.fluent.parametric import ParametricSession
except ImportError:
    from ansys.fluent.addons.parametric import ParametricSession

# Parametric session starting with a case file
session1 = ParametricSession("elbow_params_2.cas.h5", start_transcript=True)

# Start study
study1 = session1.studies["elbow_params_2-Solve"]
session1.studies

# Create a new study
study2 = session1.new_study()

# Get input parameters
ip = study2.design_points["Base DP"].input_parameters
ip

# set parameter_2
ip["parameter_2"] = 1.3

# Set input parameters to design points
study2.design_points["Base DP"].input_parameters = ip

# Update current design point
study2.update_current_design_point()

# Get output parameters
study2.design_points["Base DP"].output_parameters

# Add design point
dp1 = study2.add_design_point()

# Duplicate design point
dp2 = study2.duplicate_design_point(dp1)

# Delete design points
study2.delete_design_points([dp1, dp2])

# Save the project
# session1.project.save_as(
# "D:\Examples (1)\Examples\004 Fluent Parametric - Mainak Kundu\abLatest.flprj")

# Parametric session starting with a project file
# session2 = ParametricSession(project_filepath="ab.flprj", start_transcript=True)

# End sessions
session1.exit()
# session2.exit()
