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
        print("error: invalid arguments")
        sys.exit(1)

    # print arguments and env car
    print("enter script")
    print("    ARGUMENT = %s" % ARGUMENT)
    print("    VARWORLD = %s" % VARWORLD)
    print("exit script")

    # create file
    with open(os.path.join("data_output", FILENAME + ".txt"), "w") as fid:
        fid.write("ARGUMENT = %s\n" % ARGUMENT)
        fid.write("VARWORLD = %s\n" % VARWORLD)

    sys.exit(0)
