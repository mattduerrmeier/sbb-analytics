CREATE CONSTRAINT agencyIdConstraint FOR (a:Agency) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT routeIdConstraint FOR (r:Route) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT tripIdConstraint FOR (t:Trip) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT stopIdConstraint FOR (s:Stop) REQUIRE s.id IS UNIQUE;

// Agency 
LOAD CSV WITH HEADERS FROM "file:///agency.txt" AS row
CREATE (a:Agency {
    id: row["agency_id"],
    name: row["agency_name"]
    // url: row["agency_url"],
    // timezone: row["agency_timezone"],
    // lang: row["agency_lang"],
    // phone: row["agency_phone"]
});

// Routes
LOAD CSV WITH HEADERS FROM "file:///routes.txt" AS row
MERGE (a:Agency {id : row["agency_id"]}) 
CREATE (r:Route {
    id: row["route_id"],
    short_name: row["route_short_name"],
    // long_name: row["route_long_name"],
    desc: row["route_desc"],
    type: toInteger(row["route_type"])
})
CREATE (a)-[rel:OPERATES]->(r);

// Trips
LOAD CSV WITH HEADERS FROM "file:///trips.txt" AS row
CALL {
    WITH row
    MERGE (r:Route {id : row["route_id"]}) 
    CREATE (t:Trip {
        id: row["trip_id"],
        service_id: row["service_id"],
        headsign: row["trip_headsign"],
        short_name: toInteger(row["trip_short_name"])
        // direction_id: toInteger(row["direction_id"])
    })
    CREATE (r)<-[rel:USES]-(t)
} IN TRANSACTIONS;

// Stops
LOAD CSV WITH HEADERS FROM "file:///stops.txt" AS row 
CREATE (s:Stop {
    id: row["stop_id"],
    name: row["stop_name"],
    location: point({
        longitude: toFloat(row["stop_lon"]),
        latitude: toFloat(row["stop_lat"])
    }),
    parent_station: row["parent_station"]
});

// Stop times
// Very large! Takes ~10-15 minutes to run
LOAD CSV WITH HEADERS FROM "file:///stop_times.txt" AS row 
CALL {
    WITH row
    MATCH (t:Trip {id: row["trip_id"]})
    MATCH (s:Stop {id: row["stop_id"]})
    CREATE (stt:StopTime {
        arrival_time: row["arrival_time"],
        departure_time: row["departure_time"],
        stop_sequence: toInteger(row["stop_sequence"]),
        pickup_type: toInteger(row["pickup_type"]),
        drop_off_type: toInteger(row["drop_off_type"])
    })
    MERGE (stt)-[:REFERENCES]->(s)
    MERGE (t)-[:STOPSAT]->(stt)

} IN TRANSACTIONS;
