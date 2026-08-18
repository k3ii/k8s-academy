<a id="an-eviction-as-a-slope"></a>
# The same eviction you already caused, this time as four lines on one graph

**Claim** — an eviction read in a log is a moment, and an eviction read on a time series is a *shape*: an approach with a slope you could have extrapolated, a decision, a discontinuity, and a recovery that overshoots. Everything the log told you is on the graph, and two things the log could not tell you are as well.

**Rests on** — [the honest expression](26-the-metric-is-the-file.md) and [the eviction you drove in exercise 12](12-an-eviction-you-configured.md). This is that same event, instrumented — which is why the phase puts observability last rather than first.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the stack up and the worker on its **default** eviction threshold. The default is small, so the approach takes several minutes — and a long approach is exactly what makes a slope readable.

**Setup** — a Grafana panel with four series on one axis, before you start anything:

1. your honest available-memory expression for `pair-worker`;
2. a horizontal line at the node's configured hard threshold (`kubectl get --raw ".../configz" | jq '.kubeletconfig.evictionHard'`);
3. `container_memory_working_set_bytes` for the hog pod;
4. `kube_pod_container_status_restarts_total` and `kube_pod_status_phase{phase="Failed"}` for the namespace.

**Do**

```sh
kubectl create ns slope
kubectl -n slope apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: climber}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/fill/$i bs=1M count=16 2>/dev/null; i=$((i+1)); sleep 10; done"]
    volumeMounts: [{name: fill, mountPath: /fill}]
  volumes: [{name: fill, emptyDir: {medium: Memory}}]
EOF2
```

Then leave it alone and watch the graph. When the eviction fires, note the wall-clock time, and afterwards line up three timestamps: the moment your extrapolated slope predicted the crossing, the moment the graph shows the crossing, and the moment the kubelet logged the decision.

```sh
ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-15 min" -o short-precise | grep -i -e eviction -e reclaim'
kubectl -n slope get pod climber -o jsonpath='{.status.phase}{"\t"}{.status.reason}{"\n"}'
```

**Observe** — the two things the log could not tell you:

- **How long the node had been in trouble before anything happened.** The slope crosses "obviously heading for the threshold" minutes before it crosses the threshold, and that interval is the entire window in which a human or an autoscaler could have acted.
- **What the recovery actually looks like.** Available memory does not return to the threshold; it jumps past it by roughly `evictionMinimumReclaim`, and then decays again as the page cache refills. The second decay is not a second problem, and telling those apart on a graph is a skill the log cannot teach.

**Expect** — a clean ramp at about 1.6 MB/s, a crossing, a single pod's series going to zero, and a step up in available memory. Expect the kubelet's log timestamp to fall **before** the crossing is visible on the graph — the scrape interval is 30s, so the graph is up to half a minute behind the decision. That lag is the reason a dashboard is a poor incident *detector* and a good incident *explanation*, and it is worth writing in exactly those words.

Expect `kube_pod_status_phase{phase="Failed"}` to go to 1 and **stay there**, because [the evicted pod's corpse is retained](12-an-eviction-you-configured.md). On a real cluster that series climbing over days is the signature of a node quietly evicting on a schedule nobody has looked at.

**Write down** — the annotated screenshot or the four queries with the three timestamps, the measured slope, the extrapolated crossing against the real one, and the overshoot compared with `evictionMinimumReclaim`. That closes [module 6.6's write-down](../../phases/06-kubelet-node.md#m6-6) and [objective 7](../../phases/06-kubelet-node.md#objectives).

**Footprint note** — one hog on the worker, bounded by the node's default eviction threshold, with the recorder safely on the other guest [by construction](25-the-stack-that-must-not-be-evicted.md). Prometheus's 2h retention comfortably covers the whole run; if you want to keep the graph, export the panel rather than extending retention.

**Teardown** — `kubectl delete ns slope`. Confirm `MemoryPressure=False` on the node before moving on. **The topology stays** — [6.C4](28-6c4-disk-pressure-cascade.md) needs the same dashboard.
