#! /bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
NVIM_RPLUGIN_LOCATION="$HOME/.config/nvim/rplugin/python"
UNINSTALL_OPTION="--uninstall"

function install() {
  mkdir -p $NVIM_RPLUGIN_LOCATION
  ln -s $SCRIPTPATH/tandem_lib $NVIM_RPLUGIN_LOCATION/tandem_lib
  ln -s $SCRIPTPATH/tandem_neovim.py $NVIM_RPLUGIN_LOCATION/tandem_neovim.py

  echo "Symlinks created! Please open nvim and run :UpdateRemotePlugins to complete the install."
}

function uninstall() {
  rm $NVIM_RPLUGIN_LOCATION/tandem_lib
  rm $NVIM_RPLUGIN_LOCATION/tandem_neovim.py

  echo "Symlinks removed. Please open nvim and run :UpdateRemotePlugins to remove the plugin's bindings."
}

if [ "$1" == "$UNINSTALL_OPTION" ] ; then
  uninstall
else
  install
fi
