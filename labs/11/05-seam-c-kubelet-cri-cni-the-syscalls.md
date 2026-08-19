<a id="seam-c-kubelet-cri-cni-the-syscalls"></a>
# Seam C: the bound pod becomes a process — kubelet to CRI to CNI, ending on a `clone`/`setns` you once made by hand

**Artifact** — the sub-path `config/apiserver.go → pod_workers.go → kuberuntime_manager.computePodActions → CRI → CNI` cited `file:line` at a stated sha, ending with the veth/netns the CNI ADD produced and the [P0](../../phases/00-linux-primitives.md) syscall it reduces to. Two areas — [Area 7](../../strands/source-reading.md#area-7-kubelet) (P6) and [Area 5](../../strands/source-reading.md#area-5-networking) (P7) — and the point where the loop closes: the container this trace produces *is* the namespaces and cgroups you created by hand in week one, now created for you.

**Rests on** — [Seam B](04-seam-b-watch-cache-scheduler-binding.md), which set the node; [the CRI calls one pod makes, read in P6](../../phases/06-kubelet-node.md#m6-1); [the CNI plugin you built in P7](../../phases/07-networking.md#m7-2), which is these primitives automated; and [the P0 syscalls](../../phases/00-linux-primitives.md) the whole trace terminates on.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the module framing](../../phases/11-synthesis.md#m11-4). The CRI RuntimeService split and the CNI ADD were read in [P6](../../phases/06-kubelet-node.md#m6-1) and [P7](../../phases/07-networking.md#m7-2); this exercise cites the decision point and follows it across the two gRPC/exec boundaries to the kernel. [P6's capstone could only *watch* this far end](../../phases/06-kubelet-node.md); here you cite it.

> **Question to answer from the source:** `computePodActions` decides *what* to do; cite the line where it decides a container must be created, follow it to the CRI call, then name the CNI ADD result — the veth and netns — and point at the [P0](../../phases/00-linux-primitives.md) syscall (`clone`/`setns`/`unshare`) it corresponds to. The trace ends on a syscall you once made yourself.

**Build** — create a pod on the worker, then read the seam from the node side: the kubelet's CRI calls to the runtime and the CNI ADD that wired the netns, ending at the namespaces the container now holds.

```sh
kubectl run seamc --image=nginx --restart=Never
WK=10.10.10.131
# the CRI calls the kubelet made for this pod:
ssh zain@$WK 'sudo crictl ps --name seamc; sudo crictl inspect $(sudo crictl ps -q --name seamc) | grep -i -A2 "namespaces\|pid"'
# the netns the CNI ADD produced — the veth end and the namespace itself:
ssh zain@$WK 'sudo ip netns list; sudo lsns -t net | grep -i nginx || true'
```

**Verify from outside** — a reader opens `computePodActions` at your sha, finds the create decision, follows the cited line to the CRI call, and matches your named CNI result (a veth pair, a netns) to a P0 syscall. "The kubelet starts it" fails; `computePodActions:NNN → CRI CreateContainer → CNI ADD → clone(CLONE_NEWNET)` passes.

**Expect** — the pod's namespaces present on the worker and traceable to a `clone`/`setns` — the same primitives [P0](../../phases/00-linux-primitives.md) made by hand, now made by the machine. [Exercise 6](06-11c4-kill-one-trace-component-mid-flight.md) breaks the CNI to strand the pod at this seam's last frame.

**Write down** — the `config/apiserver.go → pod_workers.go → computePodActions → CRI → CNI` sub-path cited to source, ending with the P0 syscall the running container reduces to. The final third; the three sub-paths joined are [the capstone](07-the-joined-trace-terminal-to-container.md).

**Footprint note** — [`pair` at 5.0GB](../../strands/lab-topologies.md#pair), unchanged.

**Teardown** — `kubectl delete pod seamc`; **the topology stays** — [exercise 6](06-11c4-kill-one-trace-component-mid-flight.md) breaks Seams B and C on this same cluster, then [the joined trace](07-the-joined-trace-terminal-to-container.md) assembles all three.
