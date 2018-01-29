all: dir agent crdt deps plugin
.PHONY: all

dir:
	sudo mkdir -p /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages
	sudo mkdir -p /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem
	sudo mkdir -p /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/agent
	sudo mkdir -p /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/crdt
	sudo mkdir -p /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/enum-dist

agent:
	sudo cp -r ../../agent/ /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/agent

crdt:
	sudo cp -r ../../crdt/ /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/crdt

deps:
	sudo cp -r ./enum-dist/ /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem/enum-dist

plugin:
	sudo cp *.py /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem

clean:
	sudo rm -rf /Users/${USER}/Library/Application\ Support/Sublime\ Text\ 3/Packages/tandem
