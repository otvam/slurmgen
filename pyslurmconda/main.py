"""
User script for creating slurm jobs.
The job name is giving as an input argument.
"""

import sys
import json
import os.path
import subprocess


def _write_header(fid, tag, filename_log, resources):
    fid.write('#!/bin/bash\n')
    fid.write('\n')

    # write job name
    fid.write('####################################### sbatch name\n')
    fid.write('\n')
    fid.write('#SBATCH --job-name="%s"\n' % tag)
    fid.write('#SBATCH --output="%s"\n' % filename_log)
    fid.write('\n')

    # write job ressources
    cmd = {
        "time": "time",
        "nb_nodes": "nodes",
        "nb_tasks": "ntasks-per-node",
        "list_nodes": "nodelist",
        "memory": "mem",
    }
    fid.write('####################################### sbatch resources\n')
    fid.write('\n')
    for tag, cmd in cmd.items():
        val = resources[tag]
        if val is not None:
            fid.write('#SBATCH --%s="%s"\n' % (cmd, val))
    fid.write('\n')


def _write_summary(fid, tag, filename_log, filename_slurm):
    fid.write('####################################### summary\n')
    fid.write('\n')

    # write param
    fid.write('echo "==================== PARAM"\n')
    fid.write('echo "TAG          : %s"\n' % tag)
    fid.write('echo "LOG FILE     : %s"\n' % filename_log)
    fid.write('echo "SLURM FILE   : %s"\n' % filename_slurm)
    fid.write('\n')

    # write slurm
    fid.write('echo "==================== SLURM"\n')
    fid.write('echo "JOB ID       : $SLURM_JOB_ID"\n')
    fid.write('echo "JOB NAME     : $SLURM_JOB_NAME"\n')
    fid.write('echo "JOB NODE     : $SLURM_JOB_NODELIST"\n')
    fid.write('\n')


def _write_environment(fid, folder_delete, folder_create, var, conda):
    fid.write('####################################### environment\n')
    fid.write('\n')

    # remove folder
    if folder_delete:
        fid.write('echo "==================== FOLDER DELETE"\n')
        for value in folder_delete:
            fid.write('rm -rf "%s"\n' % value)
        fid.write('\n')

    # create folder
    if folder_create:
        fid.write('echo "==================== FOLDER CREATE"\n')
        for value in folder_create:
            fid.write('mkdir -p "%s"\n' % value)
        fid.write('\n')

    # set env
    if var:
        fid.write('echo "==================== ENV VAR"\n')
        for var, value in var.items():
            fid.write('export %s="%s"\n' % (var, value))
        fid.write('\n')

    # write conda load
    if conda is not None:
        fid.write('echo "==================== CONDA LOAD"\n')
        fid.write('source "%s"\n' % conda["path"])
        fid.write('\n')

        # write conda activate
        fid.write('echo "==================== CONDA ACTIVATE"\n')
        fid.write('conda activate "%s"\n' % conda["name"])
        fid.write('\n')


def _write_command(fid, command):
    # extract data
    exe = command["exe"]
    script = command["script"]
    arg_list = command["arg_list"]

    # write command
    fid.write('####################################### run\n')
    fid.write('\n')
    fid.write('echo "==================== RUN"\n')
    if arg_list:
        # parse arguments
        arg_all = ['"' + arg + '"' for arg in arg_list]
        arg_all = " ".join(arg_all)

        # write command
        fid.write('%s %s %s\n' % (exe, script, arg_all))
    else:
        fid.write('%s %s\n' % (exe, script))
    fid.write('\n')


def _generate_file(tag, filename_slurm, filename_log, env, job):
    # extract env
    var = env["var"]
    folder_delete = env["folder_delete"]
    folder_create = env["folder_create"]
    conda = env["conda"]

    # extract job
    resources = job["resources"]
    command = job["command"]

    # write the data
    with open(filename_slurm, "w") as fid:
        # write pragma
        _write_header(fid, tag, filename_log, resources)

        # write script
        fid.write('####################################### start\n')
        fid.write('\n')
        fid.write('echo "================================= SLURM START"\n')
        fid.write('\n')

        # write payload
        _write_summary(fid, tag, filename_log, filename_slurm)
        _write_environment(fid, folder_delete, folder_create, var, conda)
        _write_command(fid, command)

        # end script
        fid.write('####################################### end\n')
        fid.write('\n')
        fid.write('echo "======================================== SLURM END"\n')
        fid.write('exit 0\n')


def run_data(tag, control, env, job):
    # extract
    overwrite = control["overwrite"]
    sbatch = control["sbatch"]
    folder = control["folder"]

    # create the folders
    if not os.path.isdir(folder):
        os.makedirs(folder)

    # get filenames
    filename_slurm = os.path.join(folder, tag + ".slm")
    filename_log = os.path.join(folder, tag + ".log")

    # remove old files
    if overwrite:
        try:
            os.remove(filename_slurm)
        except FileNotFoundError:
            pass
        try:
            os.remove(filename_log)
        except FileNotFoundError:
            pass

    # check output files
    if os.path.isfile(filename_slurm):
        print("error: slurm file already exists", file=sys.stderr)
        return False
    if os.path.isfile(filename_log):
        print("error: log file already exists", file=sys.stderr)
        return False

    # create the slurm file
    _generate_file(tag, filename_slurm, filename_log, env, job)

    # submit the job
    if sbatch:
        try:
            subprocess.run(["sbatch", filename_slurm], check=True)
        except OSError:
            print("error: sbatch error", file=sys.stderr)
            return False

    return False
