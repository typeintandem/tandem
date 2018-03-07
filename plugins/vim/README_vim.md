# Tandem

Tandem is an add-on for your favorite text editor that enables peer-to-peer
collaborative editing across different editors.

This repository contains code for the Vim plugin. For more details on Tandem,
visit [our website](http://typeintandem.com), or our [mono-repository
containing all other source code.](https://github.com/typeintandem/tandem)

*Note: Vim is not officially supported due to its lack of thread-safety.
Instead we recommend Tandem with Neovim, one of our officially supported
plugins.  
We added functionality to this editor since it was a minimal amount of work to
port the logic - please use at your own risk.*

## Installation
To install, you must have a copy of vim compiled with python installed.  
You must also have `python3` and `node.js` installed.

Vim users have the option of installing in one of the following ways:
- **[Recommended]** Using your favourite plugin manager (e.g. Vundle, vim-plug,
  etc.) Tandem should be compatible with most popular plugin managers
- Installing Tandem directly. You’ll need download this repository. In your
  `~/.vimrc`, make sure you source the `tandem_vim.vim` file:
`source /path/to/tandem/plugin/tandem_vim.vim`

## Usage
Tandem users can choose either start a collaborative session or join an
existing one. Starting a collaborative session will share the contents of your
current buffer. Joining an existing session will open it’s contents in a new
buffer.

Please use one of the following commands:
- `:Tandem` - creates a new tandem session and prints the session ID
- `:Tandem <session_id>` - joins an existing tandem session with the specified
  session ID
- `:TandemStop` - leaves the current session
- `:TandemSession` - prints the current session ID

It is recommended to leave the session before exiting vim, but that process
should be automated.

## License
Copyright (c) 2018 Team Lightly

Licensed under the "Lightly-Modified Apache License", a variant of the Apache
License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. 

See [LICENSE.txt](LICENSE.txt)

This license is essentially the Apache License 2.0, except for an added a
clause that requires you to use your own servers instead of ours if you do
modify Tandem.  
You can also modify this in the configuration file at:
`agent/tandem/agent/configuration.py`

## Authors
Team Lightly  
[Geoffrey Yu](https://github.com/geoffxy), [Jamiboy
Mohammad](https://github.com/jamiboym) and [Sameer
Chitley](https://github.com/rageandqq)

We are a team of senior Software Engineering students at the University of
Waterloo.  
Tandem was created as our [Engineering Capstone Design
Project](https://uwaterloo.ca/capstone-design).
