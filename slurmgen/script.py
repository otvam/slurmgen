"""
User script for creating Slurm script from JSON files.
    - Read the JSON file.
    - Create the Slurm script.
    - Run the Slurm script (optional).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"


import os
import sys
import json
import argparse
from slurmgen import gen
from slurmgen import run


def _get_parser():
    """
    Create a command line parser with a description.

    Returns
    -------
    parser : ArgumentParser
        Command line argument parser object.
    """

    # create the parser
    parser = argparse.ArgumentParser(
        prog="sgen",
        description="SlurmGen - Simple Slurm Manager",
        epilog="Thomas Guillod - Dartmouth College",
        allow_abbrev=False,
    )

    # add the argument
    parser.add_argument(
        "template",
        help="JSON file with the job template",
        metavar="template",
    )
    parser.add_argument(
        "definition",
        help="JSON file with the job definition",
        metavar="definition",
    )
    parser.add_argument(
        "-l", "--local",
        help="Run the job locally for debugging",
        action="store_true",
        dest="local",
    )
    parser.add_argument(
        "-c", "--cluster",
        help="Run the job on the Slurm cluster",
        action="store_true",
        dest="cluster",
    )
    parser.add_argument(
        "-o", "--overwrite",
        help="Overwrite existing files",
        action="store_true",
        dest="cluster",
    )
    parser.add_argument(
        "-t", "--tag",
        help="Overwrite the job name",
        action="store",
        dest="tag",
        default=None,
    )
    parser.add_argument(
        "-ok", "--afterok",
        help="Run after successful dependency",
        action="store",
        dest="afterok",
        default=None,
    )
    parser.add_argument(
        "-any", "--afterany",
        help="Run after terminated dependency",
        action="store",
        dest="afterany",
        default=None,
    )

    return parser


def run_script():
    """
    Entry point for the command line script.

    Require two arguments:
        - JSON file with the job template
        - JSON file with the job definition

    Accept several options:
        - "-l" or "--local" Run the job locally for debugging.
        - "-c" or "--cluster" Run the job on the Slurm cluster.
        - "-o" or "--overwrite" Overwrite existing files.
        - "-t" or "--tag" Overwrite the job name.
        - "-ok" or "--afterok" Run after successful dependency.
        - "-any" or "--afterany" Run after terminated dependency.
    """

    # get argument parser
    parser = _get_parser()

    # parse the arguments
    args = parser.parse_args()

    # check that the JSON file exists
    if not os.path.isfile(args.template):
        print('error: template file not found', file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.definition):
        print('error: definition file not found', file=sys.stderr)
        sys.exit(1)

    # load the template data
    with open(args.template, "r") as fid:
        data = json.load(fid)
        control = data["control"]
        folder = data["folder"]
        pragmas_tmpl = data["pragmas"]
        vars_tmpl = data["vars"]
        pre_proc_commands_tmpl = data["pre_proc_commands"]
        post_proc_commands_tmpl = data["post_proc_commands"]

    # load the definition data
    with open(args.definition, "r") as fid:
        data = json.load(fid)
        tag = data["tag"]
        pragmas_def = data["pragmas"]
        vars_def = data["vars"]
        commands_def = data["commands"]

    # replace tag
    if args.tag is not None:
        tag = args.tag

    # find control
    cluster = control["cluster"] or args.cluster
    local = control["local"] or args.local
    overwrite = control["overwrite"] or args.overwrite
    afterok = args.afterok
    afterany = args.afterany

    # merge
    pragmas = {**pragmas_tmpl, **pragmas_def}
    vars = {**vars_tmpl, **vars_def}
    commands = pre_proc_commands_tmpl + commands_def + post_proc_commands_tmpl

    # create the Slurm script
    (filename_script, filename_log) = gen.run_data(tag, overwrite, folder, pragmas, vars, commands)

    # run the Slurm script
    run.run_data(filename_script, filename_log, local, cluster, afterok, afterany)

    # return
    sys.exit(0)


if __name__ == "__main__":
    run_script()