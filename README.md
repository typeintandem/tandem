# Tandem

Tandem is a decentralized, collaborative text-editing solution. Tandem works
with native text editors, works across different editors, and uses peer-to-peer
connections to facilitate communication.

Tandem exists as a set of plugins for native text editors. We currently support
Sublime Text 3 and Neovim. We also unofficially support Vim.

Collaborating is as easy as installing the plugin on your editor and creating a
Tandem Session. Invite other people to your session, and get typing in tandem!

## Installation

### Requirements
Tandem is currently supported on Mac OS X - it may work on Linux, but use at
your own risk.  
To use Tandem, your environment must have `python3.6+` and `node.js` installed
(tested and confirmed working on `node.js v7.7.4`).  
`python3.6+` is a requirement for our agent code and `node.js` is required by
our CRDT.

### Plugins
Please follow the installation guides for your plugin of choice:
- [Sublime](https://github.com/typeintandem/sublime)
- [Neovim](https://github.com/typeintandem/nvim)
- [Vim (unofficially supported)](https://github.com/typeintandem/vim)

## How it Works
Tandem is split into four components: the editor plugins, the networking agent,
the conflict-free replicated data type (CRDT) solution, and the rendezvous
server.

### Editor Plugins
The plugins interface with the text buffer in your plugin, detecting local
changes and applying remote changes, and allowing users to create, join and
leave sessions. Each plugin has its own repository and code.

### Agent
The agent establishes connections between other peers connected to your
collaborative session. It takes messages from the editor plugin and broadcasts
them to all peers, and with the help of the CRDT instructs the editor to apply
remote changes to your local text buffer.

### CRDT
The CRDT is used to represent the state of your local document, and transforms
document edits into operations that can be applied remotely, without conflicts.
We submit these conflict-free operations to other peers via the agent.

*Instead of reinventing the wheel and writing the CRDT ourselves, we leveraged
the work done by GitHub's team working on Teletype. We used [their
CRDT](https://github.com/atom/teletype-crdt) under the hood and instead
focussed our efforts on integrating the CRDT with different editors.*

### Rendezvous Server
The rendezvous server is used to help establish peer-to-peer connections. It
server notes the connection details of any peer that joins a session. When any
subsequent peer wants to join, the server provides the connection details of
all other peers in the session so that they can communicate directly with each
other.

**Note: Peer-to-peer connections cannot always be established. As a convenience
to the user, the rendezvous server will also act as a relay to send data
between agents when this happens.**  
If you wish to disable this behaviour, you can do so by disabling the
`USE_RELAY` flag in: `agent/tandem/agent/configuration.py`

## Terms of Service
By using Tandem, you agree that any modified versions of Tandem will not use
the rendezvous server hosted by the owners. You must host and use your own copy
of the rendezvous server. We want to provide a good user experience for Tandem,
and it would be difficult to do that with modified clients as well.

You can launch the rendezvous server by running `python3 ./rendezvous/main.py`.
Change the address of the rendezvous server used by the agent in the
configuration file to point to your server's host. This file is located at:
`agent/tandem/agent/configuration.py`

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
