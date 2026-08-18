# Phase 4 — Controllers & reconciliation

> **4 weeks.** The area with the best on-ramp in the corpus — a complete controller in one commented file — and the phase where the watch machinery you *read* in P2–P3 becomes machinery you *write*.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P3](03-api-machinery.md) — the watch cache you read there is the far end of the informer's watch here, and the `ErrCompacted → 410 → relist` chain (etcd [P2](02-etcd.md), apiserver [P3](03-api-machinery.md)) is exactly what the reflector's `watchHandler` survives. This phase is where that chain stops being a fact and becomes a code path you own. |
| **Unlocks** | [P5](05-scheduler.md) — the scheduler is a controller with an unusually interesting `syncHandler`, and its informers and workqueue are the ones you build here. [P12](12-gitops-platform.md) — Flux's four controllers are the reconcile loop you hand-write, so GitOps *practice* there rests on the *mechanism* here. This also closes the gap [P1](01-operate-shallow.md) opened: Helm had no controller and did not reconcile; a controller does. |
| **Source area** | [Area 4 — Controllers](../strands/source-reading.md#area-4-controllers), entry point `sample-controller/controller.go`. **Read its reflector→DeltaFIFO→indexer→workqueue diagram before any `tools/cache` source** — the other order is the specific failure mode the area warns about (`reflector.go` and `shared_informer.go` are miserable cold, delightful once the pattern is known). |
| **Language** | Go — **two build artifacts**, hand-wired `client-go` then `kubebuilder`, [both gated by `envtest`](../strands/build-mechanics.md#gates) so the comparison is a `git diff`, not an anecdote. |
| **Strands** | [source reading](../strands/source-reading.md#area-4-controllers) · [build](../strands/build-mechanics.md#gates) · [talks](../strands/talks.md#controllers) |

---

## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Draw reflector → DeltaFIFO → indexer → workqueue** and name the file implementing each stage — derived from `sample-controller` *before* opening `tools/cache`, which is the correct reading order.
2. **State why a handler enqueues a *key*, not the object**, and why the worker re-reads from the lister rather than trusting the event payload — citing `sample-controller/controller.go` and `controllers.md`. This is level-triggered reconciliation, not a style choice.
3. **Show the reflector surviving a `410 Gone`** with a relist, citing `reflector.go`'s `watchHandler` — the client end of [P2](02-etcd.md)'s `ErrCompacted` and [P3](03-api-machinery.md)'s watch-cache ring buffer.
4. **Hand-wire a `client-go` operator** — informer, lister, rate-limiting workqueue, CRD, finalizer, status subresource, all by hand — that passes `envtest`.
5. **Explain the `ControllerExpectations` mechanism** and why a diff-driven controller over-creates without it, citing `controller_utils.go` and `replica_set.go`.
6. **Diagnose a namespace wedged in `Terminating`** to the specific finalizer, and name what `Foreground`/`Background`/`Orphan` propagation each do — citing the GC graph and the namespace controller.
7. **Run two replicas with and without leader election** and show the `LeaseLock` renew-deadline-vs-lease-duration behaviour, citing `leaderelection.go`.
8. **Produce a `git diff` of the `kubebuilder` scaffold against your hand-wired operator**, naming what `controller-gen`, `zz_generated.deepcopy.go` and `envtest` produced that you had written by hand.

---

## 2. Modules

Reading is [Area 4](../strands/source-reading.md#area-4-controllers), and the sequencing rule is load-bearing: **the picture and `sample-controller` first, `tools/cache` in earnest only after.** Each cited item carries a question to answer — no bare links.

### Module 4.1 — The reconcile principle, and the picture first (~4 days)

Before any `client-go` source, install the one idea everything else serves.

**Read**

| Item | Answer from it |
|---|---|
| `controllers.md` (item 1, **read first, always**) | Why do you re-read from the cache instead of trusting the event, and what makes a reconcile safe to run twice? State the idempotency rule in one sentence. |
| `sample-controller` README + the `client-go-controller-interaction` diagram (item 2) | The reflector→DeltaFIFO→indexer→workqueue picture with prose. Ten minutes that saves ten hours — draw it from memory afterwards. |
| `sample-controller/controller.go` (item 3, ⭐) | The Rosetta Stone: one file with informer setup, key-enqueuing handlers, the worker loop, `syncHandler`, owner refs and status update. Which line enqueues a *key* rather than the object, and why? |

**Do** — run `sample-controller` against the [`pair`](https://github.com/k3ii/k8s-academy/issues/8) cluster, watch it reconcile its CRD, and add a log line at each of the five moving parts named in the diagram.

**Break it** — chaos drill [4.C1](#3-chaos-drills) in miniature: `kubectl edit` the managed object's status to a wrong value and watch the controller stomp it back on the next resync. That stomp is level-triggered reconciliation, and it is the same one you saw in [P1](01-operate-shallow.md) — now you can point at the loop that does it.

**Write down** — the reflector→DeltaFIFO→indexer→workqueue diagram, drawn from memory, with the file per stage.

### Module 4.2 — The machinery, in reading order (~1 week)

Now `tools/cache`, in the order the area prescribes — small and elegant first, the 55 KB files last and only in part.

**Read**

| Item | Answer from it |
|---|---|
| `util/workqueue/queue.go` (item 4) | The best *first* piece of `client-go` source. How do the dirty and processing sets give you de-duplication and single-worker-per-key at once? |
| `util/workqueue/{delaying,rate_limiting}_queue.go` (item 5) | `AddAfter` and exponential per-item backoff. What symptom does a *broken* controller show when its rate limiter is wrong — and how would you recognise the hot loop? |
| `tools/cache/delta_fifo.go` (item 7) | **The conceptual crux.** Why does the queue hold *deltas per key*, and what does `Replace` do on a re-list that a plain FIFO could not? |
| `tools/cache/reflector.go` — `ListAndWatch`, `watchHandler` only (item 8) | The file that connects controllers back to API machinery. Where is `ErrResourceExpired`/`410` handled, and what does the reflector do next? **This is objective 3.** |
| `tools/cache/shared_informer.go` — `Run`, `HandleDeltas` (item 9) | One watch shared by many handlers. What does `HasSynced` promise, and why must a controller wait for it before its first reconcile? |

**Do** — instrument a running informer: log every delta type (`Added`/`Updated`/`Deleted`/`Sync`) and force a relist by restarting the apiserver (the [P3](03-api-machinery.md) `3.C4` move) — watch `Replace` fire and the `Sync` deltas arrive.

**Break it** — reproduce the `410`: overflow the [P3](03-api-machinery.md) watch-cache window under your informer and catch `watchHandler` relisting. The chain you traced across two phases now runs through your own log lines.

**Write down** — the `410`-to-relist path with its `reflector.go` citation, tied explicitly back to P2's `ErrCompacted`.

### Module 4.3 — Build artifact 1: the hand-wired operator (~1 week)

The phase's centre. Everything above becomes something you wire yourself, modelled on `sample-controller`.

**Do** — build a `client-go` operator with **every part by hand**: a CRD (and its generated clientset/listers/informers — read `code-generator` item 23 to make `pkg/generated/` legible), a shared informer, a lister, a rate-limiting workqueue, key-enqueuing handlers, a `syncHandler` that reconciles desired-vs-actual, a **finalizer** for cleanup, and a **status subresource** with conditions.

**Gate** — [`envtest`](../strands/build-mechanics.md#gates): a real `kube-apiserver` and `etcd` out-of-cluster, so the reconciler meets genuine optimistic concurrency, watch delivery, defaulting and validation — not a fake client that agrees with whatever you wrote. **This is the objective gate a hand-wired controller otherwise lacks**, and the reason module 4.6's diff is a comparison rather than a story.

**Break it** — chaos drill [4.C1](#3-chaos-drills) for real: kill the operator mid-`syncHandler` and confirm it converges on restart with no lost work. If it loses work, the bug is that you trusted the event or did not requeue on error — fix it, because this *is* the capstone.

**Write down** — the five hand-wired parts mapped to their `sample-controller` equivalents, and the one line in your worker loop that requeues a key on error (the no-lost-work guarantee).

### Module 4.4 — Exemplars, owner refs, GC and finalizers (~1 week)

The in-tree controllers, read for the patterns your operator glossed — and the source behind the two nastiest real-world failures.

**Read**

| Item | Answer from it |
|---|---|
| `pkg/controller/replicaset/replica_set.go` (item 11) | **The most readable exemplar in-tree.** How does `manageReplicas` compute actual-vs-desired, and where does adopt/orphan happen via owner refs? |
| `controller_utils.go` — `Expectations` types only (item 12) | The mechanism that stops a controller over-creating while its cache is stale. **Why would a naive diff-driven controller create too many pods without it?** (This is objective 5, and a bug your hand-wired operator may have.) |
| `controller-ref.md` + `garbage-collection.md` (items 18–19) | Adoption/orphaning, and why exactly one owner may have `controller: true`. `Orphan`/`Background`/`Foreground` propagation — what does each do to children? |
| `garbagecollector/graph.go` + `namespace/` + KEP-5080 (items 20–21) | The owner-reference graph, and **the `kubernetes` finalizer** — the single most-encountered finalizer problem. What makes a namespace stick in `Terminating`? |

**Do** — create an owner-reference chain (a CRD owning ConfigMaps), delete with each propagation policy, and watch children orphan, background-delete, or foreground-delete.

**Break it** — chaos drill [4.C2](#3-chaos-drills): add a finalizer to your CRD, then make its cleanup fail, and wedge the object (and a namespace) in `Terminating`. Diagnose it from the object's `metadata.finalizers` and the GC controller's behaviour, then clear it correctly — not by force-removing the finalizer, but by fixing the cleanup.

**Write down** — the `Terminating` diagnosis: which finalizer, why it blocked, and the propagation policy that produced the child behaviour you saw.

### Module 4.5 — Leader election (~3 days)

Self-contained, well-commented, and directly demonstrable — the answer to "what happens when you run two replicas".

**Read**

| Item | Answer from it |
|---|---|
| `tools/leaderelection/leaderelection.go` (item 16) | `LeaseLock`, the renew deadline versus the lease duration, and the `OnStoppedLeading` contract. What must a controller do the instant it loses the lease, and why is the renew deadline shorter than the lease? |
| KEP-4355 Coordinated Leader Election (item 17) | `LeaseCandidate` and skew-aware leader selection — the modern extension. When does uncoordinated election pick the wrong leader during an upgrade? |

**Do** — add leader election to your hand-wired operator and run two replicas; watch one lead, kill it, watch the standby acquire the lease after the renew deadline lapses.

**Break it** — chaos drill [4.C3](#3-chaos-drills): run the two replicas **without** leader election and watch them fight — double-creating, stomping each other's status. Then add it back. The fight is the argument for the lease.

**Write down** — the observed failover timing (lease duration, renew deadline, actual takeover gap) with the `leaderelection.go` citation.

### Module 4.6 — Build artifact 2: kubebuilder, and the diff (~4 days)

The scaffold, met *after* the hand-wiring, so `controller-gen`, `Reconcile(ctx, req)`, `envtest` and `zz_generated.deepcopy.go` land as **recognition, not magic** ([#9](https://github.com/k3ii/k8s-academy/issues/9) — order fixed, do not swap).

**Do** — rebuild the *same* operator with `kubebuilder`: `make manifests`, the `Reconcile` method, the generated deepcopy. Gate it with the same [`envtest`](../strands/build-mechanics.md#gates) as artifact 1 — identical harness, which is what makes the comparison honest.

**Break it** — feed the `kubebuilder` operator the *same* mid-reconcile kill from 4.C1. It should survive identically — and if it survives more gracefully, name the `controller-runtime` machinery (the manager, the shared cache, the default rate limiter) that bought that.

**Write down** — **the capstone diff**: `kubebuilder`'s scaffold against your hand-wired code, every generated file mapped to the hand-written part it replaces, with what each one does that you did by hand.

---

## 3. Chaos drills

**Hand-driven, every one** — [Chaos Mesh is not introduced until P6](06-kubelet-node.md), deliberately after several phases of manual failure so the tool reads as a scripted wrapper over primitives already met. These drills are all *convergence under interruption* — the level-triggered guarantee tested, not asserted.

| # | Drill | By hand | What you must produce afterwards |
|---|---|---|---|
| 4.C1 | **Kill the controller mid-reconcile** | SIGKILL the operator during `syncHandler` | That it converges on restart with **no lost work**, and the line that requeues on error — the capstone's core |
| 4.C2 | **A finalizer that never completes** | make a CRD's finalizer cleanup fail | The specific finalizer wedging the object/namespace in `Terminating`, and the *correct* clearance (fix cleanup, not force-remove) |
| 4.C3 | **Two replicas, no leader election** | run two operator pods without a lease | The concrete symptom of the fight (double-create, status stomp), then the lease that ends it |
| 4.C4 | **A stale informer cache** | act on the cache immediately after a change, before `HasSynced` | Why acting before sync is wrong, and how re-read-from-cache-plus-resync recovers — the reason objective 2 exists |

4.C1 is the capstone's restart test; 4.C3 is module 4.5's payoff.

---

## 4. Talks

Full entries with runtimes under [Controllers](../strands/talks.md#controllers).

- **The Life of a Kubernetes Watch Event** (Zhang & Cai) — **the most load-bearing talk in the corpus**, and doubly so now: it follows one change from the etcd watch through the apiserver cache, the reflector, DeltaFIFO, indexer and workqueue — *the exact pipeline you build this phase*. Watch it first; it is modules 4.1–4.2 in one sitting.
- **client-go: The Good, The Bad and The Ugly** (Cosic) — the honest tour of the moving parts and their sharp edges, aimed precisely at someone wiring a reconcile loop *by hand*. The edges in this talk are the ones you will hit in module 4.3.
- **Don't Write Controllers Like Charlie Don't Does** (Young) — the current catalogue of controller bugs: status-vs-spec confusion, non-idempotent reconciles, hot loops, requeue misuse. Watch it *after* 4.3, as a review of the operator you just wrote.

---

## 5. Ecosystem

**Flux** — the reconcile loop you just hand-wrote, running in production ([#6](https://github.com/k3ii/k8s-academy/issues/6) settled Flux over Argo).

- **Hands-on:** read Flux's controller source **immediately after building your own operator** — the single best available reality-check on what you wrote. Its four controllers (**source, kustomize, helm, notification**) are the same informer→workqueue→reconcile shape, with real reconcile intervals and real drift correction.
- **Internals note:** Flux **closes the gap [P1](01-operate-shallow.md) opened.** There, `helm upgrade` did *not* reconcile — delete a resource it made and it stayed gone. Flux's helm-controller *does* reconcile: it re-reads desired state (a git commit) against actual and corrects drift, on an interval, forever. That difference — a controller versus a client-side templater — is the whole GitOps argument, and now you can point at the loop that makes it true.
- **Maturity:** CNCF **graduated**. **GitOps splits across two phases by design:** its *mechanism* is here ("how does a controller make the cluster match a git commit"); its *practice* is [P12](12-gitops-platform.md) ("how do you run a delivery model on that").

---

## 6. Capstone

**The hand-wired operator managing a CRD end to end, surviving a restart mid-reconcile with no lost work — plus a written `git diff` of what `kubebuilder` scaffolded against what you wrote by hand.**

Two artifacts, checked together:

1. **The operator** (module 4.3): a CRD reconciled through a hand-wired informer/lister/workqueue, with a finalizer and a status subresource, passing `envtest`. The **no-lost-work proof** is the point: SIGKILL it mid-`syncHandler` (drill 4.C1) and it converges on restart, because reconcile is level-triggered and re-reads from cache — not because it buffered the event. Demonstrate this, do not assert it.
2. **The diff** (module 4.6): the `kubebuilder` version of the same operator, with a written mapping of every generated artifact to its hand-written equivalent.

**Cite `file:line` a hostile reader could check** — at minimum:
- the key-enqueue-not-object line in your controller, against its `sample-controller/controller.go` model;
- the requeue-on-error line that makes restart lossless;
- the `ErrResourceExpired`/`410` handling in `tools/cache/reflector.go` that your informer relies on;
- the `Expectations` types in `controller_utils.go` if your operator needed them to avoid over-creating.

Every path verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills) — the two 55 KB `tools/cache` files are exactly where a copied line number rots.

---

## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster / `envtest`:**
- [ ] The hand-wired operator reconciles a CRD, with finalizer and status subresource, passing `envtest`.
- [ ] SIGKILL it mid-reconcile; it converges on restart with no lost work.
- [ ] Two replicas fight without leader election, then cooperate with it — timed failover shown.

**Build artifacts:**
- [ ] Artifact 1: the hand-wired `client-go` operator (`envtest`-gated).
- [ ] Artifact 2: the `kubebuilder` operator, same job, same `envtest`.
- [ ] The `git diff` mapping every scaffolded file to its hand-written equivalent.

**Written artifacts (each is a module's Write-down):**
- [ ] The reflector→DeltaFIFO→indexer→workqueue diagram from memory, file per stage (4.1).
- [ ] The `410`-to-relist path citing `reflector.go`, tied to P2's `ErrCompacted` (4.2).
- [ ] The five hand-wired parts mapped to `sample-controller`, and the requeue line (4.3).
- [ ] The `Terminating` diagnosis — finalizer, cause, propagation policy (4.4).
- [ ] The observed leader-election failover timing citing `leaderelection.go` (4.5).
- [ ] The capstone diff (4.6).

**Falsifiable claims — write, then verify against source:**
- [ ] Why a handler enqueues a key, not the object.
- [ ] Why a diff-driven controller over-creates without `Expectations`.
- [ ] Why the renew deadline is shorter than the lease duration.

---

## 8. Gate

You may advance to [P5](05-scheduler.md) when:

1. **The hand-wired operator survives a mid-reconcile kill with no lost work**, and you can point at the requeue line and say why level-triggered reconciliation makes the restart safe. If it loses work, the reconcile is trusting the event — **stay here**, because [P5](05-scheduler.md)'s scheduler is this same loop with a harder `syncHandler`.
2. **The `kubebuilder` diff is done and every generated file has a named hand-written equivalent.** The scaffold must read as recognition — if any of it is still magic, the hand-wiring did not land.
3. **The `410`-to-relist chain is reflexive across all three layers** — etcd `ErrCompacted` ([P2](02-etcd.md)), apiserver watch-cache ([P3](03-api-machinery.md)), and your own reflector relisting. This is the third time you have met it; from here it is assumed, never re-taught.

The reconcile loop is the pattern the rest of the control plane is built from. When [P5](05-scheduler.md) opens the scheduler, its informers, its workqueue, and its "re-read, don't trust the event" discipline are all machinery you have now written by hand and watched survive being killed.
