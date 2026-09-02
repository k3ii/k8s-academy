<a id="choose-the-workload-shape"></a>
# Five workload kinds, chosen by the property that forces the choice

**Claim** — for each of five workload kinds, you can state the one property that makes it the only correct choice. You can also demonstrate that property, instead of asserting it. Two of the five kinds differ in exactly one guarantee.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Two nodes matter here, because a DaemonSet on one node teaches nothing.

**Do**

1. **DaemonSet.** Deploy one, then check its pods against `kubectl get nodes`. Now cordon the worker. You cannot add the expectation of a *third* node, so do this instead: remove the toleration for the control plane's taint, and count the pods again. Then ask two questions. What scheduled these pods? Which tolerations did the controller add on its own?

   ```sh
   kubectl get ds/agent -o jsonpath='{.spec.template.spec.tolerations}' | jq
   ```

   The tolerations that you never wrote are the interesting output.

2. **Job and CronJob.** Run a Job with `completions: 4, parallelism: 2`, and give it a command that exits non-zero one time in three. Watch the retry. Then find the two fields that decide when a Job gives up. Next, schedule a CronJob at `* * * * *`, let three of them fire, and find where the old ones went.
3. **StatefulSet.** Deploy three replicas with a headless Service. Then demonstrate the three guarantees that a Deployment does not give:

   ```sh
   kubectl get pods -l app=db          # names are ordinal, not random
   kubectl delete pod db-1             # comes back as db-1, same name
   kubectl scale sts/db --replicas=0   # watch the order of termination
   kubectl exec -it client -- nslookup db-0.db
   ```

   Predict the scale-down order before you run the third command.

4. **Deployment.** You already have one. Put it beside the StatefulSet, and write the single sentence that distinguishes the two.
5. Give one workload to each of the five shapes. For each one, ask the same question: *what would go wrong if I used a Deployment instead?* Two of the five have no good answer, and saying so is the correct result.

**Expect** — the pods of the DaemonSet carry five or six tolerations that the controller injected. One of them is `node.kubernetes.io/unschedulable`, and it is why a DaemonSet pod appears on a cordoned node. The two give-up fields of the Job are `backoffLimit` and `activeDeadlineSeconds`. The history of the CronJob is bounded by `successfulJobsHistoryLimit`. The StatefulSet scales **down in reverse ordinal order**, and each pod has a stable DNS name in the form `db-0.db.<ns>.svc`. That name is the actual point of the headless Service. Note one deliberate omission: **this exercise does not use `volumeClaimTemplates`**. The persistence half of StatefulSet is the subject of [P8](../../phases/08-storage.md), and this cluster has no provisioner. The ordering and identity guarantees are the half that belongs to P1.

**Write down** — the table of five rows: the kind, the one forcing property, and the failure that you would get if you used a Deployment instead.

**Teardown** — delete the DaemonSet, the Job, the CronJob and the StatefulSet. Confirm that the leftover Jobs of the CronJob went with it. Keep `deploy/web`. **The topology stays.**
