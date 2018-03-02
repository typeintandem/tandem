# Release Scripts
These scripts were created to simplify the release of Tandem plugins.


## Pre-requisites
You should create a `.env` file locally with the credentials for the Tandem
bot.  Contact the Tandem maintainers for access.

## Usage
The only script you'll need to run is the `tandem_release.sh` script. It takes
in the type of plugin to build, and the path to (a clone of) the plugin
repository as arguments.

For example, to build the `vim` plugin, navigate:
```
./tandem__release.sh vim /path/to/vim/repository/clone
```
(Note: You must be on `master` in this repository when committing)

## How it Works
The `tandem_release.sh` script does the following:

1. "Setup": parses the arguments, determines variables required by parts of the script
1. "Prepare": runs a plugin specific `prepare.sh` -- copies the plugin and
   tandem agent code to the plugin repository
2. "Commit": commits the plugin code in the specified repository and pushes it
   to GitHub
3. "Release": runs a helper `release.py` that creates a GitHub release.  Python
   is used to simplify interfacing with the GitHub API.

The Tandem Bot credentials are used to commit and release the plugin. Your (the
script runners) credentials will be used to push the committed code to GitHub.
