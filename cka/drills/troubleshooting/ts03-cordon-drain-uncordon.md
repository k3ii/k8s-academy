<a id="ts03"></a>
# TS3 — Make `drain` refuse, say exactly why, then get it through legitimately

**Reflex** · **Pinned** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Troubleshooting / Troubleshoot clusters and nodes

> **`kubectl drain` has two different ways of saying no, and they want opposite responses.** A DaemonSet pod, a bare pod or an `emptyDir` is an *immediate refusal* whose answer is a flag. A PodDisruptionBudget is not a refusal at all — it is an eviction loop that retries until you give up — and **no flag fixes it**. Reaching for `--force` on the second kind is the mistake this drill exists to burn out of you.

> **Needs three nodes.** Two workers so a drained pod has somewhere to go; this is why it sits on `workhorse` and not on the daily driver.

**Break it** — *pass 1 only.*

1. A DaemonSet across both workers. Drain one. Read the refusal; add the flag that answers it.
2. A bare pod — `kubectl run`, no controller — on the same node. Drain again. Different refusal, different flag, and understand that the flag means *this pod is not coming back*.
3. A Deployment of **two** replicas with a PDB of `minAvailable: 2`, both replicas on the node you are draining. Drain. Watch it **not refuse**: it evicts nothing and retries, printing `Cannot evict pod as it would violate the pod's disruption budget`, forever.
4. Get it through **legitimately** — three ways, and say which you would use in a change window: scale the Deployment up so the budget can be met elsewhere, relax `minAvailable`, or delete the PDB and accept the disruption deliberately. `--force` and `--disable-eviction` are the fourth way and they are the wrong answer here; know what each actually does before you rule it out.
5. `uncordon`, and confirm the scheduler uses the node again — which is not automatic for pods already placed elsewhere.

**Observe**

```sh
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
kubectl get pdb -A
kubectl describe pdb <name> | sed -n '/Status/,$p'    # ALLOWED DISRUPTIONS is the number that matters
kubectl get nodes -o custom-columns=NAME:.metadata.name,SCHEDULABLE:.spec.unschedulable
kubectl get events -A --field-selector reason=EvictionBlocked --sort-by=.lastTimestamp
```

**Done when** — you can state, cold, which refusals take a flag and which do not, and `ALLOWED DISRUPTIONS: 0` makes you look at the PDB rather than at the node.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. You build the DaemonSet, the bare pod and the PDB yourself. | 10 min |
| **2** | A node already carrying unrelated workload. Same four causes, real noise. | 8 min |
| **3** | **Injected.** A drain is already blocked when you arrive and nobody says by what. | **5 min** |

**Teardown** — `uncordon` **every** node before you leave, and delete the PDB. A cordoned node left behind silently halves the next drill's capacity and looks like a scheduling bug.

**See also** — **TS4** is the involuntary version of the same event and **must be the last object in any `workhorse` block**, because it destroys the cluster's usable state. **B2** is where a legitimate drain actually gets used.
