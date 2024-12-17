#!/bin/bash
# Script for creating a release:
#   - create a tag
#   - create a release
#   - upload the package
#
# Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

function parse_arg {
  # get the version and release message
  if [[ "$#" -eq 2 ]]
  then
    VER=$(echo $1 | awk '{$1=$1;print}')
    MSG=$(echo $2 | awk '{$1=$1;print}')
  else
    echo "error: usage : run_release.sh VER MSG"
    exit 1
  fi
}

function check_release {
  echo "======================================================================"
  echo "============================== CHECK RELEASE"
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

  # abort in case of failure
  if [[ $ret != 0 ]]
  then
    echo "======================================================================"
    echo "============================== RELEASE FAILURE"
    echo "======================================================================"
    exit $ret
  fi
}

function clean_data {
  echo "======================================================================"
  echo "============================== CLEAN DATA"
  echo "======================================================================"

  # clean package
  rm -rf dist
  rm -rf build
  rm -rf *.egg-info

  # clean version file
  rm -rf version.txt
}

function build_check {
  echo "======================================================================"
  echo "============================== BUILD AND CHECK"
  echo "======================================================================"

  # init status
  ret=0

  # create a temporary tag
  git tag -a $VER -m "$MSG" > /dev/null

  # build the release
  python -m build
  ret=$(( ret || $? ))

  # check the linter
  ruff check --no-cache .
  ret=$(( ret || $? ))

  # check the format
  ruff format --no-cache --check .
  ret=$(( ret || $? ))

  # remove the temporary tag
  git tag -d $VER > /dev/null

  # abort in case of failure
  if [[ $ret != 0 ]]
  then
    echo "======================================================================"
    echo "============================== RELEASE FAILURE"
    echo "======================================================================"
    exit $ret
  fi
}

function upload_pkg {
  echo "======================================================================"
  echo "============================== UPLOAD PACKAGE"
  echo "======================================================================"

  # create a tag
  git tag -a $VER -m "$MSG"

  # push the tag
  git push origin --tags

  # create a release
  gh release create $VER --title $VER --notes "$MSG"

  # upload to PyPI
  twine upload dist/*
}

function ret_collect {
  echo "======================================================================"
  echo "============================== RELEASE SUCCESS"
  echo "======================================================================"
}

# parse the arguments
parse_arg "$@"

# run the code
check_release
clean_data
build_check
upload_pkg

# collect status
ret_collect

exit 0
