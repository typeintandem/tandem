#!/bin/bash

set -e

if [[ "$1" == "" ]]; then
  echo "ERROR: Please supply a path to the plugin target destination."
  exit 1
fi

INSTALL_PATH="$1"

./prepare.sh $INSTALL_PATH
./commit.sh $INSTALL_PATH
./release.sh $INSTALL_PATH
