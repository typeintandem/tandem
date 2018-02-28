# Release Scripts
These scripts were created to simplify the release of Tandem plugins.


## Pre-requisites
You should create a `.env` file locally with the credentials for the Tandem
bot, and source it.  Contact the Tandem administrators for access.

## Usage
The only scripts you'll need to run are the `tandem_<type>_release.sh` scripts
within each plugins respective subdirectory. They take in the path to (a clone of) the plugin repository as an argument.

For example, to build the `vim` plugin, navigate:
```
cd vim
./tandem_vim_release.sh /path/to/tandem/vim/plugin/repository
```

You must be on `master` in this repository when committing.

## How it Works
Each `tandem_<type>_release.sh` script runs the following three scripts in
sequence. It passes in the plugin path as an argument.

1. prepare.sh -- copies the plugin and tandem agent code to the plugin repository
2. commit.sh (located in `common/`) -- commits the plugin code
3. release.sh -- creates a git tag and GitHub release

The Tandem Bot credentials are used to commit and release the plugin. Your (the
script runners) credentials will be used to push the committed code to GitHub.
