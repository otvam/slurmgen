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
    with importlib.resources.open_text("slurmgen", "version.txt") as file:
        __version__ = file.read()
except FileNotFoundError:
    __version__ = 'x.x.x'

# import the script in the namespace
from slurmgen.script import *
