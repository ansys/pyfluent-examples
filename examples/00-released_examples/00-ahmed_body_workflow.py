"""
.. _ahmed_body_simulation:

Ahmed Body External Aerodynamics Simulation
-------------------------------------------
"""

#######################################################################################
# Objective
# =====================================================================================
#
# Ahmed body is a simplified car model used for studying the flow around it and to
# predict the drag and lift forces. The model consists of a slanted back and a blunt
# front.
#
# In this example, PyFluent API is used to perform Ahmed Body external aerodynamics
# simulation. which includes typical workflow of CFD Simulation as follows:
#
# * Importing the geometry/CAD model.
# * Meshing the geometry.
# * Setting up the solver.
# * Running the solver.
# * Post-processing the results.
#
#
#
# .. image:: ../../_static/ahmed_body_model.png
#    :align: center
#    :alt: Ahmed Body Model


#######################################################################################
# Import required libraries/modules
# =====================================================================================

from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

try:
    import ansys.fluent.visualization.pyvista as pv
except ImportError:
    import ansys.fluent.post.pyvista as pv

from ansys.fluent.visualization import set_config

#######################################################################################
# Specifying save path
# =====================================================================================
# save_path can be specified as Path("E:/", "pyfluent-examples-tests") or
# Path("E:/pyfluent-examples-tests") in a Windows machine for example,  or
# Path("~/pyfluent-examples-tests") in Linux.
save_path = Path(pyfluent.EXAMPLES_PATH)

#######################################################################################
# Configure specific settings for this example
# =====================================================================================
set_config(blocking=True, set_view_on_display="isometric")

#######################################################################################
# Launch Fluent session with meshing mode
# =====================================================================================
session = pyfluent.launch_fluent(mode="meshing", cleanup_on_exit=True)
session.health_check_service.status()

#######################################################################################
# Meshing Workflow
# =====================================================================================

#######################################################################################
# Initialize the Meshing Workflow
# =====================================================================================

workflow = session.workflow
geometry_filename = examples.download_file(
    "ahmed_body_20_0degree_boi_half.scdoc",
    "pyfluent/examples/Ahmed-Body-Simulation",
    save_path=save_path,
)
workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
workflow.TaskObject["Import Geometry"].Arguments = dict(FileName=geometry_filename)
workflow.TaskObject["Import Geometry"].Execute()


#######################################################################################
# Add Local Face Sizing
# =====================================================================================
add_local_sizing = workflow.TaskObject["Add Local Sizing"]
add_local_sizing.Arguments = dict(
    {
        "AddChild": "yes",
        "BOIControlName": "facesize_front",
        "BOIFaceLabelList": ["wall_ahmed_body_front"],
        "BOIGrowthRate": 1.15,
        "BOISize": 8,
    }
)
add_local_sizing.Execute()

add_local_sizing.InsertCompoundChildTask()
workflow.TaskObject["Add Local Sizing"].Execute()
add_local_sizing = workflow.TaskObject["Add Local Sizing"]
add_local_sizing.Arguments = dict(
    {
        "AddChild": "yes",
        "BOIControlName": "facesize_rear",
        "BOIFaceLabelList": ["wall_ahmed_body_rear"],
        "BOIGrowthRate": 1.15,
        "BOISize": 5,
    }
)
add_local_sizing.Execute()

add_local_sizing.InsertCompoundChildTask()
workflow.TaskObject["Add Local Sizing"].Execute()
add_local_sizing = workflow.TaskObject["Add Local Sizing"]
add_local_sizing.Arguments = dict(
    {
        "AddChild": "yes",
        "BOIControlName": "facesize_main",
        "BOIFaceLabelList": ["wall_ahmed_body_main"],
        "BOIGrowthRate": 1.15,
        "BOISize": 12,
    }
)
add_local_sizing.Execute()

#######################################################################################
# Add BOI (Body of Influence) Sizing
# =====================================================================================
add_boi_sizing = workflow.TaskObject["Add Local Sizing"]
add_boi_sizing.InsertCompoundChildTask()
add_boi_sizing.Arguments = dict(
    {
        "AddChild": "yes",
        "BOIControlName": "boi_1",
        "BOIExecution": "Body Of Influence",
        "BOIFaceLabelList": ["ahmed_body_20_0degree_boi_half-boi"],
        "BOISize": 20,
    }
)
add_boi_sizing.Execute()
add_boi_sizing.InsertCompoundChildTask()


#######################################################################################
# Add Surface Mesh Sizing
# =====================================================================================
generate_surface_mesh = workflow.TaskObject["Generate the Surface Mesh"]
generate_surface_mesh.Arguments = dict(
    {
        "CFDSurfaceMeshControls": {
            "CurvatureNormalAngle": 12,
            "GrowthRate": 1.15,
            "MaxSize": 50,
            "MinSize": 1,
            "SizeFunctions": "Curvature",
        }
    }
)

generate_surface_mesh.Execute()
generate_surface_mesh.InsertNextTask(CommandName="ImproveSurfaceMesh")
improve_surface_mesh = workflow.TaskObject["Improve Surface Mesh"]
improve_surface_mesh.Arguments.update_dict({"FaceQualityLimit": 0.4})
improve_surface_mesh.Execute()

#######################################################################################
# Describe Geometry, Update Boundaries, Update Regions
# =====================================================================================
workflow.TaskObject["Describe Geometry"].Arguments = dict(
    CappingRequired="Yes",
    SetupType="The geometry consists of only fluid regions with no voids",
)
workflow.TaskObject["Describe Geometry"].Execute()
workflow.TaskObject["Update Boundaries"].Execute()
workflow.TaskObject["Update Regions"].Execute()

#######################################################################################
# Add Boundary Layers
# =====================================================================================
add_boundary_layers = workflow.TaskObject["Add Boundary Layers"]
add_boundary_layers.AddChildToTask()
add_boundary_layers.InsertCompoundChildTask()
workflow.TaskObject["smooth-transition_1"].Arguments.update_dict(
    {
        "BLControlName": "smooth-transition_1",
        "NumberOfLayers": 14,
        "Rate": 1.15,
        "TransitionRatio": 0.5,
    }
)
add_boundary_layers.Execute()


#######################################################################################
# Generate the Volume Mesh
# =====================================================================================
generate_volume_mesh = workflow.TaskObject["Generate the Volume Mesh"]
generate_volume_mesh.Arguments.update_dict({"VolumeFill": "poly-hexcore"})
generate_volume_mesh.Execute()

#######################################################################################
# Switch to the Solver Mode
# =====================================================================================
session = session.switch_to_solver()

#######################################################################################
# Mesh Visualization
# =====================================================================================

#%%
# .. image:: ../../_static/ahmed_body_mesh_1.png
#    :align: center
#    :alt: Ahmed Body Mesh

#%%
# .. image:: ../../_static/ahmed_body_mesh_2.png
#    :align: center
#    :alt: Ahmed Body Mesh

#######################################################################################
# Solver Setup and Solve Workflow
# =====================================================================================

#######################################################################################
# Define Constants
# =====================================================================================
density = 1.225
inlet_velocity = 30
inlet_area = 0.11203202

#######################################################################################
# Define Materials
# =====================================================================================
session.setup.materials.fluid["air"].density.value = density

viscous = session.setup.models.viscous
viscous.model = "k-epsilon"
viscous.k_epsilon_model = "realizable"
viscous.options.curvature_correction = True

#######################################################################################
# Define Boundary Conditions
# =====================================================================================
inlet = session.setup.boundary_conditions.velocity_inlet["inlet"]
inlet.turbulence.turbulent_intensity = 0.05
inlet.momentum.velocity.value = inlet_velocity
inlet.turbulence.turbulent_viscosity_ratio_real = 5

outlet = session.setup.boundary_conditions.pressure_outlet["outlet"]
outlet.turbulence.turbulent_intensity = 0.05

#######################################################################################
# Define Reference Values
# =====================================================================================
reference_values = session.setup.reference_values
session.setup.reference_values.area = inlet_area
session.setup.reference_values.density = density
session.setup.reference_values.velocity = inlet_velocity

#######################################################################################
# Define Solver Settings
# =====================================================================================
session.solution.methods.p_v_coupling.flow_scheme = "Coupled"

discretization_scheme = session.solution.methods.discretization_scheme
discretization_scheme["pressure"] = "second-order"
discretization_scheme["k"] = "second-order-upwind"
discretization_scheme["epsilon"] = "second-order-upwind"

session.solution.initialization.defaults["k"] = 1e-6

for criterion in [
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
]:
    session.solution.monitor.residual.equations[criterion].absolute_criteria = 0.0001

#######################################################################################
# Define Report Definitions
# =====================================================================================

session.solution.report_definitions.drag["cd-mon1"] = {
    "zones": "*ahmed*",
    "scaled": True,
    "force_vector": [0, 0, 1],
}
session.parameters.output_parameters.report_definitions["cd-mon1-op"] = {
    "report_definition": "cd-mon1",
}
session.solution.monitor.report_plots["cd-mon1"] = {
    "report_defs": ["cd-mon1"],
}

#######################################################################################
# Initialize and Run Solver
# =====================================================================================

initialization = session.solution.initialization
initialization.initialization_type = "standard"
initialization.standard_initialize()

session.solution.run_calculation.iterate(iter_count=5)

#######################################################################################
# Post-Processing Workflow
# =====================================================================================
session.results.surfaces.iso_surface["xmid"] = {
    "field": "x-coordinate",
    "iso_values": [0.0],
}

graphics_session1 = pv.Graphics(session)

contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "velocity-magnitude"
contour1.surfaces_list = ["xmid"]
contour1.display("window-1")

contour2 = graphics_session1.Contours["contour-2"]
contour2.field.allowed_values
contour2.field = "pressure-coefficient"
contour2.surfaces_list = ["xmid"]
contour2.display("window-2")

#######################################################################################
# Simulation Results Visualization
# =====================================================================================

#%%
# .. image:: ../../_static/ahmed_body_model_velocity_mag.png
#    :align: center
#    :alt: Velocity Magnitude

#%%
#    Velocity Magnitude Contour

#%%
# .. image:: ../../_static/ahmed_body_model_pressure_coeff.png
#    :align: center
#    :alt: Peressure Coefficient

#%%
#    Pressure Coefficient Contour

#######################################################################################
# Save the case file
# =====================================================================================

save_case_data_as = Path(save_path) / "ahmed_body_final.cas.h5"
session.file.write_case_data(file_name=save_case_data_as)

#######################################################################################
# Close the session
# =====================================================================================
session.exit()


#######################################################################################
# References
# =====================================================================================
#
# [1] S.R. Ahmed, G. Ramm, Some Salient Features of the Time-Averaged Ground Vehicle
# Wake,SAE-Paper 840300,1984

# sphinx_gallery_thumbnail_path = '_static/ahmed_body_model_pressure_coeff.png'
