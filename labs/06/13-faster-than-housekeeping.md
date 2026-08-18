<a id="faster-than-housekeeping"></a>
# The kubelet reacts before its own timer does, and the kernel is what wakes it

**Claim** — the eviction manager's polling interval is *not* the worst-case detection latency, because memory has a second path: the cgroup notifies the kubelet through an `eventfd` the moment usage crosses a watermark. You can predict both latencies and measure the difference.

**Rests on** — [the eviction you configured](12-an-eviction-you-configured.md); the threshold from that exercise is still on the worker and this one reuses it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, worker only.

**Read**

| Item | Answer from it |
|---|---|
| `pkg/kubelet/eviction/memory_threshold_notifier.go` (item 13) | The `eventfd` registration: which cgroup file is watched, what value is written to register interest, and what the notifier does when it fires. Which signals get a notifier, and which are left to polling only? |
| KEP-4205, PSI-based node conditions (item 14) | What pressure-stall information measures that `memory.available` cannot. Why is "time spent stalled" a different question from "bytes free"? |
| The housekeeping interval `synchronize()` runs on | The polling half of the pair — the number you are about to compare against. |

Answer [module 6.3's fourth question](../../phases/06-kubelet-node.md#m6-3) in one sentence before you run anything: how does the kubelet react faster than its housekeeping interval?

**Do**

1. Find the notifier at work on the worker. The kubelet registers against the root memory cgroup for the node-level signal:

   ```sh
   ssh zain@10.10.10.131 'ls /sys/fs/cgroup/memory.pressure /sys/fs/cgroup/kubepods.slice/memory.* 2>/dev/null; \
     sudo ls -l /proc/$(pidof kubelet)/fd | grep -c eventfd'
   ```

2. Read the kernel's own pressure numbers while the node is idle, so you have a baseline:

   ```sh
   ssh zain@10.10.10.131 'cat /proc/pressure/memory; cat /sys/fs/cgroup/kubepods.slice/memory.pressure'
   ```

3. **Predict two latencies**, then produce them. Re-run the slow hog from [exercise 12](12-an-eviction-you-configured.md), but this time timestamp the crossing yourself: sample `memory.available` every second and record the wall-clock second at which it goes below `700Mi`, then compare with the timestamp on the kubelet's first eviction log line.

   ```sh
   ssh zain@10.10.10.131 'while :; do printf "%s %s\n" "$(date +%T)" \
     "$(awk "/MemAvailable/ {print \$2}" /proc/meminfo)"; sleep 1; done' | tee /tmp/avail.log
   ```

   ```sh
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-5 min" -o short-precise | grep -i "attempting to reclaim"'
   ```

4. Check whether PSI is a live signal on this node or only a readable file:

   ```sh
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" | jq '.kubeletconfig.featureGates'
   grep -rn 'PSI' ~/src/kubernetes/pkg/features/kube_features.go
   ```

**Observe** — the gap between your recorded crossing second and the kubelet's log timestamp. Then repeat the run with a *slower* allocator (`sleep 20` between steps) and compare the gap again.

**Expect** — a reaction well inside the housekeeping interval, and — this is the part worth the setup — **a gap that does not grow when the allocation slows down**. A pure poller would show a gap uniformly distributed up to one full interval; a watermark notifier shows a small gap regardless of approach speed. Two runs are enough to tell those apart.

Expect `/proc/pressure/memory` to be readable on Debian 13 and to be near zero at idle, and expect the PSI feature gate to be **off** unless you turned it on — so on this node, pressure is information you can read and not a signal the kubelet acts on. Record which it is, because that is the difference between "the kernel offers this" and "the kubelet uses this", and the two are constantly conflated.

Expect `MemAvailable` from `/proc/meminfo` to disagree with the kubelet's own `memory.available`. Do not fix it yet — [exercise 26](26-the-metric-is-the-file.md) is where that disagreement becomes the finding.

**Write down** — the two measured gaps, the housekeeping interval with its citation, the cgroup file the notifier watches, and your one-sentence answer from before the run, marked right or wrong.

**Footprint note** — same contained hog as [exercise 12](12-an-eviction-you-configured.md), run twice. No change to the 6.5GB steady state.

**Teardown** — `kubectl delete ns evict` and kill the sampling loop. **Leave the kubelet configuration in place.** **The topology stays.**
