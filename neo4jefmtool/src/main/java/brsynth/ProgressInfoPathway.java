package brsynth;

import apoc.result.ProgressInfo;

public class ProgressInfoPathway extends ProgressInfo {
    public static final ProgressInfoPathway EMPTY = new ProgressInfoPathway(null, null, null);
    public long pathways;

    public ProgressInfoPathway(String file, String source, String format) {
        super(file, source, format);
    }

    public ProgressInfoPathway(ProgressInfoPathway pi) {
        super(pi);
        this.pathways = pi.pathways;
    }

    @Override
    public String toString() {
        return String.format("nodes = %d rels = %d properties = %d pathways = %d", nodes,
                relationships, properties, pathways);
    }

    public ProgressInfoPathway update(long nodes, long relationships, long properties,
            long pathways) {
        this.nodes += nodes;
        this.relationships += relationships;
        this.properties += properties;
        this.pathways += pathways;
        return this;
    }
}
