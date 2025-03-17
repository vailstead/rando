# Prometheus Performance Limits

- Up to ~10 million active time series per instance is generally considered stable.
- Beyond 10M series, performance degrades significantly due to:
  - Increased memory usage.
  - Higher query latency.
  - Longer compaction times.
- At ~20 million series, most setups will experience serious slowdowns unless optimized.
```sql
Total time series = (number of targets) × (metrics per target) × (labels variations)
```

# Key Performance Factors

- Active time series: More time series = more memory needed.
- Scrape interval: Lower intervals (e.g., 1s) generate more data.
- Label cardinality: More unique labels = exponential increase in time series.
- Retention period: Longer retention = more disk usage but does not directly affect active time series.
- Query complexity:	Complex queries with many labels slow down response times.

A single Prometheus instance can handle ~10M series reliably.
Beyond that, you should shard using Thanos, Mimir, or multiple Prometheus instances.
High-cardinality labels are the biggest cause of performance issues.

# How to Optimize Prometheus Performance
- Reduce Label Cardinality
  - Avoid high-cardinality labels like user_id, request_id, etc.
- Optimize Scrape Intervals
  - Use 30s–60s intervals instead of 1s unless real-time data is needed.
- Shard Prometheus (Federation or Thanos)
  - Use multiple Prometheus instances instead of a single large one.
  - Thanos allows scalable long-term storage.
- Enable WAL Compression
  - Reduces write amplification and improves storage efficiency.
```yaml
storage.tsdb:
  wal_compression: true
```
- Use Thanos, Mimir, or Cortex for Large Deployments
  - Thanos: Adds horizontal scalability and long-term storage (e.g., S3).
  - Mimir/Cortex: Allows running distributed Prometheus instances.

 
# How to Check Current Time Series Count
Run this in Prometheus Query UI, This returns the total active time series.

```promql
# Counts all active time series currently stored in Prometheus.
count({__name__=~".+"})
```

Breakdown by job
```promql
# Shows the number of time series per job.
count({job=~".+"}) by (job)
```

Check High Cardinality Metrics
```promql
# Lists each metric name and the number of time series it generates.
count by (__name__) ({__name__=~".+"})
```

Check Memory Usage of Time Series
```promql
# Returns the number of series currently in memory.
prometheus_tsdb_head_series
```

Rough estimation of performance (Active Time Series Count)
<1M	Normal, runs smoothly
1M - 5M	Watch memory usage, optimize labels
5M - 10M	May need sharding (Thanos, Federation)
>10M	Performance degradation likely

# Node Exporter Time Series
The number of time series a single Prometheus Node Exporter instance generates depends on:

- Enabled collectors (default vs. custom collectors)
- Label cardinality (e.g., per CPU, per disk)
- Scrape frequency

## Default Time Series
- A default Node Exporter instance generates ~700–1000 time series.
- The count increases based on system hardware:
  - More CPUs → More cpu metrics
  - More disks → More disk and filesystem metrics
  - More network interfaces → More network metrics
 
## Example:
- 1 CPU, 1 Disk, 1 NIC	~700 time series
- 4 CPUs, 2 Disks, 2 NICs	~1,500  time series
- 16 CPUs, 8 Disks, 4 NICs	~3,000+  time series

## Disabling unused collecters:
- Disabling unused collectors is a good idea to reduce overall timeseries consumption
```yaml
docker run -d --name=node_exporter \
  -p 9100:9100 \
  quay.io/prometheus/node-exporter \
  --no-collector.entropy \
  --no-collector.textfile
```
- Additional prometheus scrape configs can be modified to drop unneeded metrics:
```yaml
scrape_configs:
  - job_name: "node-exporter"
    scrape_interval: 30s
    static_configs:
      - targets: ["node-exporter:9100"]
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: "node_cpu_seconds_total"
        action: drop
```

# Remote Write

## When should you use remote write
When Should You Use Remote Write?
- If you need long-term metric storage in a system like Thanos, Mimir, Cortex, or VictoriaMetrics.
- If you want centralized monitoring across multiple Prometheus instances.
- If you have high availability and need to ensure metrics are retained even if local Prometheus fails.

Avoid Remote Write if:  

- You only need short-term metric storage (use local Prometheus TSDB instead).
- You expect real-time queries from Prometheus (use Thanos Query instead).
- You have network constraints that can’t handle constant metric streaming.

## Perfomance Considerations
Prometheus Remote Write has several performance considerations because it continuously streams data to an external system, unlike local storage which writes in batches. Here’s what you need to consider:
-  Increased CPU and Memory Usage
  - Remote Write constantly sends data over the network, consuming CPU and memory
  - If the write queue is too large, Prometheus can run out of memory.
  
- Network Bandwidth Impact
  - Every scraped metric must be transmitted to the remote store.
  - This can saturate network links if metrics are high-cardinality.
 
- Remote Write Latency
  - Prometheus buffers metrics before sending. If the remote system is slow, backpressure builds up.
  - Large queues can lead to dropped metrics.
 
- Query Performance
  - Remote Write does NOT support queries!
  - Prometheus cannot read back from a remote write endpoint.
 
- Disk I/O Considerations
  - Prometheus still writes locally before sending via Remote Write.
  - High disk usage may cause slowdowns.
