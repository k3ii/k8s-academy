<a id="delete-a-managed-pod"></a>
# Chaos drill 1.C1 — delete a pod that something is watching

**Claim** — you can say three things. You can name the controller that recreated the pod. You can say **what two values it compared**. You can explain why deleting the pod is futile against a Deployment, while deleting the ReplicaSet is not. **[The gate names this drill](../../phases/01-operate-shallow.md#gate): if you cannot say those things, you stay in P1.**

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with `deploy/web` at 3 replicas. Do this drill [by hand](../../strands/chaos.md#principle). There is no tool here, and there does not need to be one. That is the point of running this drill so early.

**Do**

1. **Write the prediction first.** Do it for each of five deletions. For each one, say what comes back, how quickly, with what name, and *which* controller acted.
   - delete one pod
   - delete all three pods at once
   - delete the ReplicaSet
   - delete the ReplicaSet with `--cascade=orphan`
   - delete the Deployment
2. Run the five deletions, one at a time. Restore the state between each one. Keep a watch running:

   ```sh
   kubectl get pods,rs,deploy -w
   ```

3. After the single-pod delete, find the evidence of *who* acted:

   ```sh
   kubectl get events --sort-by=.lastTimestamp | tail -5
   kubectl get pod <new> -o jsonpath='{.metadata.ownerReferences}' | jq
   ```

   The source of the event and the owner reference name two different objects. Both are correct. Say what each one means.

4. Run `kubectl scale deploy/web --replicas=0`, then scale back to 3. Note two things. Which object's `spec` did you change? Which object's `spec` changed *as a consequence*? Then say how many levels the change propagated.
5. Now do the orphan case from step 1 properly. After `--cascade=orphan`, the pods survive with no owner. Watch what the Deployment does about that. It creates a **new** ReplicaSet. You now have three unmanaged pods, and it will never clean them up. Say why the label selector did not save you.
6. Finally, contrast this behaviour with [the static pod](04-static-pod-blip.md). Delete the mirror pod for `kube-scheduler`. Nothing recreates it, and it comes back anyway. There are two different mechanisms here, and two different answers to the question "what put it back?".

**Expect** — a replacement arrives within one second. It has a fresh random suffix and the same `pod-template-hash`. The actor is the **ReplicaSet controller**, and not the Deployment controller. It compared two values: `rs.spec.replicas`, against the count of pods that match `rs.spec.selector` and that it currently sees. It has no record that a pod was deleted, and it needs none. Nothing about the loop is event-driven in the usual sense of that word. Deleting the ReplicaSet is equally futile, one level up. Only deleting the Deployment ends the chain. The chain is owner references all the way down, and garbage collection walks them.

**Write down** — the prediction table of five rows, with the actual results. Then write the sentence that the gate asks for: which controller acted, and what it compared. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the same claim in falsifiable form.

**Teardown** — delete any orphaned pods from step 5. Restore `deploy/web` to 3 replicas. **The topology stays.**
