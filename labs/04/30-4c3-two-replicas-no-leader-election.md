<a id="4c3-two-replicas-no-leader-election"></a>
# 4.C3 — two replicas, no lease, and the fight you can measure

**Claim** — with `--leader-elect=false` and two replicas, the operator does not visibly break, and that is the drill. The damage is a measurable fight — a doubled write rate, a conflict storm, a status field that flaps between two values — and you have to go and look for each one, because the Ensembles keep converging the whole time. Turning the lease back on ends all three at once.

**Rests on** — [the working leader election](28-two-replicas-one-lease.md), which this removes, and [the two-leader window](29-why-the-renew-deadline-is-shorter.md), which showed why converging is not the same as being correct.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — the escape hatch is one command, and it is worth having in a second terminal before you start: `kubectl -n academy-build scale deploy academy-operator --replicas=1`. Everything below is reversible by that plus flipping the flag back.

Give the operator a `--leader-elect` flag defaulting to `true`, named after [`kube-controller-manager`'s](../../phases/04-controllers.md#m4-5) because it is the same switch. Seed ten Ensembles, each with `voices: 3`, so there is enough work for two loops to collide over:

```sh
for i in $(seq 1 10); do
  kubectl apply -f - <<YAML
apiVersion: academy.k3ii.dev/v1alpha1
kind: Ensemble
metadata: {name: fight-$i, namespace: default}
spec: {voices: 3, registryNamespace: ensemble-registry}
YAML
done
```

**Do**

1. Predict, in writing, before you change anything. Two identical controllers, both reconciling all ten objects: which of these do you expect — duplicate ConfigMaps, a status that flaps, errors in the logs, or nothing visible at all? Commit to an answer. The value of this drill is in being wrong about it.

2. Turn the lease off and let both run:

   ```sh
   kubectl -n academy-build set args deploy/academy-operator -- --leader-elect=false
   kubectl -n academy-build scale deploy academy-operator --replicas=2
   kubectl -n academy-build logs -l app=academy-operator --prefix -f | tee /tmp/fight.log
   ```

3. Make one replica slow, so the two hold different views of the same object. Restart one pod with `--slow-reconcile=3s` — [the flag from the mid-reconcile kill](17-4c1-kill-it-mid-reconcile.md) — and leave the other at full speed.

4. Change something while both are watching, and watch the status rather than the children:

   ```sh
   kubectl patch ensemble fight-1 --type=merge -p '{"spec":{"voices":6}}'
   kubectl get ensemble fight-1 -o jsonpath='{.status}{"\n"}' ; sleep 1 ; kubectl get ensemble fight-1 -o jsonpath='{.status}{"\n"}'
   kubectl get ensemble fight-1 -w -o custom-columns=GEN:.metadata.generation,OBS:.status.observedGeneration,READY:.status.readyVoices,RV:.metadata.resourceVersion
   ```

5. Count the fight instead of describing it:

   ```sh
   grep -c 'STAGE/write' /tmp/fight.log
   grep -ci 'conflict\|the object has been modified' /tmp/fight.log
   kubectl get events --field-selector involvedObject.name=fight-1 --sort-by=.lastTimestamp | tail
   ```

   Then do the same run again with one replica and compare the two write counts for the same ten objects.

6. End it. Set `--leader-elect=true`, leave both replicas up, and repeat step 5.

**Observe** — the three numbers from step 5 under each of the three configurations (two replicas no lease, one replica, two replicas with lease), and the `RV` column's rate of change in step 4.

**Expect** — the ConfigMaps are fine. There is no duplicate: [the deterministic name](22-expectations-or-over-create.md) turns the second create into an `AlreadyExists` that your code already ignores, and this is the prediction most people get wrong.

What you get instead:

- **Roughly double the writes** for the same work, and every write is a `resourceVersion` bump that every watcher in the cluster now has to process. Two replicas of a controller are not two workers sharing a queue; they are two workers doing the whole queue.
- **A conflict count that was zero and is now not.** These are recovered — each loses a round trip and retries — so the objects converge and the logs look busy rather than broken.
- **A status that flaps** in step 4, because the slow replica writes a `readyVoices` computed from a view that was already stale when it started. Each write succeeds. Nothing is in conflict, because each writer re-read first. The field simply holds the wrong number for seconds at a time, and anything reading that status to make a decision reads the wrong number too.
- **Duplicate Events** on the same object, which is the cheapest symptom to spot in a real cluster and the one people notice first.

Step 6's numbers should return to the single-replica ones exactly. That is the finding worth stating: the lease bought no correctness the API server was not already providing, and bought a very large amount of *quiet*.

**The generalisation** — this is why `kube-controller-manager` and `kube-scheduler` ship with `--leader-elect=true` and why nobody runs them any other way, and it is what [3.C4](../../phases/03-api-machinery.md#chaos) was showing you from the other side when those leases went unrenewed during the outage.

**Write down** — your step 1 prediction verbatim, the nine numbers from step 5, the flapping status values with their timestamps, and one sentence on which of the four symptoms you would actually detect in production and how.

**Footprint note** — unchanged from [the previous exercise](28-two-replicas-one-lease.md); two replicas is the steady state for all of module 4.5.

**Teardown** — `--leader-elect=true`, scale back to one replica, `kubectl delete ensemble fight-1 ... fight-10`, and confirm `ensemble-registry` has no `fight-*` keys left — a fight during deletion is the one way this drill can leave litter. **The topology stays** — [the second operator](31-scaffold-the-same-operator.md) is built against this same cluster.
