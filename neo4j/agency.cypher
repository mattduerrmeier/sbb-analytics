CREATE CONSTRAINT agencyIdConstraint FOR (a:Agency) REQUIRE a.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///agency.txt" AS row
CREATE (a:Agency {
    id: row["agency_id"],
    name: row["agency_name"],
    url: row["agency_url"],
    timezone: row["agency_timezone"],
    lang: row["agency_lang"],
    phone: row["agency_phone"]
});
