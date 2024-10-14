#!/bin/bash
# Script for creating a release:
#   - create a tag
#   - create a release
#   - upload the package
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
  rm -rf slurmgen.egg-info

  # clean version file
  rm -rf version.txt
}

function create_tag {
  echo "======================================================================"
  echo "Create tag"
  echo "======================================================================"

  # create a tag
  git tag -a $VER -m "$MSG"

  # push the tags
  git push origin --tags
}

function create_release {
  echo "======================================================================"
  echo "Create release"
  echo "======================================================================"

  # create a release
  gh release create $VER --title $VER --notes "$MSG"
}

function upload_package {
  echo "======================================================================"
  echo "Upload package"
  echo "======================================================================"

  # create package
  python -m build

  # upload to PyPi
  twine upload dist/*
}

# get the version and commit message
if [ "$#" -eq 2 ]; then
  VER=$1
  MSG=$2
else
  echo "error : usage : run_release.sh VER MSG"
  exit 1
fi

# run the code
clean_data
create_tag
create_release
upload_package

exit 0
