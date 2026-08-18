<a id="why-the-renew-deadline-is-shorter"></a>
# Why the renew deadline is shorter than the lease, and the window it does not close

**Claim** — [the checklist's](../../phases/04-controllers.md#checklist) third falsifiable claim: `RenewDeadline` is shorter than `LeaseDuration` so that a leader **stops acting before anyone else is entitled to start**, and `client-go` refuses a configuration where that is not true. But the ordering is a bound on a window, not the removal of one: freeze a leader for longer than the lease and you can watch two processes both believe they lead, and the thing that actually stops the second write is not the lease at all.

**Rests on** — [the running two-replica operator](28-two-replicas-one-lease.md) with both replicas up, and [the 409 you asserted in `envtest`](16-envtest-is-a-real-apiserver.md), which is the mechanism this exercise ends on.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup**

The victim must be a process you can freeze, so find the leader's PID on the node it runs on:

```sh
kubectl -n academy-build get lease academy-operator -o jsonpath='{.spec.holderIdentity}{"\n"}'
kubectl -n academy-build get pod <holder> -o wide          # which node
ssh zain@10.10.10.131 'sudo crictl ps --name operator -o json | grep -m1 "\"id\""'
ssh zain@10.10.10.131 'sudo crictl inspect <id> | grep -m1 "\"pid\""'
```

`SIGSTOP` freezes the process without telling it anything — no signal handler runs, no context is cancelled, no lease is released. That is the point: it is the closest thing the lab has to a stop-the-world GC pause, a blocked syscall or a node that briefly stops being scheduled, which are the three ways this happens for real.

**Do**

1. Answer from source first, and predict:

   ```sh
   cd ~/src/kubernetes && git grep -n 'renewDeadline\|leaseDuration must be greater\|RetryPeriod must be greater\|func NewLeaderElector' \
     -- staging/src/k8s.io/client-go/tools/leaderelection/leaderelection.go
   ```

   Find the three validation errors `NewLeaderElector` returns. Write down, before running anything, what happens if you set `LeaseDuration: 5s, RenewDeadline: 6s` — an error at construction, an error at acquisition, or a leader that thrashes.

2. Try it. Set exactly that pair, redeploy one replica, and read what it says.

3. Put the durations back, then freeze the leader and watch the standby:

   ```sh
   ssh zain@10.10.10.131 'sudo kill -STOP <pid>'
   date +%T.%3N
   kubectl -n academy-build get lease academy-operator -w
   ```

4. When the standby has taken the lease, and **not before**, wake the old leader and watch both logs at once:

   ```sh
   date +%T.%3N; ssh zain@10.10.10.131 'sudo kill -CONT <pid>'
   kubectl -n academy-build logs -l app=academy-operator --prefix -f --tail=20
   ```

5. Do it again, and this time make the frozen leader have work to lose: `kubectl patch` an Ensemble's `spec.voices` while it is frozen, so both processes have a reason to write the moment it wakes.

**Observe** — the two timestamps, the lease's `holderIdentity` and `leaseTransitions` across the freeze, and the woken process's last few lines before it exits.

**Expect** — step 2 fails at construction with a message naming the two durations. The library does not accept the configuration at all, which is a stronger guarantee than a runtime check and is worth citing exactly.

Step 3: the standby acquires after roughly the lease duration, because a frozen process cannot release anything.

Step 4 is the finding. The woken process has no way to tell that it lost. It resumes wherever it was, and depending on where that was it may run a reconcile — a full one, with writes — before its renewal loop next gets a turn, notices the lease has moved, calls `OnStoppedLeading` and exits. **For that window there were two leaders**, and no amount of duration tuning removes it, because the frozen process's clock was frozen too.

Now the important half: in step 5, that second write mostly does not corrupt anything, and the reason is nothing to do with leader election. The wakened leader is holding a stale object, so its update carries a stale `resourceVersion` and the API server rejects it with a 409 — [the assertion you wrote in `envtest`](16-envtest-is-a-real-apiserver.md). Where it would have created a child, [the deterministic name](22-expectations-or-over-create.md) makes the second create an `AlreadyExists` rather than a duplicate.

**So state the relationship plainly**: leader election reduces how often two writers collide; optimistic concurrency and deterministic naming are what make a collision harmless. A controller that relies on the lease for correctness is a controller with a bug that shows up on a bad afternoon rather than in a test. The ordering `RetryPeriod < RenewDeadline < LeaseDuration` buys you a *rare* window, and the rest of the operator has to survive it.

**Write down** — the construction error with its `file:line`, the two measured timestamps and the gap between waking and exiting, and one sentence naming what stopped the second writer in step 5.

**Footprint note** — no new workload; a frozen process holds its memory and releases nothing, which is the worst case for the arithmetic and is still one small Go binary.

**Teardown** — confirm no process is left stopped: `ssh zain@10.10.10.131 'ps -o pid,stat,cmd -p <pid>'` must not show `T`. Delete the Ensembles you patched. **The topology stays** — [the drill](30-4c3-two-replicas-no-leader-election.md) removes the lease next.
