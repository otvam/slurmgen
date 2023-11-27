"""
Module for creating Slurm script.
    - Create the Slurm script.
    - Run the Slurm script (optional).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import sys
import os.path
import subprocess


def _write_pragmas(fid, tag, filename_log, pragmas):
    """
    Add the Slurm pragmas to the script.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    tag : string
        Name of the job to be created.
    filename_log : string
        Path of the log file created by during the Slurm job.
    pragmas : dict
        Dictionary with the pragmas controlling the Slurm job.
    """

    # check pragmas
    if "job-name" in pragmas:
        print("error: job name is already set by the script", file=sys.stderr)
        sys.exit(1)
    if "output" in pragmas:
        print("error: job log is already set by the script", file=sys.stderr)
        sys.exit(1)
    if "error" in pragmas:
        print("error: job log is already set by the script", file=sys.stderr)
        sys.exit(1)

    # write the different pragmas
    fid.write('#SBATCH --job-name="%s"\n' % tag)
    fid.write('#SBATCH --output="%s"\n' % filename_log)
    for tag, val in pragmas.items():
        fid.write('#SBATCH --%s="%s"\n' % (tag, val))
    fid.write('\n')


def _write_summary(fid, tag, filename_slurm, filename_log):
    """
    Add the different variables to the script.
    The content of the variables will be added to the log.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    tag : string
        Name of the job to be created.
    filename_slurm : string
        Path of the Slurm script to be created by this function.
    filename_log : string
        Path of the log file created by during the Slurm job.
    """

    # write the job name, log file, and script file
    fid.write('echo "==================== PARAM"\n')
    fid.write('echo "TAG          : %s"\n' % tag)
    fid.write('echo "LOG FILE     : %s"\n' % filename_log)
    fid.write('echo "SLURM FILE   : %s"\n' % filename_slurm)
    fid.write('\n')

    # write data about the job submission
    fid.write('echo "==================== INFO"\n')
    fid.write('echo "HOSTNAME     : `hostname`"\n')
    fid.write('echo "DATE         : `date`"\n')
    fid.write('\n')

    # write the job id, job name, and the assigned node names
    fid.write('echo "==================== SLURM"\n')
    fid.write('echo "JOB ID       : $SLURM_JOB_ID"\n')
    fid.write('echo "JOB NAME     : $SLURM_JOB_NAME"\n')
    fid.write('echo "JOB NODE     : $SLURM_JOB_NODELIST"\n')
    fid.write('\n')


def _write_environment(fid, folder_delete, folder_create, var):
    """
    Handling of the folders and the environment variables.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    folder_delete : list
        Name of the folders that should be deleted at the start of the job.
    folder_create : list
        Name of the folders that should be created at the start of the job.
    var : dict
        Dictionary of environment variable to be set and exported.
    """

    # remove folders
    if folder_delete:
        fid.write('echo "==================== FOLDER DELETE"\n')
        for value in folder_delete:
            fid.write('rm -rf "%s"\n' % value)
        fid.write('\n')

    # create folders
    if folder_create:
        fid.write('echo "==================== FOLDER CREATE"\n')
        for value in folder_create:
            fid.write('mkdir -p "%s"\n' % value)
        fid.write('\n')

    # set environment variables
    if var:
        fid.write('echo "==================== ENV VAR"\n')
        for var, value in var.items():
            fid.write('export %s="%s"\n' % (var, value))
        fid.write('\n')


def _write_command(fid, command):
    """
    Add a command to the Slurm script.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    command : dict
        Dictionary describing the command to be added.
    """

    # extract data
    tag = command["tag"]
    executable = command["executable"]
    arguments = command["arguments"]

    # write command
    fid.write('echo "==================== RUN: %s"\n' % tag)
    if arguments:
        arg_all = ['"' + tmp + '"' for tmp in arguments]
        arg_all = " ".join(arg_all)
        fid.write('%s %s\n' % (executable, arg_all))
    else:
        fid.write('%s\n' % executable)
    fid.write('\n')


def _generate_file(tag, filename_slurm, filename_log, env, job):
    """
    Generate and write a Slurm script.

    Parameters
    ----------
    tag : string
        Name of the job to be created.
    filename_slurm : string
        Path of the Slurm script to be created by this function.
    filename_log : string
        Path of the log file created by during the Slurm job.
    env : dict
        Name of the folders that should be deleted at the start of the job.
        Name of the folders that should be created at the start of the job.
        Dictionary of environment variable to be set and exported.
    job : dict
        Dictionary with the pragmas controlling the Slurm job.
        List of commands to be excecuted by the hob.
    """

    # extract data
    var = env["var"]
    folder_delete = env["folder_delete"]
    folder_create = env["folder_create"]

    # extract data
    pragmas = job["pragmas"]
    commands = job["commands"]

    # write the data
    with open(filename_slurm, "w") as fid:
        # write shebang
        fid.write('#!/bin/bash\n')
        fid.write('\n')

        # write pragmas
        _write_pragmas(fid, tag, filename_log, pragmas)

        # write script header
        fid.write('echo "================================= SLURM START"\n')
        fid.write('\n')

        # write summary of the variables
        _write_summary(fid, tag, filename_slurm, filename_log)

        # write environment variables
        _write_environment(fid, folder_delete, folder_create, var)

        # write the commands to be executed
        for tmp in commands:
            _write_command(fid, tmp)

        # end script footer
        fid.write('echo "======================================== SLURM END"\n')
        fid.write('exit 0\n')


def run_data(tag, control, env, job):
    """
    Extract data (config, examples, or documentation).

    Parameters
    ----------
    tag : string
        Name of the job to be created.
    control : dict
        Name of the folder for the script and log files.
        Switch controlling if previous script and log can be replaced.
        Switch controlling if the created script should be submitted to the cluster.
    env : dict
        Name of the folders that should be deleted at the start of the job.
        Name of the folders that should be created at the start of the job.
        Dictionary of environment variable to be set and exported.
    job : dict
        Dictionary with the pragmas controlling the Slurm job.
        List of commands to be excecuted by the hob.
    """

    # extract data
    overwrite = control["overwrite"]
    sbatch = control["sbatch"]
    folder = control["folder"]

    # get filenames
    filename_slurm = os.path.join(folder, tag + ".slm")
    filename_log = os.path.join(folder, tag + ".log")

    # remove previous files (if selected)
    if overwrite:
        print("info: remove existing files")
        try:
            os.remove(filename_slurm)
        except FileNotFoundError:
            pass
        try:
            os.remove(filename_log)
        except FileNotFoundError:
            pass

    # check that the output files are not existing
    print("info: check files")
    if os.path.isfile(filename_slurm):
        print("error: slurm file already exists", file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(filename_log):
        print("error: log file already exists", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    # create the Slurm script
    print("info: generate Slurm file")
    _generate_file(tag, filename_slurm, filename_log, env, job)

    # submit the job (if selected)
    if sbatch:
        print("info: submit Slurm job")
        try:
            subprocess.run(["sbatch", filename_slurm], check=True)
        except OSError:
            print("error: sbatch error", file=sys.stderr)
            sys.exit(1)
