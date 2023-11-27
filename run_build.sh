#!/bin/bash
# Script for building the Python package:
#   - clean the generated files
#   - build the documentation
#   - build the package
#
# Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

function clean_data {
  echo "======================================================================"
  echo "CLEAN DATA"
  echo "======================================================================"

  # clean package
  rm -rf dist
  rm -rf build
  rm -rf pyslurmconda.egg-info

  # clean version file
  rm -rf version.txt
}

function build_package {
  echo "======================================================================"
  echo "BUILD PACKAGE"
  echo "======================================================================"

  # build package
  python -m build

  # update status
  ret=$(( ret || $? ))
}

# init status
ret=0

# build the documentation
clean_data
build_package

exit $ret
