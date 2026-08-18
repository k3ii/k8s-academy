<a id="rolling-update-predictions"></a>
# Predict the ReplicaSet counts at every step of a rollout

**Claim** — given `replicas`, `maxSurge` and `maxUnavailable`, you can write down the pod count of the old and new ReplicaSet at each step of a rolling update *before* running it, and be right — including the step where the totals exceed `replicas`.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. A Deployment with numbers chosen so the arithmetic is not trivial:

   ```yaml
   spec:
     replicas: 5
     strategy:
       rollingUpdate: {maxSurge: 2, maxUnavailable: 1}
   ```

   Use an image with a slow start (`command: ["sh","-c","sleep 15; exec nginx -g 'daemon off;'"]`) so the intermediate states last long enough to see.

2. **Write the prediction table first.** Rows are moments in time, columns are: old RS pods, new RS pods, total, ready. Predict the maximum total and the minimum ready. Then state the general rule: what caps each?
3. Roll it: `kubectl set image deploy/web app=nginx:1.27` and watch:

   ```sh
   kubectl get rs -w -o custom-columns=NAME:.metadata.name,DESIRED:.spec.replicas,CURRENT:.status.replicas,READY:.status.readyReplicas
   ```

4. Compare against the prediction. Then re-run with `maxSurge: 0, maxUnavailable: 1` and predict again — a rollout that can never exceed `replicas` is a different shape and takes visibly longer.
5. Now `kubectl rollout undo`. Predict first: does this create a *third* ReplicaSet, or reuse the first? Check with `kubectl get rs` and look at `pod-template-hash`.
6. Roll three more times, then `kubectl get rs`. Count them, then find the field that decides how many are kept:

   ```sh
   kubectl get deploy/web -o jsonpath='{.spec.revisionHistoryLimit}{"\n"}'
   ```

**Observe** — `kubectl rollout status`, `kubectl rollout history deploy/web`, and `kubectl describe rs <old>` for the scale-down events in order.

**Expect** — the maximum total is `replicas + maxSurge` and the minimum ready is `replicas - maxUnavailable`; the controller moves in whichever direction has slack, which is why a rollout with `maxSurge: 0` proceeds one pod at a time and stalls entirely if a new pod never becomes ready. `rollout undo` **reuses** the old ReplicaSet — it is still there at zero replicas, with the same `pod-template-hash`, and scaling it back up is the whole of a rollback. That retained-and-empty ReplicaSet is the mechanism [the incident note](24-the-incident-note.md) has to explain.

**Write down** — the prediction table with actuals beside it, and the two capping rules in one line each. [Module 1.3 wants the predictions, not the observations](../../phases/01-operate-shallow.md#m1-3).

**Teardown** — leave `deploy/web`; [the probes exercise](09-probes-three-kinds.md) rewires it. **The topology stays.**
