# Tandem

Tandem is an add-on for your favorite text editor that enables peer-to-peer collaborative editing across different editors.

This repository contains code for the Sublime Text 3 plugin. For more details on Tandem, visit [our website](http://typeintandem.com), or our [mono-repository containing all other source code.](https://github.com/typeintandem/tandem)

## Installation
To install, you must have a copy of Sublime Text 3 installed. Older versions of Sublime are not supported.  
You must also have `python3` and `node.js` installed.

Sublime Text 3 users have the option of installing in one of three ways:
- **[Recommended]** Using Package Control, searching for Tandem in the global package list.  
This is the simplest and easiest way to install Tandem.
- Using Package Control, adding this repository as a source. You will then need to install the Tandem package from this repository. Due to name conflicts, you will need to navigate to the default package installation directory (e.g. `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`) and rename the directory from `sublime` to `tandem`.  
Installing from the official source will remove the need to do this.
- Installing manually. Download the code to the Sublime Text 3 packages directory, and place it in a folder called `tandem`.

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
- `view.run_command(“tandem”)` : starts a session and prints the session ID
- `view.run_command(“tandem_connect”, “abcd-1234”)`: joins a tandem session with the specified session ID (in this case, “abcd-1234”)
- `view.run_command(“tandem_stop”)`: leaves an existing Tandem session
- `view.run_command(“tandem_session”)`: displays the current session ID

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
