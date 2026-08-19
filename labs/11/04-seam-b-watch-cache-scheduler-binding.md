<a id="seam-b-watch-cache-scheduler-binding"></a>
# Seam B: the persisted pod becomes a scheduled one — `spec.nodeName` empty to set, and the `Binding` POST that did it, cited

**Artifact** — the sub-path `watch cache → scheduler informer → schedule_one.go → Binding` with the bind line cited `file:line` at a stated sha, and the before/after of `spec.nodeName` captured live — empty at create, set the instant the bind lands. One area, [Area 3](../../strands/source-reading.md#area-3-scheduler) (P5): how the persisted-but-unscheduled pod from [Seam A](02-seam-a-client-apiserver-etcd.md) acquires a node.

**Rests on** — [Seam A](02-seam-a-client-apiserver-etcd.md), which left the pod in etcd with no node; [the paper map](01-the-paper-trace-before-the-cluster.md); and [the scheduler you built from scratch in P5](../../phases/05-scheduler.md#m5-1) — a ~200-line scheduler that watches unscheduled pods and POSTs a `Binding` is the exact mechanism this seam cites in the real one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Two nodes are enough to watch the scheduler *choose* one.

**Read** — [the module framing](../../phases/11-synthesis.md#m11-3). The filter/score cycle and why the bind is asynchronous were read in [P5](../../phases/05-scheduler.md#m5-1); this exercise cites the bind against a live create and watches the field move. Live-verify the path — [the scheduler queue moved to `backend/queue/`, older citations are stale](../../strands/source-archaeology.md#stale-paths).

> **Question to answer from the source:** the scheduler does not mutate the pod's node field directly — it POSTs a `Binding`. Cite the line in `schedule_one.go` that issues the bind, and explain why binding is a *separate write* through the apiserver (a second trip through [Seam A](02-seam-a-client-apiserver-etcd.md), now for a `Binding` subresource) and not an in-place update of the pod the scheduler already holds in cache.

**Build** — create a fresh pod under a watch so the transition is visible, then read the bind out of source and confirm the field moved:

```sh
kubectl run seamb --image=nginx --restart=Never &
kubectl get pod seamb -w -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
# nodeName is empty for the first frames, then set the moment the Binding lands
```

**Verify from outside** — a reader opens `schedule_one.go` at your sha and finds the bind issued as a POST of a `Binding`, not an in-place pod update; and your capture shows `spec.nodeName` empty then set, with nothing in between. The explanation must say *why* it is a separate write — the scheduler's cached pod is a stale copy, and the apiserver is the single writer of record. [Exercise 6](06-11c4-kill-one-trace-component-mid-flight.md) breaks this seam to show the frame that gives up when no node can be chosen.

**Expect** — `nodeName` empty for the first observed frames, then set; and a bind line that is a `Binding` POST. If you find the scheduler writing `nodeName` directly, you are reading the wrong frame — the real one goes through the apiserver.

**Write down** — the `watch cache → informer → schedule_one.go → Binding` sub-path with the bind line cited, and the `spec.nodeName` before/after. The middle third of [the joined trace](07-the-joined-trace-terminal-to-container.md).

**Footprint note** — [`pair` at 5.0GB](../../strands/lab-topologies.md#pair), unchanged.

**Teardown** — `kubectl delete pod seamb`; **the topology stays** for [Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md).
