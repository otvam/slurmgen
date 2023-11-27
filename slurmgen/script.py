"""
User script for creating slurm jobs.
The job name is giving as an input argument.
"""

import os
import sys
import json
import argparse
from slurmgen import main


def _get_parser():
    """
    Create a command line parser with a description.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="slurmgen",
        description="SlurmGen - Simple Slurm Manager",
        epilog="Thomas Guillod - Dartmouth College",
        allow_abbrev=False,
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
    main.run_data(tag, control, env, job)

    # return
    sys.exit(0)


if __name__ == "__main__":
    run_script()