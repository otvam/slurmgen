"""
Simple script with a dummy payload for the examples.
    - Read the command line arguments.
    - Read an environment variable.
    - Display the variable content to the console.
    - Write the variable content in a file.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import os
import sys

# get env var
VARWORLD = os.getenv("VARWORLD")


if __name__ == "__main__":
    # parse arguments
    if len(sys.argv) == 3:
        FILENAME = sys.argv[1]
        ARGUMENT = sys.argv[2]
    else:
        print("invalid arguments")
        sys.exit(1)

    # print the variable content
    print("enter script")
    print("    ARGUMENT = %s" % ARGUMENT)
    print("    VARWORLD = %s" % VARWORLD)
    print("exit script")

    # create file with the variable content
    os.makedirs("data_output", exist_ok=True)
    with open(os.path.join("data_output", FILENAME + ".txt"), "w") as fid:
        fid.write("ARGUMENT = %s\n" % ARGUMENT)
        fid.write("VARWORLD = %s\n" % VARWORLD)

    sys.exit(0)
