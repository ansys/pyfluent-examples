"""
AnsysLab-exhaust-manifold
=========================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# # Exhaust Manifold
#
# This is a demonstration of the setup and solution of a three-dimensional
# turbulent fluid flow in a manifold exhaust system. The manifold configuration
# is encountered in the automotive industry. It is often important to predict
# the flow field in the area of the mixing region in order to properly design
# the junction.
#
# Here we use the fault-tolerant meshing workflow, which unlike the watertight workflow # noqa: E501
# is appropriate for geometries with imperfections, such as gaps and leakages.
#
# Problem Description:
#
# Air flows through the three inlets with a uniform velocity, and then
# exits through the outlet. A small pipe is placed in the main portion of the
# manifold where edge extraction will be considered. There is also a known small
# leakage included that will be addressed in the meshing portion of the tutorial
# to demonstrate the automatic leakage detection aspects of the meshing workflow.
#
# In Fluent Meshing, Fault-tolerant Meshing workflow:
# - Import a CAD geometry and manage individual parts
# - Generate a surface mesh
# - Cap inlets and outlets
# - Extract a fluid region
# - Define leakages
# - Extract edge features
# - Setup size controls
# - Generate a volume mesh
#
# Fluent Solver:
# - Set up appropriate physics and boundary conditions
# - Calculate a solution
# - Review the results of the simulation
#
# One instance of Fluent meshing and multiple instances of Fluent solver are deployed. The start-up # noqa: E501
# procedure is executed in parallel.
#
# Each instance is run in -gu mode, which is now supported, in order to allow the processes # noqa: E501
# to generate and save graphical images. Meshing images are saved and downloaded, and presented # noqa: E501
# in a gallery.
#
# Mesh is sent from meshing to all solvers via parallel file transfer as follows: the
# mesh generated by the meshing process is saved; downloaded from the meshing location; uploaded to each # noqa: E501
# solver location; read into each solver.
#
# Solver runs are then executed in parallels as follows: each solver is set up with different boundary # noqa: E501
# condition data; calculations are performed; results from all solvers are collated, tabulated and # noqa: E501
# plotted (using pandas); results are visualised via a PyFluent package that use PyVista. # noqa: E501

# !pip install ansys-platform-instancemanagement
# !pip install simple_upload_server_client-0.0.1-py3-none-any.whl
# !pip install ansys_fluent_solver-0.7.dev0-py3-none-any.whl

# !pip show ansys-fluent-solver ansys-platform-instancemanagement simple-upload-server-client # noqa: E501

# Function to create a PyFluent session in either meshing or solver mode.

"""
create_session creates a PyFluent session in either meshing or solver mode depending on the # noqa: E501
meshing_mode bool argument. PyPIM is used for instance management, which simplifies configuration # noqa: E501
from the user's standpoint, by fixing a lot of configuration details in the back-end. PyPIM # noqa: E501
also provides access to a file upload/download service, which is used in this demo.
"""

import os
import time

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples, launch_fluent


def create_session(mode):
    session = launch_fluent(cleanup_on_exit=False, mode=mode)
    return session


def launch_meshing():
    return create_session(mode="meshing")


def launch_solver():
    return create_session(mode="solver")


pyfluent.version_info()

# Functions for handling the transfer of mesh from meshing to solver

from ansys.fluent.core.utils.async_execution import asynchronous
from ansys.fluent.core.utils.data_transfer import transfer_case


@asynchronous
def read_mesh_into_solver(file_name, solver_session):
    print("read in solver")
    solver_session.upload(file_path=file_name, remote_file_name=file_name)
    time.sleep(5)
    solver_session.tui.file.read_case(file_name)  # make this asynchronous
    print("have read in solver")


def read_mesh_into_solvers(file_name, solver_sessions):
    reads = []
    for solver_session in solver_sessions:
        reads.append(read_mesh_into_solver(file_name, solver_session))
    for r in reads:
        r.result()


# Functions for displaying the Fluent meshing images
gallery = []


def init_graphics(session):
    session.scheme_eval.string_eval("(cx-set-window 1)")


def meshing_image_filename():
    name = "meshing_image_" + str(meshing_image_filename.index)
    meshing_image_filename.index += 1
    return name


meshing_image_filename.index = 0

import os
import time


def update_meshing_display(session, task_name, retry=0):

    if task_name == "Import CAD and Part Management" and retry == 0:
        session.scheme_eval.string_eval(
            f'(eval \'(meshing-wf-part-management-draw "{task_name}") tgrid-package)'
        )  # noqa: E501

    filename = meshing_image_filename()
    full_filename = filename + ".png"

    session.tui.display.save_picture(filename)
    sleeps = 0
    saved = False
    while (not saved) and (sleeps < 10):
        time.sleep(2)
        # saved = file_service.get_folder_content('data')
        saved = True

    pod_name = "."
    if saved:
        session.download(file_name=full_filename, local_file_path=pod_name)
    downloaded = saved and (full_filename in os.listdir(pod_name))
    print(os.listdir(pod_name))
    print(downloaded)
    print(filename)
    print(full_filename)
    # print(file_service.get_folder_content('data'))
    print(pod_name)
    if downloaded:
        full_path = os.path.join(pod_name, full_filename)
        gallery.append([full_path, task_name])
        import IPython

        return lambda: IPython.display.Image(full_path)
    if retry > 4:
        return None
    retry = retry + 1
    return update_meshing_display(session, task_name, retry)


# Class to define the details of the fault-tolerant meshing for the current problem


class ExhaustFTMWorkflow:
    def __init__(self, launcher):
        self.session = session = launcher()
        self.workflow = session.workflow
        self.PartManagement = session.PartManagement
        self.PMFileManagement = session.PMFileManagement
        self.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
        # init_graphics(session)

    def import_cad(self):
        self.PartManagement.InputFileChanged(
            FilePath=import_filename, IgnoreSolidNames=False, PartPerBody=False
        )
        self.PMFileManagement.FileManager.LoadFiles()
        self.PartManagement.Node["Meshing Model"].Copy(
            Paths=[
                "/dirty_manifold-for-wrapper,"
                + "1/dirty_manifold-for-wrapper,1/main,1",  # noqa: E501
                "/dirty_manifold-for-wrapper,"
                + "1/dirty_manifold-for-wrapper,1/flow-pipe,1",  # noqa: E501
                "/dirty_manifold-for-wrapper,"
                + "1/dirty_manifold-for-wrapper,1/outpipe3,1",  # noqa: E501
                "/dirty_manifold-for-wrapper,"
                + "1/dirty_manifold-for-wrapper,1/object2,1",  # noqa: E501
                "/dirty_manifold-for-wrapper,"
                + "1/dirty_manifold-for-wrapper,1/object1,1",  # noqa: E501
            ]
        )
        self.PartManagement.ObjectSetting["DefaultObjectSetting"].OneZonePer.setState(
            "part"
        )
        task_name, task, set_task_args, execute_task = self._task(
            "Import CAD and Part Management"
        )  # noqa: E501
        set_task_args(
            {
                "Context": 0,
                "CreateObjectPer": "Custom",
                "FMDFileName": import_filename,
                "FileLoaded": "yes",
                "ObjectSetting": "DefaultObjectSetting",
                "Options": {
                    "Line": False,
                    "Solid": False,
                    "Surface": False,
                },
            }
        )
        execute_task()
        return self

    def describe_geometry(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Describe Geometry and Flow"
        )  # noqa: E501
        set_task_args(
            {
                "AddEnclosure": "No",
                "CloseCaps": "Yes",
                "FlowType": "Internal flow through the object",
            }
        )
        task.UpdateChildTasks(SetupTypeChanged=False)
        set_task_args(
            {
                "AddEnclosure": "No",
                "CloseCaps": "Yes",
                "DescribeGeometryAndFlowOptions": {
                    "AdvancedOptions": True,
                    "ExtractEdgeFeatures": "Yes",
                },
                "FlowType": "Internal flow through the object",
            }
        )
        task.UpdateChildTasks(SetupTypeChanged=False)
        execute_task()
        return self

    def cover_openings(self):

        task_name, task, set_task_args, execute_task = self._task(
            "Enclose Fluid Regions (Capping)"
        )  # noqa: E501

        set_task_args(
            {
                "CreatePatchPreferences": {
                    "ShowCreatePatchPreferences": False,
                },
                "PatchName": "inlet-1",
                "SelectionType": "zone",
                "ZoneSelectionList": ["inlet.1"],
            }
        )
        set_task_args(
            {
                "CreatePatchPreferences": {
                    "ShowCreatePatchPreferences": False,
                },
                "PatchName": "inlet-1",
                "SelectionType": "zone",
                "ZoneLocation": [
                    "1",
                    "351.68205",
                    "-361.34322",
                    "-301.88668",
                    "396.96205",
                    "-332.84759",
                    "-266.69751",
                    "inlet.1",
                ],
                "ZoneSelectionList": ["inlet.1"],
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()
        set_task_args({})
        self.workflow.TaskObject["inlet-1"].Execute()
        set_task_args(
            {
                "PatchName": "inlet-2",
                "SelectionType": "zone",
                "ZoneSelectionList": ["inlet.2"],
            }
        )
        set_task_args(
            {
                "PatchName": "inlet-2",
                "SelectionType": "zone",
                "ZoneLocation": [
                    "1",
                    "441.68205",
                    "-361.34322",
                    "-301.88668",
                    "486.96205",
                    "-332.84759",
                    "-266.69751",
                    "inlet.2",
                ],
                "ZoneSelectionList": ["inlet.2"],
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()
        set_task_args({})
        self.workflow.TaskObject["inlet-2"].Execute()
        set_task_args(
            {
                "PatchName": "inlet-3",
                "SelectionType": "zone",
                "ZoneSelectionList": ["inlet"],
            }
        )
        set_task_args(
            {
                "PatchName": "inlet-3",
                "SelectionType": "zone",
                "ZoneLocation": [
                    "1",
                    "261.68205",
                    "-361.34322",
                    "-301.88668",
                    "306.96205",
                    "-332.84759",
                    "-266.69751",
                    "inlet",
                ],
                "ZoneSelectionList": ["inlet"],
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()
        set_task_args({})
        self.workflow.TaskObject["inlet-3"].Execute()
        set_task_args(
            {
                "PatchName": "outlet-1",
                "SelectionType": "zone",
                "ZoneSelectionList": ["outlet"],
                "ZoneType": "pressure-outlet",
            }
        )
        set_task_args(
            {
                "PatchName": "outlet-1",
                "SelectionType": "zone",
                "ZoneLocation": [
                    "1",
                    "352.22702",
                    "-197.8957",
                    "84.102381",
                    "394.41707",
                    "-155.70565",
                    "84.102381",
                    "outlet",
                ],
                "ZoneSelectionList": ["outlet"],
                "ZoneType": "pressure-outlet",
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()
        set_task_args({})
        self.workflow.TaskObject["outlet-1"].Execute()
        return self

    def extract_edge_features(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Extract Edge Features"
        )  # noqa: E501
        set_task_args(
            {
                "ExtractMethodType": "Intersection Loops",
                "ObjectSelectionList": ["flow_pipe", "main"],
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()

        (
            edge_group_task_name,
            _,
            set_edge_group_task_args,
            execute_edge_group_task,
        ) = self._task(
            "edge-group-1"
        )  # noqa: E501
        set_edge_group_task_args(
            {
                "ExtractEdgesName": edge_group_task_name,
                "ExtractMethodType": "Intersection Loops",
                "ObjectSelectionList": ["flow_pipe", "main"],
            }
        )
        set_task_args({})

        execute_edge_group_task()
        return self

    def identify_regions(self):
        task_name, task, set_task_args, execute_task = self._task("Identify Regions")

        set_task_args(
            {
                "SelectionType": "zone",
                "X": 377.322045740589,
                "Y": -176.800676988458,
                "Z": -37.0764628583475,
                "ZoneSelectionList": ["main.1"],
            }
        )
        set_task_args(
            {
                "SelectionType": "zone",
                "X": 377.322045740589,
                "Y": -176.800676988458,
                "Z": -37.0764628583475,
                "ZoneLocation": [
                    "1",
                    "213.32205",
                    "-225.28068",
                    "-158.25531",
                    "541.32205",
                    "-128.32068",
                    "84.102381",
                    "main.1",
                ],
                "ZoneSelectionList": ["main.1"],
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()

        (
            fluid_region_name,
            fluid_region_task,
            set_fluid_region_task_args,
            execute_fluid_region_task,
        ) = self._task(
            "fluid-region-1"
        )  # noqa: E501

        set_fluid_region_task_args(
            {
                "MaterialPointsName": "fluid-region-1",
                "SelectionType": "zone",
                "X": 377.322045740589,
                "Y": -176.800676988458,
                "Z": -37.0764628583475,
                "ZoneLocation": [
                    "1",
                    "213.32205",
                    "-225.28068",
                    "-158.25531",
                    "541.32205",
                    "-128.32068",
                    "84.102381",
                    "main.1",
                ],
                "ZoneSelectionList": ["main.1"],
            }
        )
        set_task_args({})

        execute_fluid_region_task()
        set_task_args(
            {
                "MaterialPointsName": "void-region-1",
                "NewRegionType": "void",
                "ObjectSelectionList": ["inlet-1", "inlet-2", "inlet-3", "main"],
                "X": 374.722045740589,
                "Y": -278.9775145640143,
                "Z": -161.1700719416913,
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()

        set_task_args({})

        _1, _2, _3, execute_void_region_task = self._task("void-region-1")
        execute_void_region_task()
        return self

    def define_leakage_threshold(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Define Leakage Threshold"
        )  # noqa: E501

        set_task_args(
            {
                "AddChild": "yes",
                "FlipDirection": True,
                "PlaneDirection": "X",
                "RegionSelectionSingle": "void-region-1",
            }
        )
        task.AddChildToTask()

        task.InsertCompoundChildTask()

        (
            leakage_task_name,
            leakage_task,
            set_leakage_args,
            execute_leakage_task,
        ) = self._task(
            "leakage-1"
        )  # noqa: E501

        set_leakage_args(
            {
                "AddChild": "yes",
                "FlipDirection": True,
                "LeakageName": leakage_task_name,
                "PlaneDirection": "X",
                "RegionSelectionSingle": "void-region-1",
            }
        )
        set_task_args(
            {
                "AddChild": "yes",
            }
        )

        execute_leakage_task()
        return self

    def update_region_settings(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Update Region Settings"
        )  # noqa: E501
        set_task_args(
            {
                "AllRegionFilterCategories": ["2"] * 5 + ["1"] * 2,
                "AllRegionLeakageSizeList": ["none"] * 6 + ["6.4"],
                "AllRegionLinkedConstructionSurfaceList": ["n/a"] * 6 + ["no"],
                "AllRegionMeshMethodList": ["none"] * 6 + ["wrap"],
                "AllRegionNameList": [
                    "main",
                    "flow_pipe",
                    "outpipe3",
                    "object2",
                    "object1",
                    "void-region-1",
                    "fluid-region-1",
                ],
                "AllRegionOversetComponenList": ["no"] * 7,
                "AllRegionSourceList": ["object"] * 5 + ["mpt"] * 2,
                "AllRegionTypeList": ["void"] * 6 + ["fluid"],
                "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
                "FilterCategory": "Identified Regions",
                "OldRegionLeakageSizeList": [""],
                "OldRegionMeshMethodList": ["wrap"],
                "OldRegionNameList": ["fluid-region-1"],
                "OldRegionOversetComponenList": ["no"],
                "OldRegionTypeList": ["fluid"],
                "OldRegionVolumeFillList": ["hexcore"],
                "RegionLeakageSizeList": [""],
                "RegionMeshMethodList": ["wrap"],
                "RegionNameList": ["fluid-region-1"],
                "RegionOversetComponenList": ["no"],
                "RegionTypeList": ["fluid"],
                "RegionVolumeFillList": ["tet"],
            }
        )
        execute_task()
        return self

    def configure_mesh_control(self):
        self._execute_task("Choose Mesh Control Options")
        return self

    def generate_surface_mesh(self):
        self._execute_task("Generate the Surface Mesh")
        return self

    def update_boundaries(self):
        self._execute_task("Update Boundaries")
        return self

    def add_boundary_layers(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Add Boundary Layers"
        )  # noqa: E501

        task.AddChildToTask()

        task.InsertCompoundChildTask()

        (
            aspect_ratio_name,
            aspect_ratio_task,
            set_aspect_ratio_args,
            execute_aspect_ratio_task,
        ) = self._task(
            "aspect-ratio_1"
        )  # noqa: E501

        set_aspect_ratio_args(
            {
                "BLControlName": aspect_ratio_name,
            }
        )
        set_task_args({})

        execute_aspect_ratio_task()
        return self

    def generate_volume_mesh(self):
        task_name, task, set_task_args, execute_task = self._task(
            "Generate the Volume Mesh"
        )  # noqa: E501
        set_task_args(
            {
                "AllRegionNameList": [
                    "main",
                    "flow_pipe",
                    "outpipe3",
                    "object2",
                    "object1",
                    "void-region-1",
                    "fluid-region-1",
                ],
                "AllRegionSizeList": ["11.33375"] * 7,
                "AllRegionVolumeFillList": ["none"] * 6 + ["tet"],
                "EnableParallel": True,
            }
        )
        execute_task()
        return self

    def _task(self, name):
        task = self.workflow.TaskObject[name]
        set_args = task.Arguments.set_state
        execute = task.Execute
        return name, task, set_args, execute

    def _execute_task(self, name):
        return self.workflow.TaskObject[name].Execute()


from ansys.fluent.core.utils.async_execution import asynchronous


def run_meshing(meshing):
    meshing.import_cad()
    update_meshing_display(meshing.session, "Import CAD and Part Management")
    meshing.describe_geometry().cover_openings()
    update_meshing_display(meshing.session, "Enclose Fluid Regions (Capping)")
    meshing.extract_edge_features().identify_regions().define_leakage_threshold().update_region_settings().configure_mesh_control().generate_surface_mesh().update_boundaries()  # noqa: E501
    update_meshing_display(meshing.session, "Update Boundaries")
    meshing.add_boundary_layers().generate_volume_mesh()
    update_meshing_display(meshing.session, "Generate the Volume Mesh")


@asynchronous
def async_run_meshing(meshing):
    run_meshing(meshing)


@asynchronous
def async_create_meshing(launcher):
    return ExhaustFTMWorkflow(launcher)


# Class to define the details of the solver workflow for the current problem
from ansys.fluent.core.utils.async_execution import asynchronous


class ExhaustFlowSolver:
    def __init__(self, launcher, inlet_velocity, inlet_turbulent_intensity):
        self.session = session = launcher()
        self.solver_tui = session.tui
        self.solver_root = session
        self.inlet_velocity = inlet_velocity
        self.inlet_turbulent_intensity = inlet_turbulent_intensity
        self.mass_flow_rate_results = []
        self.pressure_results = []
        # interior : 'interior--fluid-region-1'
        # wall : 'flow-pipe'
        self.mass_flow_rate_info = [
            ["inlet-1", "inlet-1-mass-flow-rate"],
            ["inlet-2", "inlet-2-mass-flow-rate"],
            ["inlet-3", "inlet-3-mass-flow-rate"],
            ["outlet-1", "outlet-mass-flow-rate"],
        ]
        self.pressure_info = [
            ["inlet-1", "inlet-1-pressure"],
            ["inlet-2", "inlet-2-pressure"],
            ["inlet-3", "inlet-3-pressure"],
            ["flow-pipe", "pipe-pressure"],
        ]
        # velocity-magnitude
        self.velocity_info = [
            ["inlet-1", "inlet-1-velocity"],
            ["inlet-2", "inlet-2-velocity"],
            ["inlet-3", "inlet-3-velocity"],
            ["outlet-1", "outlet-velocity"],
            ["flow-pipe", "pipe-velocity"],
        ]

    def define_units(self):
        self.solver_tui.define.units("length", "mm")

    def enable_energy_model(self):
        self.solver_root.setup.models.energy.enabled = True

    def select_turbulence_model(self):
        self.solver_tui.define.models.viscous.kw_sst("yes")

    def setup_velocity_inlets(self):
        self.solver_tui.define.boundary_conditions.set.velocity_inlet(
            "inlet-1", [], "vmag", "no", 1, "quit"
        )
        self.solver_tui.define.boundary_conditions.copy_bc(
            "inlet-1", "inlet-2", "inlet-3", ()
        )

    def set_inlet_parameters(self):
        for name in ("inlet-1", "inlet-2", "inlet-3"):
            inlet = self.solver_root.setup.boundary_conditions.velocity_inlet[name]
            inlet.vmag = self.inlet_velocity  # noqa: E501
            inlet.turb_intensity = self.inlet_turbulent_intensity

    def setup_pressure_outlet(self):
        self.solver_tui.define.boundary_conditions.set.pressure_outlet(
            "outlet-1", [], "turb-intensity", 5, "quit"
        )
        # self.solver_tui.solve.monitors.residual.plot("yes")

    def setup_field_computations(self):

        report_definitions = self.solver_root.solution.report_definitions

        for bc, flow_rate_name in self.mass_flow_rate_info:
            report_definitions.flux[flow_rate_name] = {}
            report_definitions.flux[flow_rate_name].zone_names = [bc]

        for bc, pressure_name in self.pressure_info:
            report_definitions.surface.create(name=pressure_name)
            report_definitions.surface[pressure_name].report_type = "surface-areaavg"
            report_definitions.surface[pressure_name].surface_names = [bc]
            report_definitions.surface[pressure_name].field = "pressure"

        for bc, velocity_name in self.velocity_info:
            report_definitions.surface.create(name=velocity_name)
            report_definitions.surface[velocity_name].report_type = "surface-areaavg"
            report_definitions.surface[velocity_name].surface_names = [bc]
            report_definitions.surface[velocity_name].field = "velocity-magnitude"

    def compute_fields(self):
        self.mass_flow_rate_results = [
            self.solver_root.solution.report_definitions.compute(
                report_defs=[flow_rate_name]
            )[
                0
            ][  # noqa: E501
                flow_rate_name
            ][
                0
            ]
            for bc, flow_rate_name in self.mass_flow_rate_info
        ]

        self.pressure_results = [
            self.solver_root.solution.report_definitions.compute(
                report_defs=[pressure_name]
            )[
                0
            ][  # noqa: E501
                pressure_name
            ][
                0
            ]
            for bc, pressure_name in self.pressure_info
        ]

        self.velocity_results = [
            self.solver_root.solution.report_definitions.compute(
                report_defs=[velocity_name]
            )[
                0
            ][  # noqa: E501
                velocity_name
            ][
                0
            ]
            for bc, velocity_name in self.velocity_info
        ]

    def initialize(self):
        self.solver_tui.solve.initialize.hyb_initialization()

    def solve(self):
        self.solver_tui.solve.set.number_of_iterations(5)  # (100)
        self.solver_tui.solve.iterate()


@asynchronous
def async_run_solver(solver):
    solver.define_units()
    # solver.enable_energy_model()
    solver.select_turbulence_model()
    solver.setup_velocity_inlets()
    solver.set_inlet_parameters()
    solver.setup_pressure_outlet()
    solver.setup_field_computations()
    solver.initialize()
    solver.solve()
    solver.compute_fields()


def create_solver(launcher, inlet_velocity, inlet_turbulent_intensity):
    return ExhaustFlowSolver(launcher, inlet_velocity, inlet_turbulent_intensity)


@asynchronous
def async_create_solver(launcher, inlet_velocity, inlet_turbulent_intensity):
    return create_solver(launcher, inlet_velocity, inlet_turbulent_intensity)


# Instantiate the meshing workflow object which deploys Fluent meshing

meshing = async_create_meshing(launcher=launch_meshing)

# Meanwhile instantiate and deploy all solvers
inlet_velocities = [1.2, 1.4]
inlet_turbulent_intensities = [0.05, 0.15]
solvers = []
for inlet_velocity in inlet_velocities:
    for inlet_turbulent_intensity in inlet_turbulent_intensities:
        solvers.append(
            async_create_solver(
                launcher=launch_solver,
                inlet_velocity=inlet_velocity,
                inlet_turbulent_intensity=inlet_turbulent_intensity,
            )
        )

# Meanwhile also download exhaust system CAD file from PyFluent examples

from ansys.fluent.core import examples

import_filename = examples.download_file(
    "exhaust_system.fmd", "pyfluent/exhaust_system"
)

# Wait for meshing deployment to complete

meshing = meshing.result()

# And upload CAD file to the meshing instance

import_filename

import os

meshing.session.upload(
    file_path=import_filename, remote_file_name="exhaust_system.fmd"  # noqa: E501
)

# Check existence of the CAD file on the pod
# print(file_service.file_exist(os.path.basename(import_filename)))

# Run all the meshing steps from import CAD through to writing the volume mesh

meshing_run = async_run_meshing(meshing)

# Wait on solver deployment

for i in range(len(solvers)):
    try:
        solvers[i] = solvers[i].result()
    except:
        print("error")

# Wait for the meshing run to complete

meshing_run.result()

# Transfer mesh to solvers in parallel
transfer_case(
    source_instance=meshing.session,
    solvers=[solver.session for solver in solvers],
    file_type="mesh",
    file_name_stem="",
    num_files_to_try=1,
    clean_up_temp_file=False,
    overwrite_previous=False,
)


# Run all solver workflows in parallel
runs = []

for solver in solvers:
    runs.append(async_run_solver(solver))

for run in runs:
    run.result()

# Display the gallery of meshing images

from IPython.display import HTML, display

titles = [f"<td>{image[1]}</td>" for image in gallery]
items = [f"<td><img src={image[0]}></td>" for image in gallery]
display(
    HTML(
        f"<table><tr>{titles[0]}{titles[1]}</tr><tr>{items[0]}{items[1]}</tr><tr>{titles[2]}{titles[3]}</tr><tr>{items[2]}{items[3]}</tr></table>"  # noqa: E501
    )
)

# Check the mesh in the meshing process

meshing.session.tui.mesh.check_mesh()

# Process solver results

mass_flow_results = []
for solver in solvers:
    results_for_solver = [solver.inlet_velocity, solver.inlet_turbulent_intensity]
    results_for_solver.extend(solver.mass_flow_rate_results)
    mass_flow_results.append(results_for_solver)

pressure_results = []
for solver in solvers:
    results_for_solver = [solver.inlet_velocity, solver.inlet_turbulent_intensity]
    results_for_solver.extend(solver.pressure_results)
    pressure_results.append(results_for_solver)

# Display results via pandas - tables and plots
import pandas as pd

mass_flow_frame = pd.DataFrame(
    mass_flow_results,
    columns=[
        "inlet velocity (m/s)",
        "inlet turbulent intensity (%)",
        "inlet-1 mass flow rate (kg/s)",
        "inlet-2 mass flow rate (kg/s)",
        "inlet-3 mass flow rate (kg/s)",
        "outlet mass flow rate (kg/s)",
    ],
)  # noqa: E501
display(mass_flow_frame)
mass_flow_frame.plot.scatter(
    x="inlet velocity (m/s)", y="inlet-1 mass flow rate (kg/s)"
)  # noqa: E501
mass_flow_frame.plot.scatter(
    x="inlet velocity (m/s)", y="inlet-2 mass flow rate (kg/s)"
)  # noqa: E501
mass_flow_frame.plot.scatter(
    x="inlet velocity (m/s)", y="inlet-3 mass flow rate (kg/s)"
)  # noqa: E501
mass_flow_frame.plot.scatter(
    x="inlet velocity (m/s)", y="outlet mass flow rate (kg/s)"
)  # noqa: E501

pressure_frame = pd.DataFrame(
    pressure_results,
    columns=[
        "inlet velocity (m/s)",
        "inlet turbulent intensity (%)",
        "inlet-1 pressure (Pa)",
        "inlet-2 pressure (Pa)",
        "inlet-3 pressure (Pa)",
        "flow-pipe pressure (Pa)",
    ],
)  # noqa: E501
display(pressure_frame)
pressure_frame.plot.scatter(x="inlet velocity (m/s)", y="inlet-1 pressure (Pa)")
pressure_frame.plot.scatter(x="inlet velocity (m/s)", y="inlet-2 pressure (Pa)")
pressure_frame.plot.scatter(x="inlet velocity (m/s)", y="inlet-3 pressure (Pa)")
pressure_frame.plot.scatter(x="inlet velocity (m/s)", y="flow-pipe pressure (Pa)")


# 3d plots with matplotlib

velocity_data = [solver.inlet_velocity for solver in solvers]
intensity_data = [solver.inlet_turbulent_intensity for solver in solvers]
mass_flow_data = [solver.mass_flow_rate_results[3] for solver in solvers]
pressure_data = [solver.pressure_results[3] for solver in solvers]


def make_3d_plot(z_data, z_label):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(velocity_data, intensity_data, z_data)
    ax.set_xlabel("inlet velocity (m/s)")
    ax.set_ylabel("inlet turbulent intensity (%)")
    ax.set_zlabel(z_label)
    return plt


make_3d_plot(mass_flow_data, "outlet mass flow rate (kg/s)").show()

make_3d_plot(pressure_data, "flow-pipe pressure (Pa)").show()

# Display mesh and contour from the solver via PyFluent using PyVista

# display the mesh
from ansys.fluent.visualization.pyvista import Graphics

graphics = Graphics(solvers[0].session)
mesh1 = graphics.Meshes["mesh-1"]
mesh1.show_edges = True
mesh1.surfaces_list = mesh1.surfaces_list.allowed_values
mesh1.display()

# display velocity magnitude contour on all the surfaces

contour1 = graphics.Contours["velocity-contour"]
contour1.field = "velocity-magnitude"
contour1.surfaces_list = contour1.surfaces_list.allowed_values
contour1.display()

contour2 = graphics.Contours["pressure"]
contour2.field = "pressure"
contour2.surfaces_list = contour2.surfaces_list.allowed_values
contour2.display()

# Shut down the Fluent processes
for solver in solvers + [meshing]:
    solver.session._remote_instance.delete()
