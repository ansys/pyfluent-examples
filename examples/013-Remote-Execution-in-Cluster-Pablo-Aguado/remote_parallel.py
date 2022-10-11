"""
Simulation Examples
===================
These examples show you how you can use Fluent capabilities from Python to perform
Fluent simulations. This includes geometry import, Fluent's meshing workflows,
setting up and running the solver, and reviewing the results using Fluent's
postprocessing capabilities.
"""

# # Run Remote on Linux
#
# # Requirements to run this example
# #  - Passwordless SSH connection to remote Linux machine
# #  - Remote display capabilities (Linux server)
#
# import os
# import time
#
# import ansys.fluent.core as pyfluent
#
# # Module declaration
# import paramiko
# from paramiko_expect import SSHClientInteraction  # noqa: F401
#
# # Global variable setup
# paramiko.util.log_to_file("linux_server.log")
#
# # Local side
# key_path = r"C:\Users\paguado\.ssh\id_rsa"
# local_dir = r"D:\AFT\PyFluent\py_fluent\remote"
#
# # Server side
# user = "paguado"
# server = "ottvnc15.ansys.com"
# remote_machine = "ottvnc15.ansys.com"
# remote_dir = r"/lus01/paguado/PyFluent/examples/remote"
# port = 22
# display = "ottvnc15:1.0"  # This variable obtained at the server using 'echo $DISPLAY'
# executable = "/ott/apps/daily_builds/linx64/v222_Certified_Daily/ansys_inc/v222/fluent/bin/fluent"  # noqa: E501
# cores = 28
# squeue = "ottc01"
#
# # Run mode
# # 0 - Batch, 1 - Interactive
# run_mode = 1
#
# # Function declaration
#
#
# def remote_exec(loc_client, cmd):
#     _stdin, _stdout, _stderr = loc_client.exec_command(cmd)
#     return {"stdin": _stdin, "stdout": _stdout.read().decode(), "sterr": _stderr}
#
#
# def loc_path(file):
#     return os.path.join(local_dir, file)
#
#
# def rem_path(file):
#     linux_path = remote_dir + "/" + file
#     return linux_path
#
#
# # Setup remote server ssh and sftp sessions
# os.chdir(local_dir)
#
# # SSH client
# ssh_client = paramiko.client.SSHClient()
#
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
# k = paramiko.RSAKey.from_private_key_file(key_path)
#
# ssh_client.connect(server, username=user, pkey=k)
#
# # SFTP client
# sftp = ssh_client.open_sftp()
#
# # Upload case file to remote server
# case_file = "bkd_facing_step.cas.h5"
# sftp.put(loc_path(case_file), rem_path(case_file))
#
# # Log to remote machine
#
# # Scenario 1: Connect to remote session interactively
#
# # Set remote launcher settings
# if run_mode == 1:
#     launcher = "{0} 3ddp -t{1} -nm -scheduler=slurm -scheduler_queue={2} -sifile=server.txt".format(  # noqa: E501
#         executable, cores, squeue  # noqa: E501
#     )  # noqa: E501
# else:
#     launcher = "{0} 3ddp -t{1} -nm -gu -scheduler=slurm -scheduler_queue={2} -driver opengl -sifile=server.txt".format(  # noqa: E501
#         executable, cores, squeue
#     )
#
# # Setup and run remote session
# remote_server_file = rem_path("server.txt")
# local_server_file = loc_path("server.txt")
#
# # Remove existing server file
# remote_exec(ssh_client, r"rm -f {}".format(remote_server_file))
#
# if run_mode == 1:
#     result = remote_exec(
#         ssh_client,
#         ";".join(["cd %s" % (remote_dir), "setenv DISPLAY %s" % (display), launcher]),
#     )  # noqa: E501
# else:
#     result = remote_exec(ssh_client, ";".join(["cd %s" % (remote_dir), launcher]))
#
# # Attach session
# for i in range(20):
#     try:
#         sftp.get(remote_server_file, local_server_file)
#
#     except OSError:
#         print("Witing to process start...")
#         time.sleep(5)
#
# # session = pyfluent.session.Session.create_from_server_info_file(r'D:\AFT\PyFluent\py_fluent\remote\server.txt')  # noqa: E501
# session = pyfluent.launch_fluent(mode="solver")
#
# if run_mode == 1:
#     fs = session.tui
#
# # Enable trailing from remote session
# # Fluent automatically outputs trn file. Get the latest one
# # result = remote_exec(ssh_client, "ls -t %s*.trn" % (remote_dir))
# # trnfile = os.path.join(remote_dir, result['stdout'].split()[0])
# # interact = SSHClientInteraction(ssh_client, timeout=10, display=False)
#
# # interact.send("tail -f %s" % (trnfile))
#
# # Fluent operations
# # read case
# session.tui.file.read_case(r"bkd_facing_step.cas.h5")
#
# # Set velocity inlet
# session.setup.boundary_conditions.velocity_inlet["inlet"] = {
#     "vmag": {"option": "constant or expression", "constant": 0.5}
# }
#
# # Initialize and run
# session.solution.initialization.standard_initialize()
# session.solution.run_calculation.iterate(number_of_iterations=10)  # 500
#
# # Create velocity contour and save png image
# graphs = session.results.graphics
# graphs.contour["contour-1"] = {
#     "field": "x-velocity",
#     "filled": True,
#     "surfaces_list": ["symmetry1"],
# }  # noqa: E501
# graphs.contour["contour-1"].display()
# graphs.views.restore_view(view_name="front")
# graphs.views.picture_options.driver_options = {"hardcopy_format": "png"}
# graphs.views.save_picture(file_name="velocity_cont.png")
#
# # Exit fluent
# session.exit()
#
# # Download image to local machine
# sftp.get(rem_path("velocity_cont.png"), loc_path("velocity_cont.png"))
#
# # Close agents
# sftp.close()
# ssh_client.close()
