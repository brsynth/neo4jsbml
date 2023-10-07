package brsynth;

import java.util.List;
import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.neo4j.driver.Driver;
import org.neo4j.driver.GraphDatabase;
import org.neo4j.driver.Session;
import org.neo4j.driver.Value;
import org.neo4j.driver.Values;
import org.neo4j.driver.Record;
import org.neo4j.harness.Neo4j;
import org.neo4j.harness.Neo4jBuilders;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class EnumeratePathwayTests {

    private Driver driver;
    private Neo4j embeddedDatabaseServer;

    @BeforeAll
    void initializeNeo4j() {
        this.embeddedDatabaseServer = Neo4jBuilders.newInProcessBuilder()
                .withDisabledServer()
                .withProcedure(EnumeratePathway.class)
                .build();

        this.driver = GraphDatabase.driver(embeddedDatabaseServer.boltURI());
    }

    @AfterAll
    void closeDriver(){
        this.driver.close();
        this.embeddedDatabaseServer.close();
    }

    @AfterEach
    void cleanDb(){
        try(Session session = driver.session()) {
            session.run("MATCH (n) DETACH DELETE n");
        }
    }
    public static Long convertToLong(Object o){
        String stringToConvert = String.valueOf(o);
        Long convertedLong = Long.parseLong(stringToConvert);
        return convertedLong;
        
    }

    @Test
    public void countNodes() {
        try(Session session = driver.session()) {  // In a try-block, to make sure we close the session after the test
            // Create data.
            session.run("CREATE (n:Species {id: 'A', stoichiometry: '1'})");
            session.run("CREATE (n:Species {id: 'B', stoichiometry: '1'})");
            session.run("CREATE (n:Species {id: 'C', stoichiometry: '1'})");
            session.run("CREATE (n:Species {id: 'D', stoichiometry: '1'})");
            session.run("CREATE (n:Species {id: 'E', stoichiometry: '1'})");
            session.run("CREATE (n:Species {id: 'P', stoichiometry: '1'})");

            session.run("CREATE (n:Reaction {id: 'r1', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r2', reversible: 'true'})");
            session.run("CREATE (n:Reaction {id: 'r3', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r4', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r5', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r6', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r7', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r8', reversible: 'true'})");
            session.run("CREATE (n:Reaction {id: 'r9', reversible: 'false'})");
            session.run("CREATE (n:Reaction {id: 'r10', reversible: 'false'})");
            
            session.run(" MATCH (r:Reaction {id: 'r1'}), (s:Species {id: 'A'}) CREATE (r)-[:HAS_PRODUCT]->(s)");
            session.run(" MATCH (r:Reaction {id: 'r2'}), (s:Species {id: 'B'}) CREATE (r)-[:HAS_PRODUCT]->(s)");
            session.run(" MATCH (r:Reaction {id: 'r3'}), (s:Species {id: 'P'}) CREATE (r)-[:HAS_SUBSTRATE]->(s)");
            session.run(" MATCH (r:Reaction {id: 'r4'}), (s:Species {id: 'E'}) CREATE (r)-[:HAS_SUBSTRATE]->(s)");
            session.run(" MATCH (r:Reaction {id: 'r5'}), (s1:Species {id: 'A'}), (s2:Species {id: 'B'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");
            session.run(" MATCH (r:Reaction {id: 'r6'}), (s1:Species {id: 'A'}), (s2:Species {id: 'C'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");
            session.run(" MATCH (r:Reaction {id: 'r7'}), (s1:Species {id: 'A'}), (s2:Species {id: 'D'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");
            session.run(" MATCH (r:Reaction {id: 'r8'}), (s1:Species {id: 'B'}), (s2:Species {id: 'C'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");           
            session.run(" MATCH (r:Reaction {id: 'r9'}), (s1:Species {id: 'B'}), (s2:Species {id: 'P'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");
            session.run(" MATCH (r:Reaction {id: 'r10'}),(s1:Species {id: 'C'}), (s2:Species {id: 'E'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");
            session.run(" MATCH (r:Reaction {id: 'r10'}),(s1:Species {id: 'D'}), (s2:Species {id: 'P'}) CREATE (r)-[:HAS_SUBSTRATE]->(s1),(r)-[:HAS_PRODUCT]->(s2)");

            // Test insertion data
            int nodes;
            nodes = session.run("MATCH (n:Species) RETURN count(n) AS Total").single().get("Total").asInt();
            assertThat(nodes).isEqualTo(6);
            nodes = session.run("MATCH (r:Reaction) RETURN count(r) AS Total").single().get("Total").asInt();
            assertThat(nodes).isEqualTo(10);

            // Test Pathway
            session.run("CALL brsynth.enumeratePathway(['A', 'P'], 'AtoP')");
            //List<Long> pathways;
            //pathways = session.run("MATCH (s:Species {id: 'A'}) RETURN s.AtoP AS val").single().get("val").asList(Value::asLong);
            //assertThat(pathways).containsExactly(1L, 2L, 3L, 4L, 5L);
            //Record record = session.run("MATCH (s:Species) RETURN keys(s) LIMIT 1").single();
            //System.out.println(record);

            /* 
            ╞══════════════════════════════════════════════════════════════════════╡            
            │n                                                                     │
            ╞══════════════════════════════════════════════════════════════════════╡
            │(:Species {name: "A",id: "A",AtoP: [1, 2, 3, 4, 5]})                  │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Species {name: "B",id: "B",AtoP: [1, 2, 4, 5]})                     │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Species {name: "C",id: "C",AtoP: [1, 3, 4, 5]})                     │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Species {name: "D",id: "D",AtoP: [3, 4, 5]})                        │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Species {name: "E",id: "E",AtoP: [3, 4, 5]})                        │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Species {name: "P",id: "P",AtoP: [1, 2, 3, 4, 5]})                  │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r1",AtoP: [1, 2, 3, 4, 5],id: "│
            │r1"})                                                                 │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "True",name: "r2",id: "r2",AtoP: [5]})        │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r3",AtoP: [1, 2, 3, 4, 5],id: "│
            │r3"})                                                                 │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r4",AtoP: [3, 4, 5],id: "r4"}) │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r5",AtoP: [2, 4],id: "r5"})    │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r6",AtoP: [1, 3],id: "r6"})    │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r7",AtoP: [3, 4, 5],id: "r7"}) │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "True",name: "r8",id: "r8",AtoP: [1, 4, 5]})  │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r9",AtoP: [1, 2],id: "r9"})    │
            ├──────────────────────────────────────────────────────────────────────┤
            │(:Reaction {reversible: "False",name: "r10",AtoP: [3, 4, 5],id: "r10"}│
            │)
            */
        }
    }
}
