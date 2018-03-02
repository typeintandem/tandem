#!/bin/bash

# =======================================
#                 Setup
# =======================================
set -e  # terminate script if any command errors

USAGE="Usage:  ./tandem_release <vim|nvim|sublime> /path/to/repo"

if ! [[ "$1" =~ ^(vim|nvim|sublime)$ ]]; then
  echo $USAGE
  echo "ERROR: Please supply a valid plugin type."
  exit 1
fi

if [[ "$2" == "" ]]; then
  echo $USAGE
  echo "ERROR: Please supply a path to the plugin target destination."
  exit 1
fi

RELEASE_SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )

cd $RELEASE_SCRIPT_PATH
MASTER_HASH=$( git rev-parse master )
HASH=$( git rev-parse HEAD )

if [[ $MASTER_HASH != $HASH ]]; then
  echo "ERROR: You must be on master when releasing."
  exit 1
fi

PLUGIN_TYPE="$1"
PLUGIN_TYPE_PATH="./$1/"
TARGET_REPOSITORY_PATH="$2"

# =======================================
#                Prepare
# =======================================
cd ./prepare_scripts
./$PLUGIN_TYPE.sh "../$TARGET_REPOSITORY_PATH"
echo "Plugin files copied and prepared to commit."

# =======================================
#                Commit
# =======================================
cd $RELEASE_SCRIPT_PATH
MONOREPO_HASH=$( git rev-parse master )

cd $TARGET_REPOSITORY_PATH
git add .
CHANGED=$(git diff-index --name-only HEAD --)
if [ -n "$CHANGED" ]; then
  git commit -m "Cut release from $MONOREPO_HASH" --author="Team Lightly <teamlightly@gmail.com>"
  git push origin master  # Repository should have the main remote set to "origin"
  echo "Release $MONOREPO_HASH authored and pushed."
else
  echo "There were no changes to the repository and nothing was committed."
  # Does not exit - there might have been an error in releasing the last commit.
  # Allows the script to be used to retry the release.
fi

# =======================================
#                Release
# =======================================
echo -n "Are you sure you want to continue releasing (y/N)? "
read answer
if [[ $answer != "y" ]] && [[ $answer != "Y" ]] ;then
  exit 1
fi

cd $RELEASE_SCRIPT_PATH
pip install pygithub &
pip install semver &
wait

source .env

cd $TARGET_REPOSITORY_PATH
PLUGIN_REPO_HASH=$( git rev-parse master )

cd $RELEASE_SCRIPT_PATH
python release.py $PLUGIN_TYPE $PLUGIN_REPO_HASH  # python script used to simplify GitHub API usage
