<a id="rolling-update-predictions"></a>
# Predict the ReplicaSet counts at every step of a rollout

**Claim** — you are given `replicas`, `maxSurge` and `maxUnavailable`. From those three numbers you can write down the pod count of the old ReplicaSet and of the new ReplicaSet at each step of a rolling update. You do this *before* you run the update, and you are right. This includes the step where the totals exceed `replicas`.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Make a Deployment with numbers that keep the arithmetic non-trivial:

   ```yaml
   spec:
     replicas: 5
     strategy:
       rollingUpdate: {maxSurge: 2, maxUnavailable: 1}
   ```

   Use an image with a slow start, such as `command: ["sh","-c","sleep 15; exec nginx -g 'daemon off;'"]`. The slow start makes the intermediate states last long enough to see.

2. **Write the prediction table first.** Each row is a moment in time. The columns are: old RS pods, new RS pods, total, and ready. Predict the maximum total and the minimum ready count. Then state the general rule. What caps each of the two numbers?
3. Roll the deployment with `kubectl set image deploy/web app=nginx:1.27`, and watch:

   ```sh
   kubectl get rs -w -o custom-columns=NAME:.metadata.name,DESIRED:.spec.replicas,CURRENT:.status.replicas,READY:.status.readyReplicas
   ```

4. Compare the result against your prediction. Then run the rollout again with `maxSurge: 0, maxUnavailable: 1`, and predict again. A rollout that can never exceed `replicas` has a different shape, and it takes visibly longer.
5. Now run `kubectl rollout undo`. Predict the result first. Does this command create a *third* ReplicaSet, or does it reuse the first one? Check with `kubectl get rs`, and look at `pod-template-hash`.
6. Roll three more times, then run `kubectl get rs`. Count the ReplicaSets. Then find the field that decides how many of them are kept:

   ```sh
   kubectl get deploy/web -o jsonpath='{.spec.revisionHistoryLimit}{"\n"}'
   ```

**Observe** — run `kubectl rollout status` and `kubectl rollout history deploy/web`. Then run `kubectl describe rs <old>` to see the scale-down events in order.

**Expect** — the maximum total is `replicas + maxSurge`. The minimum ready count is `replicas - maxUnavailable`. The controller moves in whichever direction has slack. That behaviour explains two things. A rollout with `maxSurge: 0` proceeds one pod at a time. It also stalls completely if a new pod never becomes ready. Note what `rollout undo` does: it **reuses** the old ReplicaSet. That ReplicaSet is still there, at zero replicas, with the same `pod-template-hash`. Scaling it back up is the whole of a rollback. That retained and empty ReplicaSet is the mechanism which [the incident note](24-the-incident-note.md) has to explain.

**Write down** — the prediction table, with the actual counts beside each prediction. Then write the two capping rules, one line each. [Module 1.3 wants the predictions, and not the observations](../../phases/01-operate-shallow.md#m1-3).

**Teardown** — leave `deploy/web` in place, because [the probes exercise](09-probes-three-kinds.md) rewires it. **The topology stays.**
