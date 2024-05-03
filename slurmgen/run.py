"""
Module for running a Slurm script.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import sys
import stat
import os.path
import subprocess


def _run_cmd_raw(command, env):
    """
    Run a Slurm script.

    Parameters
    ----------
    command : list
        Command to be executed.
    env : dict
        Dictionary with the environment variables.
    """

    # run the command
    try:
        process = subprocess.run(
            command,
            env=env,
        )
    except OSError as ex:
        print("error: command not found", file=sys.stderr)
        raise ex

    # check return code
    if process.returncode == 0:
        print("info: valid return code")
    else:
        print("error: invalid return code", file=sys.stderr)
        raise RuntimeError("invalid process")


def _run_cmd_log(command, filename_log, env):
    """
    Run a Slurm script.

    Parameters
    ----------
    command : list
        Command to be executed.
    filename_log : string
        Path of the log file created by during the Slurm job.
    env : dict
        Dictionary with the environment variables.
    """

    # run the command
    try:
        with open(filename_log, "w") as fid:
            process = subprocess.run(
                command,
                env=env,
                stderr=fid,
                stdout=fid,
            )
    except OSError as ex:
        print("error: command not found", file=sys.stderr)
        raise ex

    # check return code
    if process.returncode == 0:
        print("info: valid return code")
    else:
        print("error: invalid return code", file=sys.stderr)
        raise RuntimeError("invalid process")


def run_data(filename_script, filename_log, local, cluster):
    """
    Run a Slurm script.

    Parameters
    ----------
    filename_script : string
        Path of the script controlling the simulation.
    filename_log : string
        Path of the log file created by during the Slurm job.
    local : bool
        Run (or not) the job locally.
    cluster : bool
        Run (or not) the job on the cluster.
    """

    # make the script executable
    st = os.stat(filename_script)
    os.chmod(filename_script, st.st_mode | stat.S_IEXEC)

    # submit Slurm job
    if cluster:
        print("info: run Slurm job")

        # find env
        env = os.environ.copy()

        # find command
        command = ["sbatch", filename_script]

        # run
        _run_cmd_raw(command, env)

    # run locally
    if local:
        print("info: run Shell job")

        # find env
        env = os.environ.copy()
        env["SLURM_JOB_ID"] = "NOT SLURM"
        env["SLURM_JOB_NAME"] = "NOT SLURM"
        env["SLURM_JOB_NODELIST"] = "NOT SLURM"

        # find command
        command = [filename_script]

        # run
        _run_cmd_log(command, filename_log, env)
