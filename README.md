# SBB Train Network Analytics

This project is an analysis of the Swiss train network.
We use the official timetable to create the SBB network.

We perform analysis of the graph and community detection techniques, such as Louvain, Girvan-Newman and Leiden.

# Quick Start

This project requires Python 3.10.
The notebooks use the data in `data/` such that the project still works without Neo4j.

You need to install Neo4j to recreate the network edgelist.
Neo4j is used to store the original timetable data.
We query the Swiss train network from Neo4j.

## Python

To install the required Python dependencies, run the following commands:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The Jupyter notebooks contain the various steps of the network analysis.
We provide all the necessary data, such as benchmark results and edgelist in `data/` for convenience.

## Neo4j

To configure the Neo4j database, you need to run the setup script first.
Note that this script has only been tested on Debian-based operating systems.

`setup.sh` downloads the zip dataset from the Open Data Platform Mobility [(download link)](https://opentransportdata.swiss/en/dataset/timetable-2024-gtfs2020/resource/1cb3b923-6f2b-40ee-9a9a-900417e9fda3) and unzips it in the default Neo4j import directory.

Once the script is done running, please run the `create_edgelist.py`.
This Python script queries Neo4j to create the `data/sbb.edgelist` and `data/stations.geojson`.
You must give it your Neo4j username and password as arguments.

```
./setup.sh
python create_edgelist.py <username> <password> # replace with your neo4j username and password!
```

## Plots

The graph visualization on top of the Swiss map uses the GeoPackage data from swisstopo.
The data is available [here](https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d#swissBOUNDARIES3D---Download).
Download the archive containing the file with the `gpkg` extension and decompress it in `data/`.
