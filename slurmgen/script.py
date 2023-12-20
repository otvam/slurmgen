"""
User script for creating Slurm script from JSON files.
    - Read the JSON file.
    - Create the Slurm script.
    - Run the Slurm script (optional).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"


import sys
import json
import ast
import string
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
        "-td", "--tmpl_data",
        help="Dictionary with template data",
        action="store",
        dest="tmpl_data",
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

    # add dependency options
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

    Require one argument with the JSON file with the job definition.:

    Accept several options:
        - Template
            - "-tf" or "--tmpl_file" JSON file with template data.
            - "-td" or "--tmpl_data" Dictionary with template data.
        - Run options
            - "-l" or "--local" Run the job locally for debugging.
            - "-c" or "--cluster" Run the job on the Slurm cluster.
            - "-o" or "--overwrite" Overwrite existing files.
            - "-t" or "--tag" Overwrite the job name.
        - Dependency options
            - "-ok" or "--afterok" Run after successful dependency.
            - "-any" or "--afterany" Run after terminated dependency.
    """

    # get argument parser
    parser = _get_parser()

    # parse the arguments
    args = parser.parse_args()

    # load the JSON data
    try:
        with open(args.def_file, "r") as fid:
            def_data = fid.read()
    except OSError:
        print('error: definition file not found', file=sys.stderr)
        sys.exit(1)

    # init template
    tmpl = {}

    # load the template from a file
    if args.tmpl_file is not None:
        # load the template file
        try:
            with open(args.tmpl_file, "r") as fid:
                tmpl_data = fid.read()
        except OSError:
            print('error: template file not found', file=sys.stderr)
            sys.exit(1)

        # parse the template data
        try:
            tmpl_tmp = json.loads(tmpl_data)
        except json.JSONDecodeError as ex:
            print('error: template file is invalid', file=sys.stderr)
            sys.exit(1)

        # merge the template data
        tmpl = {**tmpl, **tmpl_tmp}

    # load the template file
    if args.tmpl_data is not None:
        try:
            tmpl_tmp = ast.literal_eval(args.tmpl_data)
        except (ValueError, TypeError, SyntaxError):
            print('error: template data is invalid', file=sys.stderr)
            sys.exit(1)

        # merge the template data
        tmpl = {**tmpl, **tmpl_tmp}

    # appy the template
    obj = string.Template(def_data)
    def_data = obj.substitute(tmpl)

    # load the JSON data
    try:
        def_data = json.loads(def_data)
    except json.JSONDecodeError as ex:
        print('error: definition file is invalid', file=sys.stderr)
        sys.exit(1)

    # extract data
    tag = def_data["tag"]
    control = def_data["control"]
    folder = def_data["folder"]
    pragmas = def_data["pragmas"]
    vars = def_data["vars"]
    commands = def_data["commands"]

    # replace tag
    if args.tag is not None:
        tag = args.tag

    # find control
    cluster = control["cluster"] or args.cluster
    local = control["local"] or args.local
    overwrite = control["overwrite"] or args.overwrite

    # dependency options
    afterok = args.afterok
    afterany = args.afterany

    # create the Slurm script
    (filename_script, filename_log) = gen.run_data(tag, overwrite, folder, pragmas, vars, commands)

    # run the Slurm script
    run.run_data(filename_script, filename_log, local, cluster, afterok, afterany)

    # return
    sys.exit(0)


if __name__ == "__main__":
    run_script()