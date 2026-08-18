<a id="predict-the-bind"></a>
# Predict which PV a PVC will bind to

**Claim** — you can name the PV a given PVC will bind to *before* applying it, by walking `findBestMatchForClaim`'s predicate in your head, and be right five times out of five.

**Rests on** — [Module 8.2's reading question](../../phases/08-storage.md#m8-2): the order `findBestMatchForClaim` walks candidates in, and the tie-break when two PVs both satisfy a claim. Answer it from `index.go` first; this exercise is worthless as trial and error.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). Everything from Phase 7 is [torn down first](../../strands/lab-topologies.md#teardown), then [provision](../../strands/lab-topologies.md#provision).

**Do**

1. Create six `hostPath` PVs that differ along exactly the axes the predicate tests — two at 5Gi and two at 10Gi; one `ReadWriteOnce` and one `ReadWriteMany` at each size; one with a `storageClassName` and one without; one carrying a label.

   ```yaml
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: pv-5-rwo
     labels: {tier: slow}          # on exactly one of the six
   spec:
     capacity: {storage: 5Gi}
     accessModes: [ReadWriteOnce]  # vary
     storageClassName: ""          # empty on some, "manual" on others
     hostPath: {path: /mnt/pv-5-rwo}
     persistentVolumeReclaimPolicy: Retain
   ```

2. For each of five PVCs, **write the predicted PV and the reason into your journal before `kubectl apply`**, then apply and compare. Include:
   - a 7Gi `ReadWriteOnce` claim — which PV, and how much capacity does the bind waste?
   - a claim carrying a `selector` matching the labelled PV;
   - a claim with `storageClassName: ""` versus one omitting the field entirely — these are not the same request.
3. Write one claim you predict *cannot* bind at all, and confirm it sits `Pending` for the reason you gave.

**Observe**

```sh
kubectl get pv,pvc -o wide --watch
kubectl get pv <name> -o jsonpath='{.spec.claimRef}' | jq
kubectl -n kube-system logs -l component=kube-controller-manager --tail=200 | grep -i 'volume\|claim'
```

**Expect** — five predictions, five matches. The 7Gi claim binds to a 10Gi PV and wastes 3Gi: there is no partial fulfilment in this model. `pv.spec.claimRef` and `pvc.spec.volumeName` are **both** written, by different code paths — the bind is bidirectional and neither side alone is the truth.

**Write down** — the five predictions with outcomes, at least one of them wrong and why, and one paragraph on the capacity waste in step 2 and what it implies for sizing a StorageClass. [Required by the checklist](../../phases/08-storage.md#checklist).

**Teardown** — leave the cluster up; [the released PV](02-released-not-available.md) needs these six PVs.
