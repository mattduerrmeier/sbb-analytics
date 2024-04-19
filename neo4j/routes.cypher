CREATE CONSTRAINT routeIdConstraint FOR (r:Route) REQUIRE r.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///routes.txt" AS row
MERGE (a:Agency {id : row["agency_id"]}) 

CREATE (r:Route {
    id: row["route_id"],
    short_name: row["route_short_name"],
    long_name: row["route_long_name"],
    desc: row["route_desc"],
    type: row["route_type"]
})

CREATE (a)-[rel:OPERATES]->(r);
