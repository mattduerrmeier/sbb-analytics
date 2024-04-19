from neo4j import GraphDatabase, Result
import pandas as pd
import sys

# This scripts query the neo4j database to create the sbb.edgelist.
# You must to provide the database username and passwords as arguments.

if len(sys.argv) < 3:
    print("Please provide neo4j username and password as arguments")
    exit()

# db crendentials
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
        RETURN r.id AS route_id, t.id as trip_id, COLLECT(s.name) AS paths
        """,
        result_transformer_=Result.to_df,
    )

# for each path lis, create an edgeliste (list of tuple)
path_to_edgelist = lambda l: [(l[i], l[i + 1]) for i in range(len(l) - 1)]
df["paths"] = df["paths"].apply(path_to_edgelist)

# each tuple is not a single entry in the columns, instead of a list of tuple
sbb_edgelist = df["paths"].explode().unique()

print("Writing edgelist to sbb.edgelist")
train = pd.DataFrame(list(sbb_edgelist), columns=["from", "to"])
train.to_csv("sbb.edgelist", sep=";", header=False, index=False)
