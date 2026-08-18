<a id="4c1-kill-it-mid-reconcile"></a>
# 4.C1 — SIGKILL mid-`syncHandler`, twice, with one flag changed

**Claim** — the level-triggered operator converges after being killed at the worst possible moment, and the same operator with one changed line does not, permanently and silently. Killing it once proves nothing; **killing both versions is the proof**, because only the second run shows what the guarantee is made of.

**Rests on** — [the hand-wired loop](15-the-hand-wired-loop.md) and [its gate](16-envtest-is-a-real-apiserver.md). This drill is [the capstone's](../../phases/04-controllers.md#capstone) restart test and the reason the operator is the phase's centre.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the operator running on [`forge`](../../strands/lab-topologies.md#build-guest) as `go run`.

**Setup — two flags, added before the drill and kept afterwards.**

- `--slow-reconcile=<d>`: sleep `d` between creating one child and the next. This widens the kill window from microseconds to something a human can hit. It is instrumentation, not a bug.
- `--delta-mode`: in the `Ensemble` update handler, compute `new.spec.voices - old.spec.voices` and create exactly that many children, instead of reading `spec.voices` and reconciling to it. **This is the bug, expressed as the four-line version a reasonable person writes on a Tuesday**, and it is the whole content of the drill.

The escape hatch is the operator itself: with `--delta-mode` off, restarting it repairs any state either run leaves behind. Confirm that before you break anything.

**Do**

1. **Level-triggered run.** Start with `--slow-reconcile=3s`, scale up, and kill it in the middle:

   ```sh
   go run ./cmd/operator --kubeconfig=$HOME/.kube/config --slow-reconcile=3s -v=2 &
   OP=$!
   kubectl -n academy-lab patch ensemble alpha --type=merge -p '{"spec":{"voices":8}}'
   sleep 4 && kill -9 $OP
   kubectl -n academy-lab get configmaps      # partial: some children, not all
   ```

2. Restart it, unchanged, and wait:

   ```sh
   go run ./cmd/operator --kubeconfig=$HOME/.kube/config -v=2 &
   sleep 5 && kubectl -n academy-lab get configmaps | wc -l
   ```

3. **Delta-mode run.** Reset to three voices, restart with the flag, and kill it at the same moment:

   ```sh
   kubectl -n academy-lab patch ensemble alpha --type=merge -p '{"spec":{"voices":3}}'
   # wait for it to settle, then restart with --delta-mode --slow-reconcile=3s
   kubectl -n academy-lab patch ensemble alpha --type=merge -p '{"spec":{"voices":8}}'
   sleep 4 && kill -9 <pid>
   ```

4. Restart it in delta mode and wait as long as you like.

**Observe** — the child count after each restart, and `status.readyVoices` against `spec.voices`.

**Expect** — run 1 converges to eight within a reconcile of restart. Nothing was replayed: the informer's initial list produced an `Ensemble` whose spec said eight and whose world had five, and the same arithmetic that ran the first time ran again.

Run 2 stops at five and stays there. There is **no error, no event, no condition and no retry** — the operator is healthy, its queue is empty, and it is waiting for an update that already happened. The only way back is another write to the object, which in production means a human noticing. That is what "lost work" means and it is the failure the gate exists to keep out of [P5](../../phases/05-scheduler.md).

The line that separates them is one you can point at: the reconcile's input is either `spec.voices` — a fact that survives a restart because it is in etcd — or `new − old`, a fact that exists only in the delivery. **Every guarantee in this phase reduces to keeping the reconcile's inputs on the server side of the process boundary.**

**Write down** — the two child counts, the timing of convergence in run 1, and the citation [the capstone](../../phases/04-controllers.md#capstone) requires: the requeue-on-error line in your worker loop and one sentence on why level-triggered reconciliation makes the restart safe *without* it needing to be durable.

**Footprint note** — nothing new. `--slow-reconcile` makes reconciles longer, not larger.

**Teardown** — remove `--delta-mode` from the command line, restart the operator, confirm eight children, then set `spec.voices` back to 3. **Keep both flags in the code** — [exercise 32](32-the-same-kill-a-different-graceful.md) runs this same drill against the `kubebuilder` operator and the comparison needs the identical window. **The topology stays.**
