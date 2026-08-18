<a id="the-capstone-writeup"></a>
# The capstone: two operators, one proof, four citations

**Artifact** — [the capstone](../../phases/04-controllers.md#capstone) as the phase specifies it: the hand-wired operator managing a CRD end to end, **demonstrated** surviving a mid-reconcile kill with no lost work, plus [the written diff](33-the-diff.md), plus four `file:line` citations a hostile reader could check — each one verified live, not copied.

**Rests on** — everything in this directory. Nothing new is built here; this is the assembly, and it should take an afternoon.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), for the last time.

**Do**

1. **Restore artifact 1 as the running operator.** Scale artifact 2 to zero, artifact 1 back to one replica with `--leader-elect=true`. The capstone is artifact 1's; artifact 2 is evidence about it.

2. **Record the no-lost-work proof as a transcript, not a claim.** One terminal, one continuous session, in this order:

   ```sh
   date +%T.%3N
   kubectl get ensemble capstone -o jsonpath='{.spec.voices} {.status.readyVoices}{"\n"}'
   kubectl get cm -l academy.k3ii.dev/ensemble=capstone --no-headers | wc -l
   kubectl patch ensemble capstone --type=merge -p '{"spec":{"voices":8}}'
   # …kill it mid-reconcile, per 4.C1…
   kubectl get cm -l academy.k3ii.dev/ensemble=capstone --no-headers | wc -l   # mid-flight: fewer than 8
   kubectl -n academy-build scale deploy academy-operator --replicas=1
   kubectl get cm -l academy.k3ii.dev/ensemble=capstone --no-headers | wc -l   # after: 8
   kubectl get ensemble capstone -o jsonpath='{.status}{"\n"}'
   date +%T.%3N
   ```

   The mid-flight count is the load-bearing line. Without it the transcript proves the operator can make eight ConfigMaps, which nobody doubted. **With it, the transcript proves work was interrupted and completed anyway**, and that is the entire capstone.

3. **Verify the four citations live**, per [P2's archaeology standard](../../strands/source-archaeology.md#drills). For each: open the file at the recorded line, confirm the code is what you claimed, and record the commit sha alongside it.

   - The **key-enqueue-not-object** line in your controller, against [its `sample-controller` model](02-the-line-that-enqueues-a-key.md).
   - The **requeue-on-error** line that makes the restart lossless — the one that step 2's transcript is evidence for.
   - The **`ErrResourceExpired`/410 handling** in `tools/cache/reflector.go` that your informer relies on, from [the 410 exercise](10-the-410-under-your-own-informer.md).
   - The **`Expectations` types** in `controller_utils.go`, if your operator needed them — and if it did not, one sentence on [why deterministic names made them unnecessary](22-expectations-or-over-create.md), which is a better answer than a citation.

   `tools/cache` is two 55 KB files. A line number copied from three weeks ago has probably rotted; re-derive each one with `git grep -n` and record the sha.

4. **Assemble the write-up** from the six module artifacts you already have — [the corrected diagram](13-the-same-drawing-corrected.md), the 410 chain, the five hand-wired parts, [the `Terminating` diagnosis](26-a-namespace-stuck-in-terminating.md), [the failover timing](28-two-replicas-one-lease.md), [the diff](33-the-diff.md) — and the three falsifiable claims. They were each written when they were fresh; the job here is checking they still agree with each other, not rewriting them.

5. **Take the gate honestly.** [Its three conditions](../../phases/04-controllers.md#gate) are answerable yes or no. In particular, condition 3 asks whether the 410-to-relist chain is reflexive across etcd, the watch cache and your reflector. You have now met it three times. Say it out loud without looking; if you cannot, the fix is [exercise 10](10-the-410-under-your-own-informer.md) again, not more reading.

**Expect** — the transcript in step 2 shows a count that is neither 3 nor 8 at the moment of the kill, and 8 afterwards, with no manual intervention between them. If your mid-flight count is always 8, the reconcile is too fast to catch: raise `--slow-reconcile` rather than settling for a weaker proof.

At least one of the four citations will have moved. That is the expected outcome of step 3 and it is why the step exists.

**Write down** — the transcript, the four citations with shas, the assembled write-up, and one paragraph you will actually want in [P5](../../phases/05-scheduler.md): what the scheduler is going to have that your operator did not, given that it is this same loop with a harder `syncHandler`.

**Footprint note** — nothing new; this is the same cluster running one operator.

**Teardown** — the phase ends here. Push both build trees and the write-up first, because the cluster goes and the code does not live on it:

```sh
cd ~/k8s-academy && git add build/04-operator-clientgo build/04-operator-kubebuilder && git commit && git push
just tofu labs destroy
```

**The topology goes.** [P5](../../phases/05-scheduler.md) opens with several days of reading before it needs a cluster at all, so leaving `pair` up would be 5.0GB spent on nothing. Re-provisioning is [one command](../../strands/lab-topologies.md#provision) and takes minutes; the probes in `~/probes/` are on `forge`, which stays.
