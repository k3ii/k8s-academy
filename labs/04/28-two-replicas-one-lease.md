<a id="two-replicas-one-lease"></a>
# Two replicas, one Lease, and a failover you can time

**Artifact** — [objective 7's](../../phases/04-controllers.md#objectives) measurement: the operator running two replicas with `LeaseLock` leader election, a `Lease` object you can watch change hands, and a timed failover with the three configured durations beside the observed gap.

**Rests on** — [the in-cluster deployment](19-stage-2-and-the-role-you-write-yourself.md), which is where two replicas is a one-word change, and [module 4.5's](../../phases/04-controllers.md#m4-5) `leaderelection.go` reading question.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Both replicas run in `academy-build` on the worker node.

**Build** — wrap the controller's `Run` in `leaderelection.RunOrDie`, with a `resourcelock.LeaseLock` in `academy-build` named `academy-operator`, an identity that is the pod name (from the downward API, [per the strand's identity convention](../../strands/build-mechanics.md#identity)), and the three durations left at their defaults for the first run. Three rules the callbacks impose:

- **`OnStartedLeading` receives a context.** Every worker must stop when it is cancelled. A goroutine that ignores it is a controller that keeps reconciling after it has lost the lease, which is the two-leader state this whole mechanism exists to prevent.
- **`OnStoppedLeading` must not try to clean up gracefully.** By the time it runs, another process may already be leading. The correct body is a log line and an exit.
- **`ReleaseOnCancel: true`**, so a clean shutdown hands the lease back instead of making the standby wait out the full duration. This is the difference between a two-second and a fifteen-second failover on a rolling update, and it is one field.

Add the RBAC the lock needs: `get`, `update` and `create` on `leases` in `coordination.k8s.io`, in that namespace. It will fail loudly if you forget, which after [exercise 19](19-stage-2-and-the-role-you-write-yourself.md) you can read at a glance.

**Do**

1. Answer from source, before running:

   ```sh
   cd ~/src/kubernetes && git grep -n 'RenewDeadline\|LeaseDuration\|RetryPeriod\|func (le \*LeaderElector) renew\|tryAcquireOrRenew' \
     -- staging/src/k8s.io/client-go/tools/leaderelection/leaderelection.go
   ```

   Write down the defaults for the three durations, and **what a candidate checks before it decides an existing lease has expired** — the answer involves its own observation time, not the holder's clock, and that detail is [the next exercise](29-why-the-renew-deadline-is-shorter.md).

2. Scale to two and watch the lock:

   ```sh
   kubectl -n academy-build scale deploy academy-operator --replicas=2
   kubectl -n academy-build get lease academy-operator -o yaml
   kubectl -n academy-build logs -l app=academy-operator --prefix --tail=5
   ```

3. Time a failover. Note the wall clock, delete the holder, and watch for the successor's first reconcile:

   ```sh
   kubectl -n academy-build get lease academy-operator -o jsonpath='{.spec.holderIdentity}{"\n"}'
   date +%T.%3N; kubectl -n academy-build delete pod <holder> --grace-period=0 --force
   kubectl -n academy-build get lease academy-operator -w
   ```

4. Do it again with a graceful delete (no `--force`) and compare.

**Observe** — `holderIdentity`, `renewTime` ticking, `leaseTransitions` incrementing, and the gap between the delete and the successor's first log line.

**Expect** — exactly one replica logs reconciles; the other logs nothing but its attempt to acquire. The forced delete gives a gap close to the lease duration, because nobody released anything and the standby must wait for the lease to look stale. The graceful delete gives a gap of a second or two, because `ReleaseOnCancel` cleared the holder.

**`leaseTransitions` is the field to keep an eye on in production.** It counts hand-overs, and a cluster where it climbs steadily has controllers losing their leases without dying — usually because the API server is slow enough that renewals miss their deadline. That is a symptom with a completely different cause from the thing it looks like, which is a crashing controller.

Then read KEP-4355 and answer its question: with two candidates of different versions during an upgrade, uncoordinated election picks whichever one wins the race, and `LeaseCandidate` exists so the *cluster* can pick instead. Say in one sentence which upgrade goes wrong without it.

**Write down** — [the checklist's](../../phases/04-controllers.md#checklist) 4.5 artifact: the three configured durations, both measured gaps, and the `leaderelection.go` citation for the renewal loop.

**Footprint note** — a second replica of a small Go binary on `pair`'s worker, sized [by the same rule as the first](../../strands/build-mechanics.md#sizing). This is the phase's largest single addition and it is under 100 MiB.

**Teardown** — leave two replicas running; [the next exercise](29-why-the-renew-deadline-is-shorter.md) needs both. **The topology stays.**
