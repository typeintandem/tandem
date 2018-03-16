#! /bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

UNINSTALL_OPTION="--uninstall"

function install() {
  rm -f agent
  rm -f crdt

  ln -s $SCRIPTPATH/../../agent $SCRIPTPATH
  ln -s $SCRIPTPATH/../../crdt $SCRIPTPATH

  apm link .
}

function uninstall() {
  rm -f agent
  rm -f crdt

  apm unlink .
}

if [ "$1" == "$UNINSTALL_OPTION" ] ; then
  uninstall
else
  install
fi
