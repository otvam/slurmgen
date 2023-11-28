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
from slurmgen import main


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
        "file",
        help="JSON file with the input data",
        metavar="file",
    )

    return parser


def run_script():
    """
    Entry point for the command line script.
    Accept a single argument with the path of the JSON file.
    """

    # get argument parser
    parser = _get_parser()

    # parse the arguments
    args = parser.parse_args()

    # check that the JSON file exists
    if not os.path.isfile(args.file):
        print('error: input file not found', file=sys.stderr)
        sys.exit(1)

    # load the data
    with open(args.file, "r") as fid:
        data = json.load(fid)
        tag = data["tag"]
        control = data["control"]
        job = data["job"]

    # create the Slurm script
    main.run_data(tag, control, job)

    # return
    sys.exit(0)


if __name__ == "__main__":
    run_script()