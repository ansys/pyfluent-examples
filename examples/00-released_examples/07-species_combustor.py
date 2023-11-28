""".. _ref_species_combustor:

Modeling Species Transport and Gaseous Combustion
-------------------------------------------------
This example demonstrates using Fluent's species transport model to simulate
the reacting flow inside a cylindrical methane-air combustor. The resulting
temperature and flow fields are studied, as well as the NOx pollutants
produced.

This is based on the Fluent tutorial titled "Modeling Species Transport and
Gaseous Combustion".

**Workflow tasks**

The Modeling Species Transport and Gaseous Combustion example guides you
through these tasks:

- Loading and preparing the 2D axisymmetric mesh.
- Setting up the species transport and turbulence models.
- Setting up the boundary conditions.
- Solving for the temperature and flow fields.
- Solving for pollutant production.
- Postprocessing the solutions.

**Problem description**

The problem considers a turbulent diffusion flame in a cylindrical combustor.
A small nozzle in the center of the combustor introduces methane at 80 m/s.
Ambient air enters the combustor coaxially at 0.5 m/s. The overall equivalence
ratio is approximately 0.76 (approximately 28% excess air). The high-speed
methane jet initially expands with little interference from the outer wall,
and entrains and mixes with the low-speed air. The Reynolds number based on
the methane jet diameter is approximately :math:`5.7 \\times 10^3`.

"""

# sphinx_gallery_thumbnail_path = '_static/species_combustor_thumbnail.png'

###############################################################################
# .. image:: ../../_static/species_combustor_geom.png

###############################################################################
# Example Setup
# -------------
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes downloading and importing the
# geometry files.

from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

mesh_path = examples.download_file(
    "gascomb.msh.gz",
    "pyfluent/species_combustor_example",
)
working_dir = Path(pyfluent.EXAMPLES_PATH)

###############################################################################
# Launch Fluent
# ~~~~~~~~~~~~~
# Launch Fluent in 2D solver mode with double precision running on a single
# processor.

solver = pyfluent.launch_fluent(
    version="2d",
    precision="double",
    processor_count=1,
    mode="solver",
    cwd=working_dir,
)

###############################################################################
# Mesh
# ----
#
# Load mesh
# ~~~~~~~~~

solver.file.read_mesh(file_name=mesh_path)

###############################################################################
# Check mesh quality
# ~~~~~~~~~~~~~~~~~~

solver.mesh.check()

###############################################################################
# Scale mesh
# ~~~~~~~~~~
# Since the mesh was created in units of millimeters and Fluent operates in
# meters, scale the mesh by a factor of 0.001. Then, check the mesh again.

solver.mesh.scale(
    x_scale=1e-3,
    y_scale=1e-3,
)

solver.mesh.check()

###############################################################################
# Specify that the mesh is axisymmetric
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Specify that the mesh is axisymmetric by changing the '2D Space' setting.

solver.setup.general.solver.two_dim_space = "axisymmetric"

###############################################################################
# Models
# ------
#
# Enable energy transport equation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

solver.setup.models.energy.enabled = True

###############################################################################
# Enable species transport equation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enable the species transport equation. Configure it to model volumetric
# reactions, set the mixture material to ``methane-air``, and set the
# ``turbulence-chemistry`` interaction model to ``eddy-dissipation``.
#
# Setting the mixture to ``methane-air`` will import the species relevant to
# methane-air combustion: methane, oxygen, nitrogen, carbon dioxide, and steam.

species = solver.setup.models.species
species.model.option = "species-transport"
species.reactions.enable_volumetric_reactions = True
species.model.material = "methane-air"
species.turb_chem_interaction_model = "eddy-dissipation"

###############################################################################
# Boundary conditions
# -------------------
#
# Convert symmetry zone to axis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The symmetry zone must be converted to an axis zone to prevent numerical
# difficulties as the radius approaches zero.

bc = solver.setup.boundary_conditions
bc.set_zone_type(
    zone_list=["symmetry-5"],
    new_type="axis",
)

###############################################################################
# Set up the air inlet boundary condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rename ``velocity-inlet-8`` to ``air-inlet`` and assign the following settings:
#
# - Velocity: 0.5 m/s
# - Turbulent specification: Intensity and hydraulic diameter
# - Turbulent intensity: 10%
# - Hydraulic diameter: 0.44 m
# - Temperature: 300 K
# - O2 mass fraction: 23%
#
# Since the 'last species' is set to nitrogen, the unspecified remaining 77% of the
# species mass fraction will be set to nitrogen.

bc.velocity_inlet["velocity-inlet-8"].name = "air-inlet"

air_inlet = bc.velocity_inlet["air-inlet"]
air_inlet.momentum.velocity.value = 0.5
air_inlet.turbulence.turbulent_specification = "Intensity and Hydraulic Diameter"
air_inlet.turbulence.turbulent_intensity = 0.1
air_inlet.turbulence.hydraulic_diameter = 0.44
air_inlet.thermal.t.value = 300
air_inlet.species.mf["o2"].value = 0.23

###############################################################################
# Set up the fuel inlet boundary condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rename ``velocity-inlet-6`` to ``fuel-inlet`` and assign the following settings:
#
# - Velocity: 80 m/s
# - Turbulent specification: Intensity and hydraulic diameter
# - Turbulent intensity: 10%
# - Hydraulic diameter: 0.01 m
# - Temperature: 300 K
# - CH4 mass fraction: 100%

bc.velocity_inlet["velocity-inlet-6"].name = "fuel-inlet"

fuel_inlet = bc.velocity_inlet["fuel-inlet"]
fuel_inlet.momentum.velocity.value = 80
fuel_inlet.turbulence.turbulent_specification = "Intensity and Hydraulic Diameter"
fuel_inlet.turbulence.turbulent_intensity = 0.1
fuel_inlet.turbulence.hydraulic_diameter = 0.01
fuel_inlet.thermal.t.value = 300
fuel_inlet.species.mf["ch4"].value = 1

###############################################################################
# Set up the pressure outlet boundary condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assign the following settings:
#
# - Gauge pressure: 0 Pa
# - Backflow turbulent specification: Intensity and hydraulic diameter
# - Backflow turbulent intensity: 10%
# - Backflow hydraulic diameter: 0.45 m
# - Backflow temperature: 300 K
# - Backflow O2 mass fraction: 23%

outlet = bc.pressure_outlet["pressure-outlet-9"]
outlet.momentum.gauge_pressure.value = 0
outlet.turbulence.turbulent_specification = "Intensity and Hydraulic Diameter"
outlet.turbulence.turbulent_intensity = 0.1
outlet.turbulence.hydraulic_diameter = 0.45
outlet.thermal.t0.value = 300
outlet.species.mf["o2"].value = 0.23

###############################################################################
# Set up the outer wall boundary condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rename ``wall-7`` to ``outer-wall`` and set it to be a constant-temperature
# wall with a temperature of 300 K.

bc.wall["wall-7"].name = "outer-wall"

outer_wall = bc.wall["outer-wall"]
outer_wall.thermal.thermal_bc = "Temperature"
outer_wall.thermal.t.value = 300

###############################################################################
# Set up the nozzle boundary condition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rename ``wall-2`` to ``nozzle`` and set it to be an adiabatic wall.

bc.wall["wall-2"].name = "nozzle"

nozzle = bc.wall["nozzle"]
nozzle.thermal.thermal_bc = "Heat Flux"
nozzle.thermal.q.value = 0

###############################################################################
# Initial reaction solution
# -------------------------
# Calculate an initial flow solution accounting for combustion.
#
# Initialize flow
# ~~~~~~~~~~~~~~~
# Initialize the flow field using hybrid initialization.

solver.solution.initialization.hybrid_initialize()

###############################################################################
# Write case file
# ~~~~~~~~~~~~~~~
# Enable overwrite and write the case file to ``gascomb1.cas.h5``.

solver.file.batch_options.confirm_overwrite = True
solver.file.write_case(file_name="gascomb1.cas.h5")

###############################################################################
# Solve
# ~~~~~
# Run the calculation for 200 iterations with the time scale factor set to 5
# to speed convergence.

run_calc = solver.solution.run_calculation
run_calc.pseudo_time_settings.time_step_method.time_step_size_scale_factor = 5
run_calc.iter_count = 200
run_calc.calculate()

###############################################################################
# Write case and data files
# ~~~~~~~~~~~~~~~~~~~~~~~~~

solver.file.write_case_data(file_name="gascomb1.cas.h5")

###############################################################################
# Postprocessing
# --------------
#
# Report total sensible heat flux
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the total sensible heat flux and report it in the file
# ``heat_transfer_report.txt``. Compare it to the heat of the reaction source.
#
# We expect a net total sensible heat transfer rate of 1.5 W, which is small in
# comparison to the expected heat of the reaction source of 204,390.7 W.

solver.results.report.fluxes.heat_transfer_sensible(
    all_boundary_zones=True,
    write_to_file=True,
    file_name="heat_transfer_report.txt",
)
with open(working_dir / "heat_transfer_report.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Configure graphics picture export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Since Fluent is being run without the GUI, we will need to export plots as
# picture files.

graphics = solver.results.graphics
graphics.picture.use_window_resolution = False
graphics.picture.x_resolution = 1920
graphics.picture.y_resolution = 1440

###############################################################################
# Create and render temperature contour
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the temperature throughout the combustor, display it,
# then export the image for inspection.

graphics.contour["contour-temp"] = {
    "filled": True,
    "coloring": {"option": "banded"},
    "field": "temperature",
}
graphics.contour["contour-temp"].display()

graphics.picture.save_picture(file_name="contour-temp.png")

###############################################################################
# Temperature:
#
# .. image:: ../../_static/combustor_contour-temp.png

###############################################################################
# Create and render velocity vector plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a vector plot of the velocity vectors, display it, then export the
# image for inspection.

graphics.vector["vector-vel"] = {
    "style": "arrow",
    "scale": {"scale_f": 0.01},
    "vector_opt": {
        "fixed_length": True,
        "scale_head": 0.1,
    },
}
graphics.vector["vector-vel"].display()

graphics.picture.save_picture(file_name="vector-vel.png")

###############################################################################
# Velocity:
#
# .. image:: ../../_static/combustor_vector-vel.png

###############################################################################
# Create and render mass fraction contours
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the mass fractions of methane, oxygen, carbon dioxide,
# and steam, display them, then export the images for inspection.

for species in ("ch4", "o2", "co2", "h2o"):
    contour_name = f"contour-{species}-mass-fraction"
    graphics.contour[contour_name] = {"field": species}
    graphics.contour[contour_name].display()
    graphics.picture.save_picture(
        file_name=f"contour-{species}-mass-fraction.png",
    )

###############################################################################
# Mass fraction of methane:
#
# .. image:: ../../_static/combustor_contour-ch4-mass-fraction.png
#
# Mass fraction of oxygen:
#
# .. image:: ../../_static/combustor_contour-o2-mass-fraction.png
#
# Mass fraction of carbon dioxide:
#
# .. image:: ../../_static/combustor_contour-co2-mass-fraction.png
#
# Mass fraction of steam:
#
# .. image:: ../../_static/combustor_contour-h2o-mass-fraction.png

###############################################################################
# Report mass-weighted average outlet temperature
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the mass-weighted average of the outlet temperature and report it
# in the file ``avg-exit-temp.txt``. It should be approximately 1840 K.

solver.results.report.surface_integrals.mass_weighted_avg(
    surface_names=["pressure-outlet-9"],
    report_of="temperature",
    write_to_file=True,
    file_name="avg-exit-temp.txt",
)
with open(working_dir / "avg-exit-temp.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Report area-weighted average outlet flow velocity
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the area-weighted average of the outlet flow velocity and report
# it in the file ``avg-exit-vel.txt``. It should be approximately 3.3 m/s.

solver.results.report.surface_integrals.area_weighted_avg(
    surface_names=["pressure-outlet-9"],
    report_of="velocity-magnitude",
    write_to_file=True,
    file_name="avg-exit-vel.txt",
)
with open(working_dir / "avg-exit-vel.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Write case file
# ~~~~~~~~~~~~~~~

solver.file.write_case(file_name="gascomb1.cas.h5")

###############################################################################
# NOx prediction
# --------------
# Next, we will activate NOx pollutant models and model the NOx produced by
# the combustor. At the time of writing, NOx models can only be configured
# through the TUI.
#
# Activate NOx model
# ~~~~~~~~~~~~~~~~~~

solver.tui.define.models.nox("yes")

###############################################################################
# Configure NOx chemistry
# ~~~~~~~~~~~~~~~~~~~~~~~
# Set the following NOx chemistry settings:
#
# - Enable thermal NOx pathway
#    - Partial equilibrium model for oxygen radicals ([O])
#    - No model for hydroxyl radicals ([OH])
# - Enable prompt NOx pathway
# - Set methane as the fuel species
# - Set fuel carbon number to 1
# - Set equivalence ratio to 0.76

solver.tui.define.models.nox_parameters.nox_chemistry(
    "yes",  # Enable thermal NOx
    "1",  # Partial equilibrium model for [O]
    "0",  # No model for [OH]
    "yes",  # Enable prompt NOx
    "no",  # Disable fuel NOx
    "1",  # 1 fuel stream
    '"ch4"',  # Add [CH4] fuel species
    '""',  # Finish adding fuel species
    "no",  # Do not remove fuel species from list
    "1",  # Set fuel carbon number to 1
    "0.76",  # Set equivalence ratio to 0.76
    "no",  # No N2O path
    "no",  # No reburn
    "no",  # No SNCR
)

###############################################################################
# Configure NOx-turbulence interaction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the following NOx-turbulence interaction settings:
#
# - Configure PDF
#    - Set mode to ``temperature``
#    - Set number of points to 20
#    - Set type to ``beta``
# - Set temperature variance to ``transported``
# - Set Tmax option to ``global-tmax``

solver.tui.define.models.nox_parameters.nox_turbulence_interaction(
    "yes",  # Enable NOx-turbulence interaction
    "1",  # Set PDF mode to 'temperature'
    "20",  # Set number of PDF points to 20
    "0",  # Set PDF type to 'beta'
    "1",  # Set temperature variance to 'transported'
    "0",  # Set Tmax option to 'global-tmax'
    "yes",  # Keep default for accurate PDF integration
)

###############################################################################
# Turn on pollutant equations only
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Since the flow has already been calculated, we will only turn on the
# equations relevant to pollutant formation.

eqns = solver.solution.controls.equations

# Turn off all equations
for eqn_key in eqns.keys():
    eqns[eqn_key] = False

# Turn on pollutant and temperature variance equations
eqns["pollutant-0"] = True
eqns["tvar"] = True

###############################################################################
# Set pollutant convergence criterion
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the pollutant residual convergence criterion to :math:`10^{-6}`.

solver.solution.monitor.residual.equations["pollut_no"].absolute_criteria = 1e-6

###############################################################################
# Solve 25 iterations
# ~~~~~~~~~~~~~~~~~~~
# Run the solution for 25 iterations to calculate NOx production.

solver.solution.run_calculation.iterate(iter_count=25)

###############################################################################
# Write case and data files
# ~~~~~~~~~~~~~~~~~~~~~~~~~

solver.file.write_case_data(file_name="gascomb2.cas.h5")

###############################################################################
# Create and render nitric oxide mass fraction contour
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the mass fraction of nitric oxide, display it, then
# export the image for inspection.

graphics.contour["contour-no-mass-fraction"] = {
    "field": "mf-pollut-pollutant-0",
    "filled": False,
}
graphics.contour["contour-no-mass-fraction"].display()
graphics.picture.save_picture(
    file_name="contour-no-mass-fraction.png",
)

###############################################################################
# Mass fraction of nitric oxide:
#
# .. image:: ../../_static/combustor_contour-no-mass-fraction.png

###############################################################################
# Report mass-weighted average outlet nitric oxide mass fraction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the mass-weighted average of the outlet mass fraction of nitric
# oxide and report it in the file ``avg-exit-no-mf.txt``. It should be
# approximately 0.00445.

solver.results.report.surface_integrals.mass_weighted_avg(
    surface_names=["pressure-outlet-9"],
    report_of="mf-pollut-pollutant-0",
    write_to_file=True,
    file_name="avg-exit-no-mf.txt",
)
with open(working_dir / "avg-exit-no-mf.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Write case file
# ~~~~~~~~~~~~~~~

solver.file.write_case(file_name="gascomb2.cas.h5")

###############################################################################
# Model thermal NOx only
# ~~~~~~~~~~~~~~~~~~~~~~
# To determine the contribution of thermal NOx, we will disable the prompt NOx
# model.

solver.tui.define.models.nox_parameters.nox_chemistry(
    "yes",  # Enable thermal NOx
    "1",  # Partial equilibrium model for [O]
    "0",  # No model for [OH]
    "no",  # Disable prompt NOx
    "no",  # Disable fuel NOx
    "no",  # No N2O path
    "no",  # No reburn
    "no",  # No SNCR
)

###############################################################################
# Solve 25 iterations
# ~~~~~~~~~~~~~~~~~~~
# Run the solution for 25 iterations to calculate thermal NOx production.

solver.solution.run_calculation.iterate(iter_count=25)

###############################################################################
# Create and render nitric oxide mass fraction contour
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the mass fraction of nitric oxide with only thermal NOx,
# display it, then export the image for inspection.

graphics.contour["contour-no-mass-fraction"].display()
graphics.picture.save_picture(
    file_name="contour-thermal-no-mass-fraction.png",
)

###############################################################################
# Mass fraction of nitric oxide formed by the thermal NOx mechanism:
#
# .. image:: ../../_static/combustor_contour-thermal-no-mass-fraction.png

###############################################################################
# Report mass-weighted average outlet nitric oxide mass fraction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the mass-weighted average of the outlet mass fraction of nitric
# oxide with only thermal NOx and report it in the file
# ``avg-exit-thermal-no-mf.txt``. It should be approximately 0.00441.

solver.results.report.surface_integrals.mass_weighted_avg(
    surface_names=["pressure-outlet-9"],
    report_of="mf-pollut-pollutant-0",
    write_to_file=True,
    file_name="avg-exit-thermal-no-mf.txt",
)
with open(working_dir / "avg-exit-thermal-no-mf.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Write case and data files
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Write the case and data files for the thermal NOx-only calculation.

solver.file.write_case_data(file_name="gascomb2-thermal.cas.h5")

###############################################################################
# Model prompt NOx only
# ~~~~~~~~~~~~~~~~~~~~~
# To determine the contribution of prompt NOx, we will disable the thermal NOx
# model and re-enable the prompt NOx model.

solver.tui.define.models.nox_parameters.nox_chemistry(
    "no",  # Disable thermal NOx
    "yes",  # Enable prompt NOx
    "no",  # Disable fuel NOx
    "1",  # 1 fuel stream
    '""',  # Keep default [CH4] fuel species
    "no",  # Do not remove fuel species from list
    "1",  # Set fuel carbon number to 1
    "0.76",  # Set equivalence ratio to 0.76
    "no",  # No N2O path
    "no",  # No reburn
    "no",  # No SNCR
)

###############################################################################
# Solve 25 iterations
# ~~~~~~~~~~~~~~~~~~~
# Run the solution for 25 iterations to calculate prompt NOx production.

solver.solution.run_calculation.iterate(iter_count=25)

###############################################################################
# Create and render nitric oxide mass fraction contour
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the mass fraction of nitric oxide with only prompt NOx,
# display it, then export the image for inspection.

graphics.contour["contour-no-mass-fraction"].display()
graphics.picture.save_picture(
    file_name="contour-prompt-no-mass-fraction.png",
)

###############################################################################
# Mass fraction of nitric oxide formed by the prompt NOx mechanism:
#
# .. image:: ../../_static/combustor_contour-prompt-no-mass-fraction.png

###############################################################################
# Report mass-weighted average outlet nitric oxide mass fraction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Calculate the mass-weighted average of the outlet mass fraction of nitric
# oxide with only prompt NOx and report it in the file
# ``avg-exit-prompt-no-mf.txt``. It should be approximately
# :math:`9.87 \times 10^{-5}`.

solver.results.report.surface_integrals.mass_weighted_avg(
    surface_names=["pressure-outlet-9"],
    report_of="mf-pollut-pollutant-0",
    write_to_file=True,
    file_name="avg-exit-prompt-no-mf.txt",
)
with open(working_dir / "avg-exit-prompt-no-mf.txt", "r") as f:
    txt = f.read()
    print(txt)

###############################################################################
# Create custom field function for ppm concentration of nitric oxide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a custom field function to calculate the concentration of nitric oxide
# in parts per million (ppm).

solver.tui.define.custom_field_functions.define(
    '"no-ppm"',
    '"molef_pollut_pollutant_0*10^6/(1 - molef_h2o)"',
)

###############################################################################
# Create and render nitric oxide ppm concentration contour
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour of the ppm concentration of nitric oxide formed by the
# prompt NOx mechanism, display it, then export the image for inspection.

graphics.contour["contour-no-ppm"] = {
    "field": "no-ppm",
    "filled": False,
}
graphics.contour["contour-no-ppm"].display()
graphics.picture.save_picture(
    file_name="contour-prompt-no-ppm.png",
)

###############################################################################
# ppm concentration of nitric oxide formed by the prompt NOx mechanism:
#
# .. image:: ../../_static/combustor_contour-prompt-no-ppm.png

###############################################################################
# Write case and data files
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Write the case and data files for the prompt NOx-only calculation.

solver.file.write_case_data(file_name="gascomb2-prompt.cas.h5")

###############################################################################
# Exit Fluent
# -----------

solver.exit()
