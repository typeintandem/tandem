# Tandem

Tandem is an add-on for your favorite text editor that enables peer-to-peer collaborative editing across different editors.

This repository contains code for the Sublime Text 3 plugin. For more details on Tandem, visit [our website](http://typeintandem.com), or our [mono-repository containing all other source code.](https://github.com/typeintandem/tandem)

## Installation
To install, you must have a copy of Sublime Text 3 installed. Older versions of Sublime are not supported.  
You must also have `python3` and `node.js` installed.

Sublime Text 3 users have the option of installing in one of three ways:
-  Using Package Control, searching for Tandem in the global package list.  
This is the simplest and easiest way to install Tandem.  
*Note: This option doesn't work yet as we're [waiting to be accepted into the
official package control
repository](https://github.com/wbond/package_control_channel/pull/6986)*
- **[Recommended]** Using Package Control, adding this repository as a source. You will then need to install the Tandem package from this repository. Due to name conflicts, you will need to navigate to the default package installation directory (e.g. `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`) and rename the directory from `sublime` to `tandem`.  
Installing from the official source will remove the need to do this.
- Installing manually. Clone the repository to the Sublime Text 3 packages directory, and place it in a folder called `tandem`.

## Usage
Tandem users can choose either start a collaborative session or join an existing one.

- To start your session, select `Tandem > Start Session` from the menu or the command palette. This will create a session and give you a session ID you can share with participants you’d like to invite. Content in your buffer will be shared, so open a new view before creating a session if you don’t wish to share the contents. 
- To join an existing session, select `Tandem > Join Existing Session` from the menu or command palette. Enter the session ID given to you, press enter, and begin collaborating! Your session will be opened in a new view.
- Any user can leave a session at any time - all other peers can continue working in the session. Simply use `Tandem > Leave Session` from the menu or command palette.
- If you want to find your session ID again, select `Tandem > Show Session ID` to view your session ID.

**Note: You MUST leave an active session before exiting Sublime Text! Due to editor limitations, failure to do so will cause the networking agent to remain alive and consume system resources.** 

### Advanced Usage
While commands have GUI hooks (menu option, command palette shortcut), advanced users can also start, join and leave sessions using commands.

Open the command palette (Ctrl + `). From there, use one of the following commands:
- `view.run_command("tandem")` : starts a session and prints the session ID
- `view.run_command("tandem_connect", "abcd-1234")`: joins a tandem session with the specified session ID (in this case, "abcd-1234")
- `view.run_command("tandem_stop")`: leaves an existing Tandem session
- `view.run_command("tandem_session")`: displays the current session ID

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
