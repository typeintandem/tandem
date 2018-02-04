#! /bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
SUBLIME_PACKAGE_LOCATION="/Users/${USER}/Library/Application Support/Sublime Text 3/Packages"
SUBLIME_PLUGIN_LOCATION="/Users/$USER/Library/Application Support/Sublime Text 3/Packages/tandem"

UNINSTALL_OPTION="--uninstall"

function install() {
  uninstall

  mkdir -p "${SUBLIME_PACKAGE_LOCATION}"
  mkdir "${SUBLIME_PLUGIN_LOCATION}"

  ln -s $SCRIPTPATH/../../agent "${SUBLIME_PLUGIN_LOCATION}"
  ln -s $SCRIPTPATH/../../crdt "${SUBLIME_PLUGIN_LOCATION}"
  ln -s $SCRIPTPATH/enum-dist "${SUBLIME_PLUGIN_LOCATION}"
  ln -s $SCRIPTPATH/*.py "${SUBLIME_PLUGIN_LOCATION}"
  ln -s $SCRIPTPATH/*.sublime-* "${SUBLIME_PLUGIN_LOCATION}"
}

function uninstall() {
  rm -rf "${SUBLIME_PLUGIN_LOCATION}"
}

if [ "$1" == "$UNINSTALL_OPTION" ] ; then
  uninstall
else
  install
fi
