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

## Terms of Service
By using Tandem, you agree that any modified versions of Tandem will not use
the rendezvous server hosted by the owners. You must host and use your own copy
of the rendezvous server. We want to provide a good user experience for Tandem,
and it would be difficult to do that with modified clients as well.

You can launch the rendezvous server by running `python3 ./rendezvous/main.py`.
Change the address of the rendezvous server used by the agent in the
configuration file to point to your server's host. This file is located at:
`plugin/tandem_lib/agent/tandem/agent/configuration.py`

## License
Copyright (c) 2018 Team Lightly

See [LICENSE.txt](LICENSE.txt)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0
## Authors
Team Lightly  
[Geoffrey Yu](https://github.com/geoffxy), [Jamiboy
Mohammad](https://github.com/jamiboym) and [Sameer
Chitley](https://github.com/rageandqq)

We are a team of senior Software Engineering students at the University of
Waterloo.  
Tandem was created as our [Engineering Capstone Design
Project](https://uwaterloo.ca/capstone-design).
