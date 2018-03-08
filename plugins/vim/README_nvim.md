# Tandem

Tandem is an add-on for your favorite text editor that enables peer-to-peer
collaborative editing across different editors.

This repository contains code for the Neovim plugin. For more details on
Tandem, visit [our website](http://typeintandem.com), or our [mono-repository
containing all other source code.](https://github.com/typeintandem/tandem)

## Installation
To install, you will need to have a copy of the Neovim Python2 client.
```
pip install neovim
```
You must also have `python3` and `node.js` installed for the networking code to
work.

Neovim users have the option of installing in one of the following ways:
- **[Recommended]** Using your favourite plugin manager (e.g. Vundle, vim-plug,
  etc.) Tandem should be compatible with most popular plugin managers
- Installing Tandem directly. You’ll need download this repository to
  `~/.config/nvim/rplugin/python`.

Whether you use a plugin manager or download directly, you will also need to
complete an additional one-time step.  
Tandem uses Neovim remote plugin functionality for thread-safety, so you will
need to:
- launch `nvim`
- run `:UpdateRemotePlugins`
- quit `nvim`

You are now ready to use Tandem!

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

It is recommended to leave the session before exiting neovim, but that process
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
