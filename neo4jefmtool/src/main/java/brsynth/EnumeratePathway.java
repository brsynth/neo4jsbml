package brsynth;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Mode;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import org.neo4j.graphdb.ResourceIterator;
import org.neo4j.graphdb.Relationship;
import ch.javasoft.metabolic.FluxDistribution;
import ch.javasoft.metabolic.MetabolicNetwork;
import ch.javasoft.metabolic.compress.CompressionMethod;
import ch.javasoft.metabolic.efm.ElementaryFluxModes;
import ch.javasoft.metabolic.efm.adj.incore.tree.search.PatternTreeMinZerosAdjacencyEnumerator;
import ch.javasoft.metabolic.efm.config.Arithmetic;
import ch.javasoft.metabolic.efm.config.Config;
import ch.javasoft.metabolic.impl.DefaultMetabolicNetwork;
//import apoc.export.util.ProgressReporter;
//import apoc.result.ProgressInfo;

public class EnumeratePathway {

    static final Label SPECIES = Label.label("Species");
    static final Label REACTIONS = Label.label("Reaction");
    static final RelationshipType REL_SOURCE = RelationshipType.withName("HAS_REACTANT");
    static final RelationshipType REL_TARGET = RelationshipType.withName("HAS_PRODUCT");

    @Context
    public Transaction tx;

    @Context
    public Log log;

    @Procedure(name = "brsynth.enumeratePathway", mode = Mode.WRITE)
    @Description("Enumerate pathway with efmtools (10.1093/bioinformatics/btn401). Compute Elementaray Flux Modes (EFMs) on the whole stoichiometry matrix, then retain Species containing \"includeNode\". This parameter filter nodes based on the value of the \"id\" property. The schema needs to respect this following (s1:Species)-[HAS_SUBSTRATE]-(r:Reaction)-[HAS_PRODUCT]-(s2:Species). The property \"stoichiometry\" embedded by \"Species\" is used to set the stoichiometry of the reaction. The property \"reversible\" embedded by \"Reaction\" is also used (default: false)")
    public Stream<ProgressInfoPathway> enumeratePathway(
            @Name("includeNodes") List<String> nodeStringInclude,
            @Name("labelPathwayPrefix") String propertyNamePathway) throws Exception {

        ProgressReporterPathway reporter = new ProgressReporterPathway(null, null, ProgressInfoPathway.EMPTY);

        // Get nodes to include in the pathway
        List<Node> nodeToIncludes = new ArrayList<Node>();
        for (String nodeId : nodeStringInclude) {
            Node nodeCandidate = tx.findNodes(SPECIES, "id", nodeId).stream().findFirst()
                    .orElseThrow(IllegalArgumentException::new);
            nodeToIncludes.add(nodeCandidate);
        }

        // Create stoichiometry matrix
        List<Long> speciesIds =
                tx.findNodes(SPECIES).stream().map(x -> x.getId()).collect(Collectors.toList());
        List<Long> reactionIds =
                tx.findNodes(REACTIONS).stream().map(x -> x.getId()).collect(Collectors.toList());
        List<String> reactionReversiblesString = tx.findNodes(REACTIONS).stream()
                .map(x -> x.getProperty("reversible", "false").toString())
                .collect(Collectors.toList());
        boolean[] reactionReversibles = new boolean[reactionReversiblesString.size()];
        for (int i = 0; i < reactionReversiblesString.size(); i++) {
            boolean value = Boolean.parseBoolean(reactionReversiblesString.get(i));
            reactionReversibles[i] = value;
        }
        double[][] stoichiometryValues = new double[speciesIds.size()][reactionIds.size()];

        Map<Node, Set<Node>> reactionToNodes = new HashMap<Node, Set<Node>>();
        Map<Node, Set<Relationship>> reactionToRelationships =
                new HashMap<Node, Set<Relationship>>();
        ResourceIterator<Node> reactionNodes = tx.findNodes(REACTIONS);
        while (reactionNodes.hasNext()) {
            Node reactionNode = reactionNodes.next();
            Long reactionNodeId = reactionNode.getId();
            int reactionIx = reactionIds.indexOf(reactionNodeId);
            log.info("Reaction node ", reactionNode.getProperty("id"), " ",
                    String.valueOf(reactionIx));

            Set<Node> snodes = new HashSet<Node>();
            Set<Relationship> srelationships = new HashSet<Relationship>();
            Iterable<Relationship> nodeRelationship = reactionNode.getRelationships();
            for (Relationship relationship : nodeRelationship) {
                log.info("Relationship " + relationship.getType());
                if (relationship.getType().equals(REL_SOURCE)
                        || relationship.getType().equals(REL_TARGET)) {
                    for (Node nodeCandidate : relationship.getNodes()) {
                        log.info("Node candidate " + nodeCandidate.getProperty("id"));
                        if (nodeCandidate.getId() != reactionNodeId) {
                            double stoichiometry = Double.valueOf(
                                    nodeCandidate.getProperty("stoichiometry", -1).toString());
                            if (relationship.getType().equals(REL_SOURCE)) {
                                stoichiometry = -stoichiometry;
                            }
                            int speciesIx = speciesIds.indexOf(nodeCandidate.getId());
                            log.info("Add node " + nodeCandidate.getProperty("id") + " "
                                    + String.valueOf(speciesIx) + " "
                                    + String.valueOf(stoichiometry));
                            stoichiometryValues[speciesIx][reactionIx] = stoichiometry;
                            snodes.add(nodeCandidate);
                            srelationships.add(relationship);
                        }
                    }
                }
            }
            reactionToNodes.put(reactionNode, snodes);
            reactionToRelationships.put(reactionNode, srelationships);
        }
        log.info("Soichiometry values");
        for (double[] ar : stoichiometryValues) {
            log.info(Arrays.toString(ar));
        }

        // Compute efms
        Config.initForJUnitTest(PatternTreeMinZerosAdjacencyEnumerator.NAME,
                CompressionMethod.STANDARD_NO_DUPLICATE, Arithmetic.double_);
        MetabolicNetwork net =
                new DefaultMetabolicNetwork(stoichiometryValues, reactionReversibles);
        Iterable<? extends FluxDistribution> fluxDistributions =
                ElementaryFluxModes.calculateAndReturnEfms(net);

        // Build graph
        Long graphNumber = 1L;
        for (FluxDistribution efm : fluxDistributions) {

            double[] rates = efm.getDoubleRates();
            log.info(Arrays.toString(rates));
            Set<Node> nodes = new HashSet<Node>();
            for (int ix = 0; ix < rates.length; ix++) {
                if (rates[ix] < 0 || rates[ix] > 0) {
                    Long reactionId = reactionIds.get(ix);
                    for (var entry : reactionToNodes.entrySet()) {
                        if (entry.getKey().getId() == reactionId.longValue()) {
                            nodes.add(entry.getKey());
                            nodes.addAll(entry.getValue());
                            break;
                        }
                    }
                }
            }
            // Check if a pathway has the two targeted nodes
            boolean[] isFound = new boolean[nodeToIncludes.size()];
            for (int ix = 0; ix < isFound.length; ix++) {
                isFound[ix] = false;
            }
            for (Node node : nodes) {
                for (int ix = 0; ix < isFound.length; ix++) {
                    if (node.getId() == nodeToIncludes.get(ix).getId()) {
                        isFound[ix] = true;
                        break;
                    }
                }
            }
            int countTrue = 0;
            for (int ix = 0; ix < isFound.length; ix++) {
                if (isFound[ix]) {
                    countTrue++;
                }
            }
            // Insert data
            if (countTrue == isFound.length) {
                for (Node node : nodes) {
                    long[] props = {graphNumber};
                    if (node.hasProperty(propertyNamePathway)) {
                        long[] oldProps = (long[]) node.getProperty(propertyNamePathway);
                        long[] both = Arrays.copyOf(oldProps, oldProps.length + 1);
                        both[both.length - 1] = graphNumber;
                        props = both;
                    }
                    node.setProperty(propertyNamePathway, props);
                    reporter.update(0, 0, 1, 0);
                }
                log.info("Pathway: " + String.valueOf(graphNumber));
                log.info("Number of nodes: " + String.valueOf(nodes.size()));
                reporter.update(0, 0, 0, 1);
                graphNumber++;
            }
        }
        return reporter.stream();
    }
}
