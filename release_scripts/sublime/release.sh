#!/bin/bash

if [[ "$1" == "" ]]; then
  echo "Please supply a path to the plugin target destination."
  exit
fi

REPO_PATH="$1"
SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )

pip install pygithub &
pip install semver &
wait

source ../.env

cd $REPO_PATH
HASH=$( git rev-parse master )

cd $SCRIPT_PATH
python ../release.py sublime $HASH