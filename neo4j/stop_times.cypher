// extremely large! ~20 minutes to run
:auto LOAD CSV WITH HEADERS FROM "file:///stop_times.txt" AS row 
CALL {
    WITH row
    MATCH (s:Stop {id: row["stop_id"]})
    MATCH (t:Trip {id: row["trip_id"]})
    CREATE (stt:StopTime {
        arrival_time: row["arrival_time"],
        departure_time: row["departure_time"],
        stop_sequence: row["stop_sequence"],
        pickup_type: row["pickup_type"],
        drop_off_type: row["drop_off_type"]
    })
    MERGE (stt)-[:REFERENCES]->(s)
    MERGE (t)-[:STOPSAT]->(stt)

} IN TRANSACTIONS;
