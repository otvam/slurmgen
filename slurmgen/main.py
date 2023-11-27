"""
User script for creating slurm jobs.
The job name is giving as an input argument.
"""

import sys
import os.path
import subprocess


def _write_header(fid, tag, filename_log, pragmas):
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

    # write job name
    fid.write('#SBATCH --job-name="%s"\n' % tag)
    fid.write('#SBATCH --output="%s"\n' % filename_log)
    for tag, val in pragmas.items():
        fid.write('#SBATCH --%s="%s"\n' % (tag, val))
    fid.write('\n')


def _write_summary(fid, tag, filename_log, filename_slurm):
    # write param
    fid.write('echo "==================== PARAM"\n')
    fid.write('echo "TAG          : %s"\n' % tag)
    fid.write('echo "LOG FILE     : %s"\n' % filename_log)
    fid.write('echo "SLURM FILE   : %s"\n' % filename_slurm)
    fid.write('\n')

    # write info
    fid.write('echo "==================== INFO"\n')
    fid.write('echo "HOSTNAME     : `hostname`"\n')
    fid.write('echo "DATE         : `date`"\n')
    fid.write('\n')

    # write slurm
    fid.write('echo "==================== SLURM"\n')
    fid.write('echo "JOB ID       : $SLURM_JOB_ID"\n')
    fid.write('echo "JOB NAME     : $SLURM_JOB_NAME"\n')
    fid.write('echo "JOB NODE     : $SLURM_JOB_NODELIST"\n')
    fid.write('\n')


def _write_environment(fid, folder_delete, folder_create, var):
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


def _write_command(fid, command):
    # extract data
    tag = command["tag"]
    executable = command["executable"]
    arguments = command["arguments"]

    # write command
    fid.write('echo "==================== RUN: %s"\n' % tag)
    if arguments:
        # parse arguments
        arg_all = ['"' + tmp + '"' for tmp in arguments]
        arg_all = " ".join(arg_all)

        # write command
        fid.write('%s %s\n' % (executable, arg_all))
    else:
        fid.write('%s\n' % executable)
    fid.write('\n')


def _generate_file(tag, filename_slurm, filename_log, env, job):
    # extract env
    var = env["var"]
    folder_delete = env["folder_delete"]
    folder_create = env["folder_create"]

    # extract job
    pragmas = job["pragmas"]
    commands = job["commands"]

    # write the data
    with open(filename_slurm, "w") as fid:
        # write shebang
        fid.write('#!/bin/bash\n')
        fid.write('\n')

        # write pragma
        _write_header(fid, tag, filename_log, pragmas)

        # write script header
        fid.write('echo "================================= SLURM START"\n')
        fid.write('\n')

        # write summary
        _write_summary(fid, tag, filename_log, filename_slurm)

        # write environment
        _write_environment(fid, folder_delete, folder_create, var)

        # write the commands
        for tmp in commands:
            _write_command(fid, tmp)

        # end script footer
        fid.write('echo "======================================== SLURM END"\n')
        fid.write('exit 0\n')


def run_data(tag, control, env, job):
    # extract
    overwrite = control["overwrite"]
    sbatch = control["sbatch"]
    folder = control["folder"]

    # get filenames
    filename_slurm = os.path.join(folder, tag + ".slm")
    filename_log = os.path.join(folder, tag + ".log")

    # remove old files
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

    # check output files
    print("info: check files")
    if os.path.isfile(filename_slurm):
        print("error: slurm file already exists", file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(filename_log):
        print("error: log file already exists", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    # create the slurm file
    print("info: generate Slurm file")
    _generate_file(tag, filename_slurm, filename_log, env, job)

    # submit the job
    if sbatch:
        print("info: submit Slurm job")
        try:
            subprocess.run(["sbatch", filename_slurm], check=True)
        except OSError:
            print("error: sbatch error", file=sys.stderr)
            sys.exit(1)
