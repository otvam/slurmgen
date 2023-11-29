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
        print("info: submit Slurm job")
        try:
            subprocess.run(["sbatch", filename_script], check=True)
        except OSError:
            print("error: sbatch error", file=sys.stderr)
            sys.exit(1)

    # run locally
    if local:
        print("info: run Shell job")
        try:
            fake_slurm = os.environ.copy()
            fake_slurm["SLURM_JOB_ID"] = "NOT SLURM"
            fake_slurm["SLURM_JOB_NAME"] = "NOT SLURM"
            fake_slurm["SLURM_JOB_NODELIST"] = "NOT SLURM"
            with open(filename_log, "w") as fid:
                subprocess.run(
                    [filename_script],
                    check=True,
                    env=fake_slurm,
                    stderr=fid,
                    stdout=fid,
                )
        except OSError:
            print("error: sbatch error", file=sys.stderr)
            sys.exit(1)
