<a id="released-not-available"></a>
# A released PV does not return to the pool

**Claim** — deleting a bound PVC moves its PV to `Released`, not `Available`, and no controller will ever move it back on its own. The reclaim policy decides who does.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up from [the bind predictions](01-predict-the-bind.md), with its six PVs.

**Do**

1. Delete one of the bound PVCs from [the bind predictions](01-predict-the-bind.md). Watch its PV.
2. State, before checking, what `Released` means that `Available` does not — in terms of the `claimRef` still sitting on the PV object.
3. Make it `Available` again. Do it by the mechanism the controller respects, not by deleting and recreating the PV.
4. Repeat with a PV whose `persistentVolumeReclaimPolicy` is `Delete` rather than `Retain`, and with `Recycle` if the API still accepts it. Note which of the three the cluster actually performs and which is deprecated scaffolding.

**Observe**

```sh
kubectl get pv -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,POLICY:.spec.persistentVolumeReclaimPolicy,CLAIM:.spec.claimRef.name
kubectl get pv <name> -o yaml | grep -A5 claimRef
```

**Expect** — `Released` with a stale `claimRef` naming a PVC that no longer exists. Clearing that field is what returns the PV to the pool; the `Retain` policy exists precisely so that a human looks at the data first. `Delete` removes the PV object and, with a real provisioner, the backing volume too — which is the setting that loses data when a namespace is deleted carelessly.

**Write down** — the three reclaim policies, which controller acts on each, and one sentence on why `Retain` is the safe default for a PV you created by hand.

**Teardown** — leave it up; [the claimRef rewrite](03-rewrite-a-claimref.md) uses the same PVs.
