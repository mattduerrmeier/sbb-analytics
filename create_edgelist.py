from neo4j import GraphDatabase, Result
import pandas as pd
import sys
import geopandas as gpd
from shapely.geometry import Point

# This script queries the neo4j database to create the sbb.edgelist and station locations GeoJSON.
# You must provide the database username and password as arguments.

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

    # cypher location query
    df = driver.execute_query(
        """
        MATCH (r:Route)<-[:USES]-(t:Trip)-[:STOPSAT]->(stt:StopTime)-[:REFERENCES]->(s:Stop) 
        WHERE r.type >= 100 AND r.type <= 120
        WITH s.name AS station_name, collect(DISTINCT s.location)[0] AS lon_lat
        ORDER BY station_name
        RETURN station_name, lon_lat
        """,
        result_transformer_= Result.to_df,
    )

# convert coordinates to Point objects
df["geometry"] = df["lon_lat"].apply(lambda point: Point(point.x, point.y))
df.drop(columns=["lon_lat"], inplace=True)

# convert pandas df to geo df
gdf = gpd.GeoDataFrame(df, geometry="geometry")

# save geo df as geoJSON
print("Writing station locations to stations.geojson")
gdf.to_file("stations.geojson", driver='GeoJSON')


# cypher query for edgelist
df_edges = driver.execute_query(
    """
    MATCH (r:Route)<-[:USES]-(t:Trip)-[:STOPSAT]->(stt:StopTime)-[:REFERENCES]->(s:Stop) 
    WHERE r.type >= 100 AND r.type <= 120
    WITH r, t, s, stt 
    ORDER BY r.id, t.id, stt.stop_sequence 
    RETURN r.id AS route_id, t.id AS trip_id, COLLECT(s.name) AS paths 
    """,
    result_transformer_= Result.to_df,
)

# for each path list, create an edgelist (list of tuple)
path_to_edgelist = lambda l: [(l[i], l[i + 1]) for i in range(len(l) - 1)]
df_edges["paths"] = df_edges["paths"].apply(path_to_edgelist)

# each tuple is not a single entry in the columns, instead of a list of tuple
sbb_edgelist = df_edges["paths"].explode().unique()

print("Writing edgelist to sbb.edgelist")
train = pd.DataFrame(list(sbb_edgelist), columns=["from", "to"])
train.to_csv("sbb.edgelist", sep=";", header=False, index=False)
