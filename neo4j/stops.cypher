CREATE CONSTRAINT stopIdConstraint FOR (s:Stop) REQUIRE s.id IS UNIQUE;

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
