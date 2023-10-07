package brsynth;

import apoc.export.util.Reporter;

import java.io.PrintWriter;
import java.util.function.Consumer;
import java.util.stream.Stream;

/**
 * @author mh
 * @since 22.05.16
 */
public class ProgressReporterPathway implements Reporter {
    private final SizeCounter sizeCounter;
    private final PrintWriter out;
    private final long batchSize;
    long time;
    int counter;
    long totalEntities = 0;
    long lastBatch = 0;
    long start = System.currentTimeMillis();
    private final ProgressInfoPathway progressInfoPathway;
    private Consumer<ProgressInfoPathway> consumer;

    public ProgressReporterPathway(SizeCounter sizeCounter, PrintWriter out,
            ProgressInfoPathway progressInfoPathway) {
        this.sizeCounter = sizeCounter;
        this.out = out;
        this.time = start;
        this.progressInfoPathway = progressInfoPathway;
        this.batchSize = progressInfoPathway.batchSize;
    }

    public ProgressReporterPathway withConsumer(Consumer<ProgressInfoPathway> consumer) {
        this.consumer = consumer;
        return this;
    }

    @Override
    public void progress(String msg) {
        long now = System.currentTimeMillis();
        // todo report percentages back
        println(String.format(msg + " %d. %d%%: %s time %d ms total %d ms", counter++, percent(),
                progressInfoPathway, now - time, now - start));
        time = now;
    }

    private void println(String message) {
        if (out != null)
            out.println(message);
    }

    private long percent() {
        return sizeCounter == null ? 100 : sizeCounter.getPercent();
    }

    public void update(long nodes, long relationships, long properties) {
        time = System.currentTimeMillis();
        progressInfoPathway.update(nodes, relationships, properties);
        totalEntities += nodes + relationships;
        acceptBatch();
    }

    public void update(long nodes, long relationships, long properties, long pathways) {
        time = System.currentTimeMillis();
        progressInfoPathway.update(nodes, relationships, properties, pathways);
        totalEntities += nodes + relationships;
        acceptBatch();
    }

    public void acceptBatch() {
        if (batchSize != -1 && totalEntities / batchSize > lastBatch) {
            updateRunningBatch(progressInfoPathway);
            if (consumer != null) {
                consumer.accept(progressInfoPathway);
            }
        }
    }

    public void updateRunningBatch(ProgressInfoPathway progressInfoPathway) {
        lastBatch = Math.max(totalEntities / batchSize, lastBatch);
        progressInfoPathway.batches = lastBatch;
        this.progressInfoPathway.rows = totalEntities;
        this.progressInfoPathway.updateTime(start);
    }

    @Override
    public void done() {
        if (totalEntities / batchSize == lastBatch)
            lastBatch++;
        updateRunningBatch(progressInfoPathway);
        progressInfoPathway.done(start);
        if (consumer != null) {
            consumer.accept(progressInfoPathway);
        }
        if (consumer != null) {
            consumer.accept(ProgressInfoPathway.EMPTY);
        }
    }

    public ProgressInfoPathway getTotal() {
        progressInfoPathway.done(start);
        return progressInfoPathway;
    }

    public Stream<ProgressInfoPathway> stream() {
        return Stream.of(getTotal());
    }

    public void nextRow() {
        this.progressInfoPathway.nextRow();
        this.totalEntities++;
        acceptBatch();
    }

}
