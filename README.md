# Swiss Train Network Analytics

This project is an analysis of the Swiss train network.
We use the timetable of all Swiss public transport to create the train network.

In this project, we construct the Swiss train network, visualize and explore the graph.
We do community detection with Louvain, Girvan-Newman and Leiden, and benchmark these techniques.

# Quick Start

The [first section](#python-only) covers how to install Python dependencies.
This step is **required** for both the Python-only and the full pipeline.
The notebooks use the data in `data/` such that the project can still work without Neo4j.

The [second section](#neo4j-full-pipeline) covers how to reproduce the full pipeline with pre-processing steps.
For this version of the project, you need to install Neo4j.
Neo4j is used to store the original timetable data, build the train network, and query the coordinates of the stations.

## Python Only

This project requires **Python 3.10**.
To install the required Python dependencies, run the following commands:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
The Jupyter notebooks contain the various steps of the network analysis.
For convenience, we provide all the necessary data, such as benchmark results, graph edge list, and station coordinates in `data/`.

The three notebooks contain the following part of our project:
- `network_exploration.ipynb` contains the network exploration and visualization of the network with the Swiss map.
- `community_detection.ipynb` showcases the community detection algorithms. This notebooks run the NetworkX and our implementation of Louvain, Girvan-Newman and Leiden.
- `community_detection_evaluation.ipynb` benchmarks the community detection algorithms and our implementation. We visualize the results in this notebook.

## Neo4j Full Pipeline

This section covers how to run the full pipeline.
Please ensure that you have installed the Python dependencies before proceeding with this section.

To configure the Neo4j database with the timetable data, you need to run the setup script.
This script has only been tested on Debian-based operating systems.
`neo4j/drop.sh` is a convenient script to drop the database

`setup.sh` downloads the zip dataset from the Open Data Platform Mobility [(download link)](https://opentransportdata.swiss/en/dataset/timetable-2024-gtfs2020/resource/1cb3b923-6f2b-40ee-9a9a-900417e9fda3) and unzips it in the default Neo4j import directory.
It inserts all the data in Neo4j.
This step may take a while (between 10 and 15 minutes).

After running this script, please run the `create_edgelist.py`.
This Python script queries Neo4j to create the `data/sbb.edgelist` and `data/stations.geojson`.
You must give it your Neo4j username and password as arguments.

```
./setup.sh
python create_edgelist.py <username> <password> # replace with your neo4j username and password!
```

## Swiss Map Plots

In the second part of `network_exploration.ipynb`, the graph visualization on the Swiss map uses the GeoPackage data from Swisstopo.
To reproduce the plot, you must download the data at this [link](https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d#swissBOUNDARIES3D---Download).
Download the archive containing the file with the `gpkg` extension and decompress it in `data/`.
