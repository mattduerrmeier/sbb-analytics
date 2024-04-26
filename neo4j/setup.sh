#!/bin/sh

echo "This script may take a while to insert all the data (~15 minutes)."
time cypher-shell -f setup.cypher
