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
import string
import argparse
import traceback
from slurmgen import gen
from slurmgen import run
from slurmgen.error import SlurmGenError


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
        "def_file",
        help="JSON file with the job definition",
        metavar="def_file",
    )

    # add the template options
    parser.add_argument(
        "-tf", "--tmpl_file",
        help="JSON file with template data",
        action="store",
        dest="tmpl_file",
    )
    parser.add_argument(
        "-td", "--tmpl_str",
        help="Key / value with template data",
        action="append",
        dest="tmpl_str",
        nargs=2,
    )

    # add run options
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
        "-d", "--directory",
        help="Change the working directory",
        action="store",
        dest="directory",
    )

    return parser


def _get_template(tmpl_file, tmpl_str):
    """
    Load the template data (from file and from string).

    Parameters
    ----------
    tmpl_file : string
        String with a JSON file containing template data.
    tmpl_str : list
        List with keys/values containing template data.

    Returns
    -------
    tmpl_data : dict
        Dictionary with the parsed template data.
    """

    # init template
    tmpl_data = {}

    # load the template from a file
    if tmpl_file is not None:
        # load the template file
        try:
            with open(tmpl_file, "r") as fid:
                data_raw = fid.read()
        except OSError as ex:
            raise SlurmGenError("error: template file not found: %s" % str(ex))

        # parse the template data
        try:
            tmpl_tmp = json.loads(data_raw)
        except json.JSONDecodeError as ex:
            raise SlurmGenError("error: template file is invalid: %s" % str(ex))

        # check type
        if type(tmpl_tmp) is not dict:
            raise SlurmGenError("error: template file should contain a dict")

        # merge the template data
        tmpl_data = {**tmpl_data, **tmpl_tmp}

    # load the template file
    if tmpl_str is not None:
        tmpl_tmp = {}
        for tag, val in tmpl_str:
            tmpl_tmp[tag] = val

        # merge the template data
        tmpl_data = {**tmpl_data, **tmpl_tmp}

    # check template
    for tag, val in tmpl_data.items():
        if type(tag) != str:
            raise SlurmGenError("error: template substitution should be strings")
        if type(val) != str:
            raise SlurmGenError("error: template substitution should be strings")

    return tmpl_data


def _get_def(def_file, tmpl_data):
    """
    Load the job definition file and run the template.

    Parameters
    ----------
    def_file : string
        String with a JSON file containing the job definition data.
    tmpl_data : dict
        Dictionary with the parsed template data.

    Returns
    -------
    def_data : dict
        Dictionary with the parsed definition data.
    """

    # load the JSON data
    try:
        with open(def_file, "r") as fid:
            data_raw = fid.read()
    except OSError as ex:
        raise SlurmGenError("error: definition file not found: %s" % str(ex))

    # show template content
    if tmpl_data:
        print("info: template content")
        for tag, val in tmpl_data.items():
            print("info: var: \"%s\" => \"%s\"" % (tag, val))

    # apply the template
    try:
        obj = string.Template(data_raw)
        def_data = obj.substitute(tmpl_data)
    except (ValueError, KeyError) as ex:
        raise SlurmGenError("error: template parsing error: %s" % str(ex))

    # load the JSON data
    try:
        def_data = json.loads(def_data)
    except json.JSONDecodeError as ex:
        raise SlurmGenError("error: definition file is invalid: %s" % str(ex))

    return def_data


def run_args(def_file, tmpl_file=None, tmpl_str=None, local=False, cluster=False, directory=None):
    """
    Run the script with arguments.

    Parameters
    ----------
    def_file : string
        String with a JSON file containing the job definition data.
    tmpl_file : string
        String with a JSON file containing template data.
    tmpl_str : list
        List with keys/values containing template data.
    local : bool
        Run (or not) the job locally.
    cluster : bool
        Run (or not) the job on the cluster.
    directory : string
        Change the working directory.
    """

    # save working directory
    cwd = os.getcwd()

    # get template data
    try:
        # change working directory
        if directory is not None:
            os.chdir(directory)

        # get the template data
        tmpl_data = _get_template(tmpl_file, tmpl_str)

        # get the job definition file and apply the template
        def_data = _get_def(def_file, tmpl_data)

        # extract data
        tag = def_data["tag"]
        overwrite = def_data["overwrite"]
        folder = def_data["folder"]
        pragmas = def_data["pragmas"]
        envs = def_data["envs"]
        commands = def_data["commands"]

        # create the Slurm script
        (filename_script, filename_log) = gen.run_data(tag, overwrite, folder, pragmas, envs, commands)

        # run the Slurm script
        run.run_data(filename_script, filename_log, local, cluster)
    finally:
        os.chdir(cwd)


def run_script():
    """
    Entry point for the command line script.

    Require one argument with the JSON file with the job definition.:

    Accept several options:
        - Template
            - "-tf" or "--tmpl_file" JSON file with template data.
            - "-td" or "--tmpl_str" Dictionary with template data.
        - Run options
            - "-l" or "--local" Run the job locally for debugging.
            - "-c" or "--cluster" Run the job on the Slurm cluster.
            - "-d" or "--directory" Change the working directory.
    """

    # get argument parser
    parser = _get_parser()

    # parse the arguments
    args = parser.parse_args()

    # run
    try:
        run_args(
            args.def_file,
            tmpl_file=args.tmpl_file,
            tmpl_str=args.tmpl_str,
            local=args.local,
            cluster=args.cluster,
            directory=args.directory,
        )
    except SlurmGenError as ex:
        print("error: ============== SlurmGen ==============", file=sys.stderr)
        traceback.print_exception(ex, limit=0, chain=False)
        print("error: ============== SlurmGen ==============", file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print("error: ============== Unknown ==============", file=sys.stderr)
        traceback.print_exception(ex, limit=0, chain=False)
        print("error: ============== Unknown ==============", file=sys.stderr)
        sys.exit(1)

    # return
    sys.exit(0)


if __name__ == "__main__":
    run_script()
