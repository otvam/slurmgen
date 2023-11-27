"""
User script for creating slurm jobs.
The job name is giving as an input argument.
"""

import os
import sys
import json
import argparse
import importlib.resources
from pyslurmconda import main


def _get_version():
    """
    Get the version.

    Returns
    -------
    version : string
        String with the version.
    """

    try:
        with importlib.resources.open_text("pyslurmconda", "version.txt") as file_version:
            version = file_version.read()
    except FileNotFoundError:
        version = 'x.x.x'

    return version


def _get_parser():
    """
    Create a command line parser with a description.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="pyslurmconda",
        description="PySlurmConda - Simple Slurm Manager",
        epilog="Thomas Guillod - Dartmouth College",
        allow_abbrev=False,
    )

    # get version
    version = _get_version()

    # display the version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="PySlurmConda %s" % version,
    )

    # add subparsers
    parser.add_argument(
        "file",
        help="JSON file with the input data",
        metavar="file",
    )

    return parser


def run_script():
    # get parser
    parser = _get_parser()

    # parse the config and get arguments
    args = parser.parse_args()

    # check input file
    if not os.path.isfile(args.file):
        print('error: input file not found', file=sys.stderr)
        sys.exit(1)

    # load the data
    with open(args.file, "r") as fid:
        data = json.load(fid)
        tag = data["tag"]
        control = data["control"]
        env = data["env"]
        job = data["job"]

    # create the Slurm data
    status = main.run_data(tag, control, env, job)

    # return
    sys.exit(int(not status))


if __name__ == "__main__":
    run_script()