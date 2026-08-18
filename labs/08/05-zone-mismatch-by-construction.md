<a id="zone-mismatch-by-construction"></a>
# Build the failure that delayed binding prevents

**Claim** — with `Immediate` binding you can strand a volume in one topology domain while the only pod that wants it must run in another, and the cluster will not fix it. With `WaitForFirstConsumer` the same construction cannot be built.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [delayed binding](04-delayed-binding-observed.md). Two nodes is the minimum for this and it is exactly enough: one domain each.

**Do**

1. Label the two nodes as distinct domains:

   ```sh
   kubectl label node <cp> topology.kubernetes.io/zone=alpha
   kubectl label node <worker> topology.kubernetes.io/zone=beta
   ```

2. Add `allowedTopologies` to the **`Immediate`** class, pinning it to `alpha`:

   ```yaml
   allowedTopologies:
   - matchLabelExpressions:
     - key: topology.kubernetes.io/zone
       values: [alpha]
   ```

3. Create a PVC against it — it binds immediately, in `alpha`.
4. Now create a pod for that PVC with `nodeSelector: {topology.kubernetes.io/zone: beta}`. Record what the pod does and what the scheduler says.
5. Repeat the whole construction against the `WaitForFirstConsumer` class and show the strand cannot occur.

**Observe**

```sh
kubectl get pv <name> -o jsonpath='{.spec.nodeAffinity}' | jq
kubectl describe pod <pod> | sed -n '/Events/,$p'
kubectl -n kube-system logs -l component=kube-scheduler --tail=200 | grep -i 'volume\|node affinity'
```

**Expect** — the pod is unschedulable, and the scheduler's reason names the volume's node affinity rather than the `nodeSelector`. The volume was placed before anyone asked where the pod would run; nothing later can move it. Under `WaitForFirstConsumer` the placement decision is made once, with both constraints in hand.

**Write down** — one paragraph describing this failure to someone who has not done this phase. [The checklist asks for it](../../phases/08-storage.md#checklist), and it is a common production incident.

**Teardown** — leave it up. Remove the zone labels and the pinned class so [the Pending drill](06-four-ways-a-pvc-stays-pending.md) starts from a plain cluster.
