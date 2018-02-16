#!/bin/bash

# Given a destination, this script builds the sublime
# plugin for distribution at the destination. The
# destination supplised should be a local copy of the
# plugin repository.

# NOTE: It is the script invoker's responsibility to make sure all dependencies
# for the crdt have been built, etc.

if [[ "$1" == "" ]]; then
  echo "Please supply a path to the plugin target destination."
  exit
fi

INSTALL_PATH="$1"
SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )

# Clean existing items in plugin path
rm -rf $INSTALL_PATH/agent
rm -rf $INSTALL_PATH/crdt
rm -rf $INSTALL_PATH/enum-dist
rm -f $INSTALL_PATH/*.py
rm -f $INSTALL_PATH/*.sublime-*
rm -f $INSTALL_PATH/README.md

mkdir $INSTALL_PATH/agent/
mkdir $INSTALL_PATH/crdt/

cp -r $SCRIPT_PATH/../../agent/ $INSTALL_PATH/agent/

cp -r $SCRIPT_PATH/../../crdt/ $INSTALL_PATH/crdt/

cd $SCRIPT_PATH/../../plugins/sublime/
cp -r enum-dist/ $INSTALL_PATH/enum-dist/
cp *.py $INSTALL_PATH
cp *.sublime-* $INSTALL_PATH
cp README.md $INSTALL_PATH

# Required by Package Control
touch $INSTALL_PATH/.no-sublime-package
