#!/bin/sh

# neo4j import path
import_path=""

if [ -z "$1" ]; then
	echo "No argument provided. Using Debian's default import path"
	import_path="/var/lib/neo4j/import/"
else
	import_path="$1"
fi

echo "Neo4j import path set to $import_path"

echo "Downloading dataset..."
curl -o data.zip "https://opentransportdata.swiss/dataset/7cc000ea-0973-40c1-a557-7971a4939da3/resource/1cb3b923-6f2b-40ee-9a9a-900417e9fda3/download/gtfs_fp2024_2024-03-27_04-15.zip"
sudo unzip -d "$import_path" data.zip

echo "Starting neo4j insertion query. This may take a while... (~15 minutes)"
cypher-shell -f neo4j/setup.cypher
