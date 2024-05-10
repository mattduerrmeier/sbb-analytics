from neo4j import GraphDatabase, Result
import pandas as pd
import sys

# This script queries the neo4j database to create the sbb.edgelist.
# You must provide the database username and passwords as arguments.

if len(sys.argv) < 3:
    print("Please provide neo4j username and password as arguments")
    exit()

# db credentials
URI = "neo4j://localhost"
AUTH = (sys.argv[1], sys.argv[2])

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    info = driver.get_server_info()
    print(f"Connection established to {info.address}")

    # cypher query
    df = driver.execute_query(
        """
        MATCH (r:Route)<-[:USES]-(t:Trip)-[:STOPSAT]->(stt:StopTime)-[:REFERENCES]->(s:Stop) 
        WHERE r.type >= "100" AND r.type <= "120" 
        WITH r, t, s, stt 
        ORDER BY r.id, t.id, stt.stop_sequence 
        RETURN r.id AS route_id, t.id AS trip_id, COLLECT({name: s.name, location: s.location}) AS stops 
        """,
        result_transformer_= Result.to_df,
    )

# for each path list, create an edgelist (list of tuple)
path_to_edgelist = lambda l: [(l[i]['name'], l[i + 1]['name']) for i in range(len(l) - 1)]
df["paths"] = df["stops"].apply(path_to_edgelist)

# each tuple is not a single entry in the columns, instead of a list of tuple
sbb_edgelist = df["paths"].explode().unique()

print("Writing edgelist to sbb.edgelist")
train = pd.DataFrame(list(sbb_edgelist), columns=["from", "to"])
train.to_csv("sbb.edgelist", sep=";", header=False, index=False)

# initialise empty dictionary
station_data = {"station_name": [], "location": []}

# append unique station names with respective location
for stop_list in df["stops"].explode():
    station_name = stop_list["name"]
    location = stop_list["location"]
    if station_name not in station_data["station_name"]:
        station_data["station_name"].append(station_name)
        station_data["location"].append(location)

# create df
station_locations = pd.DataFrame(station_data)

# write to csv
print("Writing station locations to station_locations.csv")
station_locations.to_csv("station_locations.csv", sep=";", index=False)
