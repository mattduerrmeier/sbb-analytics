#!/bin/bash

if [[ "$EUID" -ne 0 ]]; then
	echo "Please run the script as root."
	exit
fi

read -r -p "This script will drop your neo4j database. Are you sure you want to proceed? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
	echo "Stopping neo4j..."
	systemctl stop neo4j
	echo "Removing database files..."
	rm -r /var/lib/neo4j/data/databases/neo4j 2>/dev/null
	rm -r /var/lib/neo4j/data/transactions/neo4j 2>/dev/null
	echo "Done! Please restart neo4j."
else
	echo "Cancelling script."
	exit
fi
