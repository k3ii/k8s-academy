<a id="the-lease-changes-hands"></a>
# Both artifacts, two replicas each, and a lease with a transition count

**Artifact** — leader election added to **both** schedulers, and the evidence that it works: a `Lease` whose `holderIdentity` changes and whose `leaseTransitions` increments when the holder is killed, measured once for the hand-written scheduler and once for the framework one. This completes [stage 2](../../strands/build-mechanics.md#two-stages) for both rows of [the artifact table](../../strands/build-mechanics.md#artifact-table).

**Rests on** — both deployments: [the second scheduler](30-a-second-scheduler-by-schedulername.md) and [the two-profile process](31-a-profile-not-a-binary.md). The lease mechanism itself was built and timed in [P4 module 4.5](../../phases/04-controllers.md#m4-5) and is not re-derived here; what is new is that the thing being made singular is a *scheduler*, and the consequence of getting it wrong is different.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. This is the **last exercise on `pair`** — [the next one](33-forge-back-down-and-workhorse-up.md) destroys it.

**Do**

1. **Answer, before building anything, why a scheduler needs this at all.** You already proved in [5.C4](10-5c4-two-schedulers-one-pod.md) that two schedulers cannot double-bind a pod, because the API server refuses the second write. So state precisely what leader election buys a scheduler, given that correctness is already guaranteed. Two answers are defensible and both are about waste rather than safety; a third is about `assume` and is the interesting one.

2. **Artifact 1**: add leader election to the hand-written scheduler using `client-go`'s `leaderelection` package with a `LeaseLock` in `academy-build`, identity from the pod name via the downward API. Add the `leases` permissions to its ClusterRole. Rebuild, push, scale to two:

   ```sh
   kubectl -n academy-build scale deployment toy-scheduler --replicas=2
   kubectl -n academy-build get lease
   ```

3. **Artifact 2**: the framework scheduler needs no code at all — it is three lines of configuration:

   ```yaml
   leaderElection:
     leaderElect: true
     resourceNamespace: academy-build
     resourceName: concentrate-scheduler
   ```

   Update the ConfigMap, restart, scale to two, and check that its ServiceAccount can write leases — this is a permission you will have missed in [exercise 31](31-a-profile-not-a-binary.md) because nothing needed it then.

4. **Watch a handover on each.** Two sessions per artifact:

   ```sh
   while :; do kubectl -n academy-build get lease -o custom-columns=\
   NAME:.metadata.name,HOLDER:.spec.holderIdentity,TRANSITIONS:.spec.leaseTransitions,RENEW:.spec.renewTime; sleep 1; done
   ```

   ```sh
   kubectl -n academy-build delete pod <the holder> --wait=false
   ```

5. **Then the ungraceful version**, which is the one that produces the real number:

   ```sh
   kubectl -n academy-build delete pod <the holder> --grace-period=0 --force
   ```

6. **Measure what the cluster lost during the gap.** With one scheduler dead and the standby not yet leading, submit pods and time how long they stay pending:

   ```sh
   date +%T.%N; kubectl -n sched-lab create deployment gap --image=registry.k8s.io/pause:3.9 --replicas=5 \
     --dry-run=client -o yaml | sed 's/^      containers:/      schedulerName: toy-scheduler\n      containers:/' | kubectl -n sched-lab apply -f -
   kubectl -n sched-lab get pods -l app=gap -o wide -w
   ```

7. Answer the third part of step 1 from evidence: what does the standby hold about the ex-leader's assumed pods when it takes over, and what does it do about it?

**Observe** — `leaseTransitions` before and after each kill, and the pending time from step 6.

**Expect** — a graceful delete to hand over in a second or two and a forced delete to take roughly the lease duration, for the reasons established in [P4](../../phases/04-controllers.md#m4-5). The numbers should match what you measured there; if they do not, the configuration differs and finding out how is worth more than the measurement.

Expect the answer to step 1 to include: two schedulers scoring every pod twice is duplicated work at cluster scale, and the loser's wasted cycle is not free. And expect the `assume` answer to be the sharp one — two schedulers each hold their **own** cache of pods they have decided but not yet seen bound, and those caches disagree, so two schedulers can both believe they placed a pod on a node that only had room for one. **The API server prevents the double bind; it does not prevent the double *decision*, and the double decision is what over-commits nodes.** That is the same failure you produced by hand in [exercise 11](11-what-assume-buys.md), reached from a different direction.

Expect the standby in step 7 to start with an empty cache and rebuild it from the informers, which means it briefly holds no record of pods that were bound moments earlier — the same catch-up you observed in [5.C4](10-5c4-two-schedulers-one-pod.md), and the honest cost of a failover.

**Write down** — the three answers from step 1, the two transition counts, the graceful and forced handover times for both artifacts, and the pending time from step 6.

**Footprint note** — four scheduler pods instead of two on `pair`, briefly. This is the phase's peak in-cluster process count and it is still small. 7.5GB total, 2.0GB margin.

**Teardown — the build half ends here.** Push both build trees to the repository, because everything on `forge` becomes irrelevant in the next exercise and the images in the registry are the only thing that crosses:

```sh
cd ~/src/k8s-academy && git add build/05-scheduler-clientgo build/05-plugin && git commit -m 'P5 build artifacts' && git push
curl -s http://forge.lab:5000/v2/_catalog
```

Confirm both images are listed. Then `kubectl -n sched-lab delete deployment gap`. **The topology goes** — [the next exercise](33-forge-back-down-and-workhorse-up.md) destroys `pair`, resizes `forge` back down and provisions `workhorse`.
