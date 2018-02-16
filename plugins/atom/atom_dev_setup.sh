#! /bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

UNINSTALL_OPTION="--uninstall"

function install() {
  uninstall

  ln -s $SCRIPTPATH/../../agent $SCRIPTPATH
  ln -s $SCRIPTPATH/../../crdt $SCRIPTPATH
}

function uninstall() {
  rm -f agent
  rm -f crdt
}

if [ "$1" == "$UNINSTALL_OPTION" ] ; then
  uninstall
else
  install
fi
