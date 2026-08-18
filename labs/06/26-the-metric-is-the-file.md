<a id="the-metric-is-the-file"></a>
# node-exporter's "available memory" is not the number the kubelet evicts on

**Claim** — the obvious PromQL for "is this node about to evict" is wrong. `node_memory_MemAvailable_bytes` and the kubelet's `memory.available` are computed from different inputs, differ by hundreds of megabytes on a busy node, and only one of them is compared against your threshold. You can produce both numbers at the same instant and account for the gap.

**Rests on** — [the stack](25-the-stack-that-must-not-be-evicted.md) for the metrics and [the allocatable arithmetic](17-where-the-ram-went.md) for the threshold. This is [the module's write-down](../../phases/06-kubelet-node.md#m6-6), done as a disagreement rather than as a query.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — the eviction signal's definition in `pkg/kubelet/eviction/helpers.go`: which of the summary API's fields becomes `memory.available`, and what is subtracted from what. Then find the same quantity's source in node-exporter — it reads `/proc/meminfo` and exports the fields verbatim, which is [the ecosystem note's claim](../../phases/06-kubelet-node.md#ecosystem) that the metric *is* the file.

**Do**

1. Take all three numbers within a few seconds of each other:

   ```sh
   ssh zain@10.10.10.131 'grep -e MemTotal -e MemFree -e MemAvailable -e "^Cached" /proc/meminfo'
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/stats/summary" \
     | jq '.node.memory | {availableBytes, usageBytes, workingSetBytes, rssBytes}'
   ssh zain@10.10.10.131 'cat /sys/fs/cgroup/memory.stat | grep -e "^inactive_file" -e "^active_file" -e "^file "'
   ```

2. **Account for the gap.** `MemAvailable` and `availableBytes` will not match. Write the arithmetic that gets from one to the other, using the cgroup numbers from step 1. The kernel's estimate and the kubelet's estimate disagree about page cache, and the two treatments are both defensible — that is why this is a gap to explain rather than a bug to report.

3. Now write the query the module asks for, twice. First the wrong one, so you have it to compare against:

   ```promql
   node_memory_MemAvailable_bytes
   ```

   Then the honest one, built from what the kubelet actually compares — node capacity minus the root cgroup's working set:

   ```promql
   node_memory_MemTotal_bytes - on(node) group_left container_memory_working_set_bytes{id="/"}
   ```

   That join will probably fail on first try, because the two series come from different scrape jobs with different labels. **Fixing it is part of the exercise**: find the label they have in common, and if there is none, use `label_replace` to make one. Check the result against `availableBytes` from step 1 before trusting it.

4. Turn it into the alerting expression — available memory approaching the configured hard threshold:

   ```promql
   (<your honest expression>) < 300 * 1024 * 1024
   ```

**Observe** — run both queries while the node is doing nothing, then re-run them while something is reading a large file (`ssh zain@10.10.10.131 'cat /var/lib/containerd/**/* > /dev/null 2>&1'` will do). Watch the two numbers move apart.

**Expect** — the two to agree within a few tens of MB on an idle node and to diverge sharply once page cache fills, because `MemAvailable` counts reclaimable cache as available and the kubelet's working-set calculation excludes only the *inactive* part of it. On a node whose cache is warm, **the obvious query says there is plenty of memory at the moment the kubelet starts evicting.**

That is the finding, and it is the reason this exercise exists at all: the dashboard everyone builds from the default node-exporter panel does not predict eviction on the node it is drawn for. Expect your honest expression to track `availableBytes` closely enough to alert on.

Expect the `id="/"` cAdvisor series to exist and be the root cgroup — the top of [the tree you walked](15-the-cgroup-tree-under-one-pod.md), now arriving as a metric.

**Write down** — the three numbers at one instant with the arithmetic reconciling them, both PromQL expressions, and one sentence on which file each side reads. Keep the honest expression: [the next exercise](27-an-eviction-as-a-slope.md) graphs it against a real eviction.

**Footprint note** — queries only; the stack is already running.

**Teardown** — nothing created. **The topology stays.**
