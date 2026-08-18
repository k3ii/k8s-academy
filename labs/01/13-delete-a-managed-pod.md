<a id="delete-a-managed-pod"></a>
# Chaos drill 1.C1 — delete a pod that something is watching

**Claim** — you can say which controller recreated the pod, **what two values it compared**, and why deleting the pod is futile against a Deployment while deleting the ReplicaSet is not. **[The gate names this drill](../../phases/01-operate-shallow.md#gate): if you cannot say it, you stay in P1.**

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with `deploy/web` at 3 replicas. [By hand](../../strands/chaos.md#principle) — there is no tool here and there does not need to be, which is the point of the drill this early.

**Do**

1. **Write the prediction first**, for each of five deletions: what comes back, how quickly, with what name, and *which* controller acted.
   - delete one pod
   - delete all three pods at once
   - delete the ReplicaSet
   - delete the ReplicaSet with `--cascade=orphan`
   - delete the Deployment
2. Run them, one at a time, restoring between each, with a watch running:

   ```sh
   kubectl get pods,rs,deploy -w
   ```

3. After the single-pod delete, find the evidence of *who*:

   ```sh
   kubectl get events --sort-by=.lastTimestamp | tail -5
   kubectl get pod <new> -o jsonpath='{.metadata.ownerReferences}' | jq
   ```

   The event's source and the owner reference name two different objects. Both are correct; say what each one means.

4. `kubectl scale deploy/web --replicas=0`, then back to 3. Note which object's `spec` you changed and which object's `spec` changed *as a consequence*, and how many levels the change propagated.
5. Now the orphan case from step 1, properly: after `--cascade=orphan`, the pods survive with no owner. Watch what the Deployment does about it — it creates a **new** ReplicaSet and you now have three unmanaged pods it will never clean up. Say why the label selector did not save you.
6. Finally, contrast with [the static pod](04-static-pod-blip.md): delete the mirror pod for `kube-scheduler`. Nothing recreates it, and it comes back anyway. Two different mechanisms, two different answers to "what put it back".

**Expect** — a replacement within a second, with a fresh random suffix and the same `pod-template-hash`; the actor is the **ReplicaSet controller**, not the Deployment controller, and the two values it compared are `rs.spec.replicas` against the count of pods matching `rs.spec.selector` that it currently sees. It has no record that a pod was deleted and it needs none — nothing about the loop is event-driven in the sense that word usually means. Deleting the ReplicaSet is equally futile one level up, and only deleting the Deployment ends the chain, because the chain is owner references all the way down and garbage collection walks them.

**Write down** — the five-row prediction table with actuals, and the sentence the gate asks for: which controller, and what it compared. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the same claim in falsifiable form.

**Teardown** — delete any orphaned pods from step 5 and restore `deploy/web` to 3 replicas. **The topology stays.**
