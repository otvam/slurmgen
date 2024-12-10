"""
Module with base import.
"""

import importlib.resources

# set basic metadata
__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

# get the version number
try:
    filename = importlib.resources.files("slurmgen").joinpath("version.txt")
    with filename.open("r") as fid:
        __version__ = fid.read()
except FileNotFoundError:
    __version__ = 'x.x.x'

# import the script in the namespace
from slurmgen.script import *
