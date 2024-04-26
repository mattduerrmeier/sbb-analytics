# SBB Network Analytics

This project is an analysis of the Swiss train network.
We use the official timetable to create the SBB network.
We performs analysis of the graph and community detection techniques.

# Quick Start

This project requires Python 3.10.

Neo4j is required to store to original timetable data and to build the network edgelist.
We will provide the edgelist as well tho avoid installing Neo4j.

## Python

To install the required Python dependencies, run the following commands:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The Jupyter notebooks contains the various steps of the network analysis.

## Neo4j

To setup the Neo4j environment, you need to run the setup script first.
Note that this script has only been tested on Debian-based operating systems.
```
./setup.sh
python create_edgelist.py
```

`setup.sh` download the zip dataset from the [Open data platform mobility](https://opentransportdata.swiss/en/dataset/timetable-2024-gtfs2020/resource/1cb3b923-6f2b-40ee-9a9a-900417e9fda3), and unzips it in the default Neo4j import directory.
The python script queries Neo4j to create the `sbb.edgelist`.
