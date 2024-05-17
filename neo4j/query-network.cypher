// query Neo4j to build the SBB network
MATCH (r:Route)<-[:USES]-(t:Trip)-[:STOPSAT]->(stt:StopTime)-[:REFERENCES]->(s:Stop)
WHERE r.type >= 100 AND r.type <= 120
WITH r, t, s, stt
ORDER BY r.id, t.id, stt.stop_sequence
RETURN r.id, t.id, COLLECT(s.name)
