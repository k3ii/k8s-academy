<a id="a-hundred-nodes-that-do-not-exist"></a>
# Above the floor at last: the knob measured against nodes with no machines under them

**Artifact** — two runs of upstream's own scheduler performance harness over the same synthetic cluster, one at the adaptive default and one at a low `percentageOfNodesToScore`, with the throughput difference recorded; plus the node count at which your `forge` refuses to run the harness at all, which is a measurement of the lab rather than of Kubernetes and worth having.

**Rests on** — [the arithmetic](16-the-knob-that-cannot-move-here.md). You proved the knob is unreachable on real hardware you can build; this reaches it on hardware nobody built.

**Topology** — **none, and this is load-bearing.** [`pair` must be down or idle](../../strands/lab-topologies.md#pair) — the harness starts an API server, an etcd and a scheduler inside one test process on [`forge`](../../strands/lab-topologies.md#build-guest), and that process is the largest thing this phase runs outside a link.

**Setup**

```sh
ssh zain@10.10.10.125
cd ~/src/kubernetes
./hack/install-etcd.sh
export PATH=$PWD/third_party/etcd:$PATH
etcd --version
ls test/integration/scheduler_perf/
```

Read [`scheduler_benchmarking.md`](../../strands/source-reading.md#area-3-scheduler) first — 3.6 KB, and it explains what the harness measures and what the workload configuration files mean, which the `-bench` flag names will not.

**Do**

1. **List the workloads before running one.** They are declared in YAML, not in Go, which is what makes this harness usable as a lab instrument:

   ```sh
   grep -rn 'name:\|nodes:\|initPods\|measurePods' test/integration/scheduler_perf/config/performance-config.yaml | head -40
   ```

   Pick the smallest workload whose node count is above the floor you derived. Write down its name, its node count and its pod count.

2. **Find your ceiling.** Run it once, with a memory watch beside it, and record the peak:

   ```sh
   # session 2
   while :; do free -m | awk '/Mem:/{print strftime("%T"), $3}'; sleep 2; done
   ```

   ```sh
   # session 1
   go test ./test/integration/scheduler_perf/... -bench=BenchmarkPerfScheduling/<workload> \
     -benchtime=1x -run=^$ -v 2>&1 | tee /tmp/perf-default.log
   ```

   If it is killed, halve the workload and try again. **The largest workload that completes is a number to write down**, not a failure — it is the honest boundary of what this lab can measure, and every conclusion below is scoped to it.

3. **Read the output.** The harness reports scheduling throughput in pods per second and the wall time of the run. Find both.

4. **Change the knob.** The workload's scheduler configuration is a `KubeSchedulerConfiguration` file in the same directory tree; copy it, set `percentageOfNodesToScore` to a low value, and point the workload at your copy:

   ```sh
   grep -rn 'schedulerConfigPath\|kubescheduler.config' test/integration/scheduler_perf/config/ | head
   ```

5. **Re-run, identically**, and diff the two throughput numbers.

6. Answer the module's question with the numbers in hand: at your workload's node count, how much work does the knob actually save, and what does it cost? The cost is not in the throughput figure — it is in the *quality* of the placement, and the harness does not measure that. Say so explicitly.

**Observe** — the two throughput figures, the peak RSS from step 2, and the wall time.

**Expect** — a measurable but unspectacular difference at a few hundred nodes, which is the correct result and matches the reason the default is adaptive rather than fixed: the knob is a trade you only want to make when the node count is large enough that the filtering cost dominates, and a few hundred is barely there.

Expect the harness to be **memory-bound on `forge` well before it is interesting**, and expect that to be the sharpest thing this exercise teaches: an in-process control plane plus a few hundred synthetic nodes is a bigger machine than a real two-node cluster. State the node count where it died.

Expect the placement-quality point to be unmeasured and to stay that way here. Scoring fewer nodes means the best node may not be among the candidates; nothing in this run would notice. That is exactly the trade [module 5.6](34-placement-that-differs-measurably.md) makes visible on three real nodes, where the knob is once again inert and the *scoring* is what changes.

**Write down** — the workload name with node and pod counts, the two throughput figures, the peak RSS, the largest workload that completed, and one sentence on what this measurement cannot see.

**Footprint note** — `forge` at 2560MB running an API server, an etcd and a scheduler in one process, with `pair` down or idle. If `pair` is up, the total is 7.5GB and the harness has the 2560MB guest to itself — that is the configuration this exercise assumes, and it is why step 2 exists rather than a promised workload size. Disk matters here too: the integration harness writes an etcd data directory under `/tmp`; check `df -h /` before and after.

**Teardown**

```sh
rm -rf /tmp/etcd* /tmp/perf-*.log
go clean -testcache
df -h /
```

Restore the workload's scheduler configuration file if you edited it in place rather than copying, and confirm with `git -C ~/src/kubernetes status --short test/integration/scheduler_perf/` that the tree is clean — a modified upstream file will confuse every citation you make for the rest of the phase. **No topology to release** — `pair` comes back up (or wakes up) for [module 5.4](18-find-the-queue-yourself.md).
