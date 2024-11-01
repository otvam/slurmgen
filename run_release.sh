#!/bin/bash
# Script for creating a release:
#   - create a tag
#   - create a release
#   - upload the package
#
# Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

function check_release {
  echo "======================================================================"
  echo "CHECK RELEASE"
  echo "======================================================================"

  # init status
  ret=0

  # check the version number
  rx='^([0-9]+)\.([0-9]+)\.([0-9]+)$'
  if ! [[ $VER =~ $rx ]]
  then
    echo "error: invalid version number format"
    ret=1
  fi

  # check the release message
  rx='^ *$'
  if [[ $MSG =~ $rx ]]
  then
    echo "error: invalid release message format"
    ret=1
  fi

  # check git branch name
  if [[ $(git rev-parse --abbrev-ref HEAD) != "main" ]]
  then
    echo "error: release should be done from main"
    ret=1
  fi

  # check git tag existence
  if [[ $(git tag -l $VER) ]]
  then
    echo "error: version number already exists"
    ret=1
  fi

  # check git repository status
  if ! [[ -z "$(git status --porcelain)" ]]
  then
    echo "error: git status is not clean"
    ret=1
  fi

  # check status
  if [[ $ret != 0 ]]
  then
    exit $ret
  fi
}

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
check_release
clean_data
create_tag
create_release
upload_package

exit 0
