CREATE CONSTRAINT tripIdConstraint FOR (t:Trip) REQUIRE t.id IS UNIQUE;

// extremely large!
:auto LOAD CSV WITH HEADERS FROM "file:///trips.txt" AS row
CALL {
    WITH row
    MERGE (r:Route {id : row["route_id"]}) 
    CREATE (t:Trip {
        id: row["trip_id"],
        service_id: row["service_id"],
        headsign: row["trip_headsign"],
        short_name: row["trip_short_name"],
        direction_id: row["direction_id"]
    })
    CREATE (r)<-[rel:USES]-(t)
} IN TRANSACTIONS;
