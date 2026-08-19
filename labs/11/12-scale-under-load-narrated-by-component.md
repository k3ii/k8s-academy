<a id="scale-under-load-narrated-by-component"></a>
# Capstone 2b — scale under real load, and name from observation which component acted at each step, with the latency of each hop

**Artifact** — a scale-under-load run narrated by component: metrics → HPA decision → new pod persisted ([Seam A](02-seam-a-client-apiserver-etcd.md)) → scheduled ([Seam B](04-seam-b-watch-cache-scheduler-binding.md)) → running ([Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md)) → in the Service's `EndpointSlice` ([P7](../../phases/07-networking.md#m7-4)) — each step attributed to the component that acted and the measured latency of the hop, and, when a node cannot satisfy the request, the named `Pending` frame. The trace you cited as *source* is now the trace you narrate as *operation*: same seams, watched under load instead of read in `k/k`.

**Rests on** — [the joined trace](07-the-joined-trace-terminal-to-container.md) (every hop you are about to time, you have already cited) and [the upgrade](11-the-upgrade-that-drops-nothing.md), which left `workhorse` up and serving. This is the second half of [the phase's second capstone](../../phases/11-synthesis.md#capstone); together they are one claim from two sides.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), continued from the upgrade — its [1-core workers](../../strands/lab-topologies.md#workhorse) are what make a `Pending` frame appear when you push past capacity, rather than a cluster that absorbs any load without choosing.

**Read** — [the capstone spec](../../phases/11-synthesis.md#capstone) and [P7's Service/EndpointSlice module](../../phases/07-networking.md#m7-4), the last hop the scaled pod must reach before it takes traffic. Nothing new is installed — metrics and the HPA are configured, not brought in.

**Do** — put an HPA on the workload, drive load past its threshold, and watch each component act in turn — timing the hops:

```sh
kubectl autoscale deployment web --cpu-percent=50 --min=2 --max=12
# drive load past the threshold (fortio from 11, or more clients):
kubectl run spike --image=fortio/fortio --restart=Never -- \
  load -c 32 -qps 2000 -t 600s http://web
# narrate, timestamping each transition:
kubectl get hpa web -w                    # metrics cross the threshold -> desired replicas rise
kubectl get pods -l app=web -w -o wide    # new pod: Pending -> Scheduled -> Running, per Seam
kubectl get endpointslice -l kubernetes.io/service-name=web -w   # the last hop into traffic
```

**Verify from outside** — a reader follows your narration and finds each step owned by a named component (metrics-server, the HPA controller, the apiserver, the scheduler, the kubelet, the EndpointSlice reconciler) with a measured latency between them — and, at the point `workhorse`'s cores run out, a pod stuck `Pending`/`unschedulable` at the scheduler frame, cited. "Kubernetes scaled it" fails the gate; a per-hop timeline passes.

**Expect** — the HPA to lag the load by its sync period (scaling is not instant, and naming that latency is the point), new pods to walk the three seams you cited, and — once both 1-core workers are full — a `Pending` pod that names the frame that stalls. If everything schedules with room to spare, push the QPS until it does not; the full node is part of the artifact.

**Write down** — the per-hop timeline (component + latency for each of metrics → HPA → Seam A → B → C → EndpointSlice) and the `Pending` frame when a node fills. This is [the gate's scale condition](../../phases/11-synthesis.md#gate): if scaling is still "Kubernetes handled it," the trace did not transfer to operations.

**Footprint note** — [`workhorse` at 7.0GB](../../strands/lab-topologies.md#workhorse), unchanged; the extra pods schedule inside the nodes' existing RAM, not on top of the host budget.

**Teardown — this is the exercise that releases the phase's topology.** Delete the workload and the load generators, then destroy `workhorse`; the descent is over and [P12](../../phases/12-gitops-platform.md) provisions its own `platform`:

```sh
kubectl delete deployment web; kubectl delete service web; kubectl delete hpa web
kubectl delete pod load spike --ignore-not-found
just tofu labs destroy
```
