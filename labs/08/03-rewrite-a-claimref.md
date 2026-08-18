<a id="rewrite-a-claimref"></a>
# Binding is reconciled state, not a transaction

**Claim** — a bind is two mutable fields on two objects that a controller keeps agreeing with each other. Edit one side and the controller's response tells you which side it treats as authoritative.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the released PV](02-released-not-available.md).

**Do**

1. Bind a PVC to a PV and confirm both `pv.spec.claimRef` and `pvc.spec.volumeName` are populated.
2. Edit the PV's `claimRef` to name a **different** PVC — one that exists and is `Pending`. Watch what `syncVolume` does about it.
3. Now do the mirror: clear `pvc.spec.volumeName` on a bound PVC and watch what `syncClaim` does.
4. Create the genuinely ambiguous state — two PVCs whose `volumeName` both name the same PV — and record which one the controller lets keep it.

**Observe**

```sh
kubectl get pv,pvc -o wide --watch
kubectl -n kube-system logs -l component=kube-controller-manager -f | grep -i 'claim\|volume'
kubectl get events --sort-by=.lastTimestamp | tail -30
```

**Expect** — the controller does not error and does not roll anything back. It reconciles toward whichever state it can make consistent, and it logs the decision. Nothing here is transactional: there is no point at which the bind is atomic, which is why the two-object design needs `claimRef` at all.

**Write down** — which field the controller treats as authoritative in step 2, cited to the function in `pv_controller.go` that made the call.

**Teardown** — delete the six PVs and their claims; [delayed binding](04-delayed-binding-observed.md) wants a clean namespace but the same cluster.

```sh
kubectl delete pvc --all && kubectl delete pv --all
```
