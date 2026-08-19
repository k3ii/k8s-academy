<a id="11c4-kill-one-trace-component-mid-flight"></a>
# 11.C4 — kill one component and the pod stops at the exact frame that component owns

**Claim** — with the scheduler stopped a new pod persists but stays `Pending` at the scheduler frame that gives up; with every node cordoned it is `Pending`/`unschedulable`; with the CNI plugin binary renamed it reaches the node but sticks at `ContainerCreating`, Seam C's last frame failing. Each stall names a frame, and the frame is one you cited in [Seam B](04-seam-b-watch-cache-scheduler-binding.md) or [Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md). One drill, demonstrated at two seams: the gap tells you which frame owns which transition.

**Rests on** — [Seam B](04-seam-b-watch-cache-scheduler-binding.md) (the bind frame) and [Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md) (the CNI frame). Do this after both are cited — the stalls are only legible against the frames they name.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the drill's chaos-table row](../../phases/11-synthesis.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand, and permanently so: the skill is reading the stall's location off the pod's own status and events.

**Do — seam B, no node to bind:** cordon every node and create a pod; it persists but never binds. Uncordon one and watch the exact frame fire.

```sh
kubectl cordon 10.10.10.130 10.10.10.131 2>/dev/null; \
  for n in $(kubectl get no -o name); do kubectl cordon ${n#node/}; done
kubectl run stalled --image=nginx --restart=Never
kubectl get pod stalled -o wide          # Pending; describe shows 'unschedulable'
kubectl describe pod stalled | sed -n '/Events/,$p'
kubectl uncordon $(kubectl get no -o name | head -1 | cut -d/ -f2)   # binds now
```

**Do — seam C, no CNI to wire the netns:** on the worker, move the plugin binary aside and create a pod pinned there; it schedules (Seam B completes) but sticks at `ContainerCreating` — the [CRI→CNI seam P6 named as the one it could only watch](../../phases/06-kubelet-node.md), now failing where you cited it.

```sh
WK=10.10.10.131
ssh zain@$WK 'sudo mv /opt/cni/bin/bridge /opt/cni/bin/bridge.off'   # or the plugin in use
kubectl run cnistall --image=nginx --restart=Never --overrides='{"spec":{"nodeName":"10.10.10.131"}}'
kubectl get pod cnistall -o wide          # ContainerCreating, not Running
kubectl describe pod cnistall | sed -n '/Events/,$p'   # CNI ADD failing
```

**Observe** — scheduler-side, the pod is `Pending`/`unschedulable` and never leaves the scheduler; CNI-side, it is `Scheduled` but never `Running`, stuck at `ContainerCreating`. Two different stalls, two different frames, each the one the missing component owns.

**Expect** — `Pending` when the bind cannot happen and `ContainerCreating` when the netns cannot be wired. The stall's *name* is the diagnostic: it points at the exact seam, which is the whole reason the trace was worth citing.

**Write down** — for each kill, the pod phase, the events line, and the Seam-B or Seam-C frame it corresponds to.

**Teardown** — restore the CNI binary and uncordon everything (the repair is part of the drill — a pod must reach `Running` again), then delete the pods; **the topology stays**:

```sh
ssh zain@10.10.10.131 'sudo mv /opt/cni/bin/bridge.off /opt/cni/bin/bridge'
for n in $(kubectl get no -o name); do kubectl uncordon ${n#node/}; done
kubectl delete pod stalled cnistall --ignore-not-found
```
