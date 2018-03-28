This folder contains files for analyzing the usage of building resources and simulating alternative service-oriented scenarios.

The python file buildingsUsage.py analyzes the building usage csv file. This file must be placed in this directory after cloning the repository. The .gitignore file will prevent any csv, json or geojson files in this directory from being git controlled or stored on the remote server.

The outputs of the buildingsUsage.py script will be stored in the /Web/prepared directory. These json files will similary be ignored by git.

The web folder contains a webtool for visualising the results of the simulated scenarios.
