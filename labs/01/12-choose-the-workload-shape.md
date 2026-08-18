<a id="choose-the-workload-shape"></a>
# Five workload kinds, chosen by the property that forces the choice

**Claim** — for each of five workload kinds you can state the one property that makes it the only correct choice, and demonstrate that property rather than assert it. Two of the five differ in exactly one guarantee.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Two nodes matters here: a DaemonSet on one node teaches nothing.

**Do**

1. **DaemonSet.** Deploy one, then check its pods against `kubectl get nodes`. Now cordon the worker and add a *third* node's worth of expectation — you cannot, so instead remove the control plane's taint tolerance and count again. Ask: what scheduled these pods, and what tolerations did the controller add on its own?

   ```sh
   kubectl get ds/agent -o jsonpath='{.spec.template.spec.tolerations}' | jq
   ```

   The tolerations you never wrote are the interesting output.

2. **Job and CronJob.** Run a Job with `completions: 4, parallelism: 2` and a command that exits non-zero one time in three. Watch the retry, then find the two fields that decide when a Job gives up. Schedule a CronJob at `* * * * *`, let three fire, and find where the old ones went.
3. **StatefulSet.** Deploy three replicas with a headless Service. Then demonstrate the three guarantees a Deployment does not give:

   ```sh
   kubectl get pods -l app=db          # names are ordinal, not random
   kubectl delete pod db-1             # comes back as db-1, same name
   kubectl scale sts/db --replicas=0   # watch the order of termination
   kubectl exec -it client -- nslookup db-0.db
   ```

   Predict the scale-down order before running it.

4. **Deployment** you already have. Put it beside the StatefulSet and write the single sentence that distinguishes them.
5. Give one workload each of the five shapes and ask, for each, *what would go wrong if I used a Deployment instead*. Two of them have no good answer, and saying so is the correct result.

**Expect** — the DaemonSet's pods carry five or six tolerations the controller injected, including `node.kubernetes.io/unschedulable`, which is why a DaemonSet pod appears on a cordoned node; the Job's `backoffLimit` and `activeDeadlineSeconds` are the two give-up fields, and the CronJob's history is bounded by `successfulJobsHistoryLimit`. The StatefulSet scales **down in reverse ordinal order** and each pod has a stable DNS name of the form `db-0.db.<ns>.svc`, which is the actual point of the headless Service. **`volumeClaimTemplates` is deliberately not used here** — the persistence half of StatefulSet is [P8](../../phases/08-storage.md)'s subject and this cluster has no provisioner; the ordering and identity guarantees are the half that belongs to P1.

**Write down** — the five-row table: kind, the one forcing property, and the failure you would get from using a Deployment instead.

**Teardown** — delete the DaemonSet, Job, CronJob and StatefulSet, and confirm the CronJob's leftover Jobs went with it. Keep `deploy/web`. **The topology stays.**
