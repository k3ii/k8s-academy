<a id="the-same-kill-a-different-graceful"></a>
# The same kill, and where the framework actually helps

**Claim** — under `SIGKILL` the `kubebuilder` operator behaves **identically** to the hand-wired one, because nothing in `controller-runtime` survives a `SIGKILL` either; the difference appears under `SIGTERM`, and it is a latency improvement, not a correctness one. Port [the `--delta-mode` bug](17-4c1-kill-it-mid-reconcile.md) into artifact 2 and the framework does not save it, which is the sentence this whole phase has been building toward.

**Rests on** — [4.C1 against artifact 1](17-4c1-kill-it-mid-reconcile.md), whose measurements this repeats verbatim, and [artifact 2 running](31-scaffold-the-same-operator.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with artifact 1 scaled to zero.

**Setup** — port both flags across: `--slow-reconcile=<d>` as instrumentation, and `--delta-mode`, which computes the new child count from `new.spec.voices - old.spec.voices` instead of from cluster state. In `controller-runtime` the second one is a little harder to write, because `Reconcile(ctx, req)` hands you a name and nothing else — you have to go out of your way to keep the previous value in memory. **That difficulty is itself a finding**; write down how much work the framework made you do to write the bug, and note that it did not refuse.

**Do**

1. Repeat 4.C1 exactly, against the level version:

   ```sh
   kubectl patch ensemble kill-me --type=merge -p '{"spec":{"voices":7}}'
   pkill -KILL -f 'manager|__debug_bin|operator'      # while a slow reconcile is in flight
   make run
   kubectl get cm -l academy.k3ii.dev/ensemble=kill-me --no-headers | wc -l
   ```

2. Repeat it against `--delta-mode`.

3. Now the part that is not a repeat. Send `SIGTERM` instead, mid-reconcile, and time what happens:

   ```sh
   date +%T.%3N; pkill -TERM -f manager; date +%T.%3N
   ```

   Watch the log lines between the signal and the exit.

4. Find the machinery in source rather than in the release notes:

   ```sh
   cd ~/go/pkg/mod/sigs.k8s.io/controller-runtime*/pkg && \
     grep -rn 'GracefulShutdownTimeout\|SetupSignalHandler\|func (cm \*controllerManager) engageStopProcedure' manager/ | head
   grep -rn 'DefaultTypedControllerRateLimiter\|MaxConcurrentReconciles' controller/ internal/controller/ | head
   ```

5. Do the same `SIGTERM` to artifact 1 and compare the two logs side by side.

**Observe** — the child count and the `Ensemble` status after each restart, and the elapsed time and log content between `SIGTERM` and exit for both artifacts.

**Expect** — steps 1 and 2 reproduce [4.C1](17-4c1-kill-it-mid-reconcile.md) with no difference at all. The level version converges on restart; the delta version stays wrong forever with no error and no event. **A framework does not make a wrong reconcile right**, and if you had met `kubebuilder` first you would probably have believed it did.

Step 3 is the real difference. `controller-runtime` installs a signal handler, cancels the manager's context, and then **waits for in-flight reconciles to return** before exiting, up to `GracefulShutdownTimeout`. Your hand-wired operator most likely exits immediately. So the framework's version finishes the reconcile it was in the middle of, and the restart has nothing to redo.

Name what that bought, precisely: **fewer seconds of stale state after a rolling update.** It did not buy correctness — step 1 proves the restart was already safe. This distinction is worth being able to make quickly, because "the framework handles shutdown for you" is usually said as though it were a correctness claim.

Three more pieces of machinery to name from step 4, each against the hand-written line it replaces:

- **The shared cache on the manager** — one informer per GVK, shared by every controller registered with it. In artifact 1 you built two event sources and would have built a third by hand for a third watch.
- **The default rate limiter** — the same exponential-plus-bucket shape you [predicted the gaps for](07-the-hot-loop-and-the-backoff-that-hides-it.md), wired in by default rather than by you remembering to. This is the one place the framework prevents a real bug you already caused on purpose.
- **`MaxConcurrentReconciles`** — one field where artifact 1 had a worker count and a `Done()` you had to not forget.

**Write down** — the two child counts and statuses from steps 1 and 2, the `SIGTERM` timings for both artifacts, the three pieces of machinery with their `file:line`, and one sentence separating what `controller-runtime` made *safer* from what it made *faster*.

**Footprint note** — no change; this is the same binary under a different signal.

**Teardown** — delete the `kill-me` Ensemble and confirm its ConfigMaps and registry key are gone. Restart `make run`. **The topology stays** — [the diff](33-the-diff.md) needs both trees present and both operators buildable.
