# SBB Network Analytics

This project creates the SBB network from the official timetable, performs analysis, and community detection.

## Quick Start

Run the following commands to setup your environment:
```sh
./data.sh
pip install -r requirements.txt
python create_edgelist.py
```

`data.sh` download the zip dataset from the [Open data platform mobility](https://opentransportdata.swiss/en/dataset/timetable-2024-gtfs2020/resource/1cb3b923-6f2b-40ee-9a9a-900417e9fda3), and unzips it in a `data/` directory.  
The python script queries Neo4j to create the `sbb.edgelist`.

The notebooks contains the various steps of the network analysis.
