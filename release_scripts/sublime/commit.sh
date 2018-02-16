#!/bin/bash

if [[ "$1" == "" ]]; then
  echo "Please supply a path to the plugin target destination."
  exit
fi

INSTALL_PATH="$1"
SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )

cd $SCRIPT_PATH
HASH=$( git rev-parse master )

cd $INSTALL_PATH
git add .
git commit -m "Release version $HASH" --author="Team Lightly <teamlightly@gmail.com>"
git push origin master

echo "Release $HASH authored and pushed."
