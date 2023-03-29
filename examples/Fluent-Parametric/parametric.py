"""
Fluent-Parametric
=================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# Import modules
try:
    from ansys.fluent.parametric import ParametricSession
except ImportError:
    from ansys.fluent.addons.parametric import ParametricSession

from pathlib import Path  # noqa: F401

import ansys.fluent.core as pyfluent  # noqa: F401
from ansys.fluent.core import examples

import_filename = examples.download_file(
    "elbow_params_2.cas.h5", "pyfluent/examples/Fluent-Parametric"
)  # noqa: E501

# Parametric session starting with a case file
session1 = ParametricSession(import_filename, start_transcript=True)

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
# project_filepath_save_as = str(
#     Path(pyfluent.EXAMPLES_PATH) / "fluent_parametric_study_save_as.flprj"
# )
# session1.project.save_as(project_filepath=project_filepath_save_as)
#
# # Parametric session starting with a project file
# project_filepath_read = project_filepath_save_as
# session2 = ParametricSession(project_filepath=project_filepath_read, start_transcript=True)  # noqa: E501
