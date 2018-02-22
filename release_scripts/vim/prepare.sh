#!/bin/bash

# Given a destination, this script builds the sublime plugin for distribution
# at the destination. The destination supplised should be a local copy of the
# plugin repository.

SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )

cd $SCRIPT_PATH
MASTER_HASH=$( git rev-parse master )
HASH=$( git rev-parse HEAD )

if [[ $MASTER_HASH != $HASH ]]; then
  echo "ERROR: You must be on master when preparing a release."
  exit 1
fi

if [[ "$1" == "" ]]; then
  echo "ERROR: Please supply a path to the plugin target destination."
  exit 1
fi

INSTALL_PATH="$1"

# Make sure the path is up-to-date
cd $INSTALL_PATH
git checkout master
git pull origin master
cd $SCRIPT_PATH

# Clean existing items in plugin path
rm -rf $INSTALL_PATH/plugin
rm -f $INSTALL_PATH/*

# Create plugin, lib, agent and crdt subdirectories
mkdir $INSTALL_PATH/plugin/
mkdir $INSTALL_PATH/plugin/tandem_lib/
mkdir $INSTALL_PATH/plugin/tandem_lib/agent/
mkdir $INSTALL_PATH/plugin/tandem_lib/crdt/

# Agent
cp -r $SCRIPT_PATH/../../agent/ $INSTALL_PATH/plugin/tandem_lib/agent/

# CRDT
$(
  cd $SCRIPT_PATH/../../crdt/;
  npm run clean;
  rm -rf node_modules;
  npm install;
  npm run build
)
cp -r $SCRIPT_PATH/../../crdt/ $INSTALL_PATH/plugin/tandem_lib/crdt/

# Sublime specific files
cd $SCRIPT_PATH/../../plugins/vim/
cp tandem_lib/*.py $INSTALL_PATH/plugin/tandem_lib/
cp tandem_vim.vim $INSTALL_PATH/plugin/
cp README_vim.md $INSTALL_PATH/README.md

echo "Release succesfully prepared."
