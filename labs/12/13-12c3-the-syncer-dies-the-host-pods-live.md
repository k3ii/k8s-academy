<a id="12c3-the-syncer-dies-the-host-pods-live"></a>
# 12.C3 — delete the vcluster syncer and watch the real half keep running while the tenant's view goes dark

**Claim** — delete the vcluster syncer pod and the two halves of a tenant come apart exactly along the real/shim line: the host pods keep running (they are real containers on a real node, and nothing killed them), while the tenant's control-plane view goes dark (the apiserver serving that view is the pod you just deleted). The failure localises the shim, which is the whole mechanism claim of [the module](12-the-same-pod-in-two-apiservers.md) made visible by breaking it.

**Rests on** — [the same-pod-twice exercise](12-the-same-pod-in-two-apiservers.md), which established which half is real and which is a shim; this drill proves it by removing the shim.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued, `vcluster-a` still up.

**Read** — [the drill's chaos-table row](../../phases/12-gitops-platform.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand: `kubectl delete` the syncer and observe which half survives.

**Do** — leave a workload running in the tenant, then delete the syncer:

```sh
vcluster connect vcluster-a -- kubectl run keeper --image=nginx --restart=Never
kubectl get pod -n vcluster-a | grep keeper     # the real host pod, running
kubectl delete pod -n vcluster-a -l app=vcluster   # kill the syncer (its own pod)
# the tenant's view is now unreachable:
vcluster connect vcluster-a -- kubectl get pods   # times out / errors — the apiserver is gone
# the real pod, on the host, is untouched:
kubectl get pod -n vcluster-a | grep keeper     # still Running — nothing killed the container
```

**Observe** — the tenant `kubectl` failing because the apiserver it talks to *was* the deleted pod, while the host pod backing the tenant workload keeps running because it is a real container the host kubelet owns, not a thing the syncer keeps alive. The syncer restarts (it is a StatefulSet) and the tenant view returns — proving the shim is recoverable and the real half never needed it.

**Expect** — a clean split: control-plane view down, workloads up. If the host pod died when you deleted the syncer, that contradicts the real/shim model — recheck, because it would mean the workload was not the real half you thought.

**Write down** — which half kept working and which went dark, and one sentence on why deleting one pod took out an apiserver but not the containers it had been presenting.

**Teardown** — let the syncer StatefulSet restore itself, delete `keeper`, and keep `vcluster-a` or delete it now — [module 12.5](14-kro-custom-resource-in-children-out.md) does not need it, but [the capstone](18-the-platform-and-its-critique.md) reuses one tenant. **The topology stays.**
