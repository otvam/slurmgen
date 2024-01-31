"""
Module for creating a Slurm script.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import sys
import os.path
import shutil
import datetime


def _write_title(fid, tag):
    """
    Write simulation header.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    tag : string
        Name of the job to be created.
    """

    # timing
    cmd_time = '`date -u +"%D %H:%M:%S"`'

    # write script header
    fid.write('echo "================================== %s - %s"\n' % (tag, cmd_time))
    fid.write('\n')


def _write_header(fid, tag, filename_log, pragmas):
    """
    Write the script header.

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

    fid.write('#!/bin/bash\n')
    fid.write('\n')
    fid.write('#SBATCH --job-name="%s"\n' % tag)
    fid.write('#SBATCH --output="%s"\n' % filename_log)
    for tag, val in pragmas.items():
        fid.write('#SBATCH --%s="%s"\n' % (tag, val))
    fid.write('\n')


def _write_summary(fid, tag, filename_script, filename_log):
    """
    Add the different variables to the Slurm script.
    The content of the variables will be added to the log.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    tag : string
        Name of the job to be created.
    filename_script : string
        Path of the script controlling the simulation.
    filename_log : string
        Path of the log file created by during the Slurm job.
    """

    # get current timestamp
    date = datetime.datetime.utcnow()

    # write the job name, log file, and script file
    fid.write('echo "==================== PARAM"\n')
    fid.write('echo "JOB TAG      : %s"\n' % tag)
    fid.write('echo "LOG FILE     : %s"\n' % filename_log)
    fid.write('echo "SCRIPT FILE  : %s"\n' % filename_script)
    fid.write('\n')

    # write data about the job submission
    fid.write('echo "==================== TIME"\n')
    fid.write('echo "DATE GEN     : %s"\n' % date.strftime("%D %H:%M:%S"))
    fid.write('echo "DATE RUN     : `date -u +"%D %H:%M:%S"`"\n')
    fid.write('\n')

    # write the job id, job name, and the assigned node names
    fid.write('echo "==================== SLURM"\n')
    fid.write('echo "JOB ID       : $SLURM_JOB_ID"\n')
    fid.write('echo "JOB NAME     : $SLURM_JOB_NAME"\n')
    fid.write('echo "JOB NODE     : $SLURM_JOB_NODELIST"\n')
    fid.write('\n')


def _write_vars(fid, var):
    """
    Handling of the folders and the environment variables.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    vars : dict
        Dictionary of environment variable to be set and exported.
    """

    if var:
        fid.write('echo "==================== ENV VAR"\n')
        for var, value in var.items():
            fid.write('export %s="%s"\n' % (var, value))
        fid.write('\n')


def _write_commands(fid, commands):
    """
    Add a command to the Slurm script.

    Parameters
    ----------
    fid : file
        File descriptor for the script.
    commands : list
        List of commands to be executed by the job.
    """

    for tmp in commands:
        # extract data
        tag = tmp["tag"]
        executable = tmp["executable"]
        arguments = tmp["arguments"]

        # write command
        fid.write('echo "==================== RUN: %s"\n' % tag)
        if arguments:
            arg_all = ['"' + tmp + '"' for tmp in arguments]
            arg_all = " ".join(arg_all)
            fid.write('%s %s\n' % (executable, arg_all))
        else:
            fid.write('%s\n' % executable)
        fid.write('\n')


def _generate_file(tag, filename_script, filename_log, pragmas, vars, commands):
    """
    Generate and write a Slurm script or a Shell script.

    Parameters
    ----------
    tag : string
        Name of the job to be created.
    filename_script : string
        Path of the script controlling the simulation.
    filename_log : string
        Path of the log file created by during the Slurm job.
    pragmas : dict
        Dictionary with the pragmas controlling the Slurm job.
    vars : dict
        Dictionary of environment variable to be set and exported.
    commands : list
        List of commands to be executed by the job.
    """

    # write the data
    with open(filename_script, "w") as fid:
        # write pragmas
        _write_header(fid, tag, filename_log, pragmas)

        # write script header
        _write_title(fid, tag)

        # write summary of the variables
        _write_summary(fid, tag, filename_script, filename_log)

        # write environment variables
        _write_vars(fid, vars)

        # write the commands to be executed
        _write_commands(fid, commands)

        # end script footer
        _write_title(fid, tag)

        # end script footer
        fid.write('exit 0\n')
        

def run_data(tag, overwrite, folder, pragmas, vars, commands):
    """
    Generate a Slurm script.

    Parameters
    ----------
    tag : string
        Name of the job to be created.
    tag : bool
        Switch controlling if previous script and log should be replaced.
    folder : dict
        Name of the output folder for the script and log files.
        Name of the folders that should be deleted at the start of the job.
        Name of the folders that should be created at the start of the job.
    pragmas : dict
        Dictionary with the pragmas controlling the Slurm job.
    vars : dict
        Dictionary of environment variable to be set and exported.
    commands : list
        List of commands to be executed by the job.
    """

    # extract data
    folder_output = folder["folder_output"]
    folder_delete = folder["folder_delete"]
    folder_create = folder["folder_create"]

    # get filenames
    filename_script = os.path.join(folder_output, tag + ".sh")
    filename_log = os.path.join(folder_output, tag + ".log")

    # remove previous files (if selected)
    if overwrite:
        print("info: remove existing files")
        try:
            os.remove(filename_script)
        except FileNotFoundError:
            pass
        try:
            os.remove(filename_log)
        except FileNotFoundError:
            pass
        try:
            os.makedirs(folder_output)
        except FileExistsError:
            pass

    # check that the output files are not existing
    print("info: check files")
    if os.path.isfile(filename_script):
        print("error: Slurm file already exists", file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(filename_log):
        print("error: log file already exists", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(folder_output):
        print("error: output folder does not exist", file=sys.stderr)
        sys.exit(1)

    # remove folders
    print("info: remove folders")
    for folder in folder_delete:
        try:
            shutil.rmtree(folder)
        except FileNotFoundError:
            pass

    print("info: create folders")
    for folder in folder_create:
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass

    # create the script
    print("info: generate Slurm file")
    _generate_file(tag, filename_script, filename_log, pragmas, vars, commands)

    return filename_script, filename_log
