# Phase 1 — Operate a cluster (deliberately shallow) + CKAD

> **2–3 weeks**, plus a **1–2 week CKAD drill block** at the end, plus a **few-day Go primer** as the closing module.
> The range is planning information. **The gate at the bottom of this file decides when the phase is finished** — not the calendar, and *not* the exam.

| | |
|---|---|
| **Prerequisites** | [P0](00-linux-primitives.md) — a Pod is namespaces + cgroups + a root filesystem, and you built that by hand, so "container" is already mechanism rather than magic. `securityContext.capabilities` here is the P0 capability drop, wearing a manifest. |
| **Unlocks** | Everything downward. This phase exists to build **referents**: when [P2](02-etcd.md) says "the watch cache serves this read" and [P3](03-api-machinery.md) says "admission mutated it before storage," *this* is the object, the rollout, the `kubectl get -w` you will already have seen. The kubeadm cluster you stand up by hand is also the exact artifact [P3](03-api-machinery.md) reads back — you will grep the PKI and static-pod manifests you generate here. |
| **Source area** | [Area 0 — Foundational](../strands/source-reading.md#area-0-foundational), the **operational half** (items 7–12) that [P0](00-linux-primitives.md) deferred to here: `api-conventions.md`'s named sections, `feature-gates.md`, `staging.md`, and `local-up-cluster.sh` as the honest inventory of what a control plane *is*. |
| **Language** | Go ([#9](https://github.com/k3ii/k8s-academy/issues/9)). The **Go primer is module 1.6**, at the very end — days, not weeks — because [P2](02-etcd.md) is the first phase that opens Go source in anger and must not be blocked on the language. |
| **Strands** | [certs](../strands/certs.md#ckad) · [talks](../strands/talks.md#debugging) · [chaos](../strands/chaos.md#principle) · [source reading](../strands/source-reading.md#area-0-foundational) |

---

<a id="objectives"></a>
## 1. Objectives

Mechanism-level where it can be, operational where the phase is deliberately shallow. Each is phrased so failing it is detectable — *understand* appears nowhere.

**This phase is held short on purpose.** Its job is fluency and referents, not internals. Resist every urge to descend — that is what the next nine phases are for. By the end you can:

1. **Stand up a working cluster with `kubeadm` by hand**, and afterwards *point at what it generated*: the static-pod manifests in `/etc/kubernetes/manifests`, the PKI under `/etc/kubernetes/pki`, the kubeconfigs, and the `kubelet` that bootstraps the rest. Naming these is the deliverable [P3](03-api-machinery.md) depends on.
2. **State any object's GVK, which fields are `spec` versus `status`, and who writes each** — and say what a changed `resourceVersion` does and does not promise, from the named sections of `api-conventions.md`.
3. **Perform a rolling update and a rollback**, and narrate the Deployment → ReplicaSet → Pod chain at each step by naming the object that changed — not by watching it happen, by predicting it.
4. **Trip a readiness probe and show traffic drain** from the Service's EndpointSlice, then restore it — the level-triggered reconciliation from [P0's `controllers.md` reading](00-linux-primitives.md) made visible in one `kubectl get endpointslices -w`.
5. **Expose one app four ways** — ClusterIP, NodePort, LoadBalancer (via MetalLB), and Ingress — and say which OSI layer and which component each relies on.
6. **Author a nontrivial Helm chart** (values, templates, a subchart dependency), and state **where Helm stores release state and what `helm upgrade` actually diffs**.
7. **Write a small Go program** exercising the primer's constructs — a goroutine feeding a channel, an interface with two implementations, wrapped errors, one table test — because that is the floor for reading `k/k` in [P2](02-etcd.md).
8. **Read a manifest field back to its P0 mechanism**: given `resources.limits.memory`, `securityContext.capabilities.drop`, or `emptyDir`, name the cgroup, capability set, or mount you manipulated by hand in P0.

---

<a id="modules"></a>
## 2. Modules

The reading (Area 0 items 7–12) is interleaved into the modules that give it something to point at — the whole reason P0 deferred it here. There is **no build-track artifact** this phase; the Go primer that would normally underpin one is instead the closing module, deliberately after everything that does not need it.

<a id="m1-1"></a>
### Module 1.1 — Stand up a control plane by hand, with kubeadm (~4 days)

The tool CKA expects, stood up deliberately so that P3 can *read what it left behind*. Do not use a one-command distro here — the point is the parts.

**Read** — [Area 0](../strands/source-reading.md#area-0-foundational) items 11–12, with a question to answer from each:

| Read | Answer from it |
|---|---|
| `staging.md` (item 11) | Why does `staging/src/k8s.io/*` exist, and how does `client-go` get published from inside the monorepo? Two pages that stop months of repo-layout confusion. |
| `local-up-cluster.sh` (item 12) | Not prose — the most honest inventory of what a control plane *is*. **List the flags it passes to each of `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`.** You will meet a third of them again in P3. |

The control plane it leaves behind runs as **static pods** — the kubelet watches a *directory*, not the API — which is a [P0](00-linux-primitives.md) mechanism rather than a new one, and the most clarifying single fact about how Kubernetes runs itself. The map of what it generated is a required input to [P3](03-api-machinery.md), which reads these files as *source*.

**Labs** — [A two-node cluster, stood up by hand](../labs/01/01-provision-and-kubeadm-init.md) · [The map of what kubeadm left on disk](../labs/01/02-what-kubeadm-generated.md) · [Two control planes, one flag list](../labs/01/03-static-pod-flags-vs-local-up.md) · [1.C4 — move the apiserver's manifest out of the directory](../labs/01/04-static-pod-blip.md)

<a id="m1-2"></a>
### Module 1.2 — The object model, as referents (~3 days)

Shallow by design: name the parts, do not open the machinery. Every term here is a hook P2–P4 will hang mechanism on.

**Read** — [Area 0](../strands/source-reading.md#area-0-foundational) item 8, `api-conventions.md`, **named sections only** (it is 115 KB — never linear): *Types (Kinds)*, *Spec and Status*, *Typical status properties / Conditions*, *Resource Version*, *Lists*.

> **Question to answer from the source:** the conventions say `resourceVersion` is *opaque* and must not be interpreted by clients. What are you allowed to do with it, and what does the doc explicitly forbid? You will see *why* in [P2](02-etcd.md), where it turns out to be an etcd revision.

Hand-editing a `status` and watching a controller stomp it back is the reconcile loop made visible, and it is objective 8 from [P0](00-linux-primitives.md) arriving as an object rather than as a shell script: re-read desired state, correct drift, forget nothing because you remembered nothing.

**Labs** — [Who writes each half of an object](../labs/01/05-spec-status-ownership.md) · [What `resourceVersion` does and does not promise](../labs/01/06-resourceversion-moves.md) · [Write a lie into status and time the correction](../labs/01/07-stomp-the-status.md)

<a id="m1-3"></a>
### Module 1.3 — Workloads: the controllers you will later read, operated (~4 days)

CKAD's centre of gravity, and a gallery of the controllers P4 dissects. Here you *drive* them; there you read them.

Two of these are P0 mechanisms wearing manifest fields — one mount type, one capability set — and the labs treat them that way rather than as new material, which is why [objective 8](#objectives) asks you to read a field back to its primitive rather than forward from the docs. The workload gallery is sized to *choose* the right shape, not to read its controller — that is [P4](04-controllers.md).

**Labs** — [Predict the ReplicaSet counts at every step](../labs/01/08-rolling-update-predictions.md) · [Three probes, three different consequences](../labs/01/09-probes-three-kinds.md) · [The same ConfigMap, two ways in](../labs/01/10-config-as-env-and-volume.md) · [The P0 capability drop, as a manifest field](../labs/01/11-drop-a-capability-in-a-manifest.md) · [Five workload kinds, chosen by the forcing property](../labs/01/12-choose-the-workload-shape.md) · [1.C1 — delete a pod that something is watching](../labs/01/13-delete-a-managed-pod.md)

<a id="m1-4"></a>
### Module 1.4 — Services, Ingress, and access (~3 days)

CKAD Services & Networking (20%), operated shallowly. P7 owns the datapath; here you own the *abstractions*.

This is the module that installs **MetalLB**, which becomes [the standard UI-access path](../strands/lab-topologies.md#access) for every later phase. **CKAD uses Ingress, not Gateway API** — Gateway API is a CKA topic ([Recent changes](../strands/certs.md#cka-changes)) and drilling it here is wasted time.

**Labs** — [One Deployment, four exposures](../labs/01/14-four-ways-to-expose.md) · [A readiness probe, followed to an endpoint list](../labs/01/15-endpointslice-drains.md) · [Why a one-label name resolves and a two-label name does not](../labs/01/16-dns-from-a-pod.md) · [1.C2 — an empty endpoint list, from `describe` alone](../labs/01/17-break-the-endpoints.md)

<a id="m1-5"></a>
### Module 1.5 — Helm and kustomize (~3 days)

Package management, required by the brief and an explicit CKAD competency (Application Deployment, 20%).

The chart authored here is [the capstone's](#capstone) input, not a demo — build it once, properly, and grow it. And the module's most useful half-hour is the one that fails: Helm is a client-side templating-and-release tool with **no controller**, so a resource deleted behind its back stays deleted. That gap is exactly the one [Flux](04-controllers.md) closes in P4, and the contrast is the lesson.

**Labs** — [Two overlays over one base](../labs/01/18-kustomize-base-and-overlays.md) · [A chart with a subchart, a helper and a real conditional](../labs/01/19-author-a-helm-chart.md) · [Find the release on the cluster and read it](../labs/01/20-helm-upgrade-and-release-state.md) · [Delete something Helm created and watch nothing happen](../labs/01/21-helm-does-not-reconcile.md)

<a id="m1-6"></a>
### Module 1.6 — The Go primer (~ a few days, last)

Deliberately last, deliberately short. The learner can already read Go; this is the floor for reading `k/k` and, later, writing it. Sized in days ([#9](https://github.com/k3ii/k8s-academy/issues/9)), not the multi-week course it is not.

Cover, each with a tiny program that proves it:
- `context.Context` — cancellation and deadlines (it is in every `k/k` function signature).
- Goroutines and channels — a producer/consumer, a `select`, a `sync.WaitGroup`.
- Interfaces and struct embedding — the pattern behind every `k/k` `Interface` type.
- Error wrapping — `fmt.Errorf("...: %w", err)`, `errors.Is`/`errors.As`.
- Generics — enough to read them, since `client-go` now uses them.
- `go mod`, and **table-driven tests** — the universal `k/k` test shape, and the one you will write against `envtest` in P4.

**No cluster of its own** — the proof is one program, and it is written on [`forge`](../strands/lab-topologies.md#build-guest) after this phase's cluster is gone. It exists to remove the language as a variable before P2.

**Labs** — [One program that exercises every primer construct](../labs/01/25-the-go-primer-program.md)

---

<a id="chaos"></a>
## 3. Chaos drills

**Hand-driven, every one** — no chaos tool until [P6](06-kubelet-node.md), per [the standing principle](../strands/chaos.md#principle). This phase's drills are all *reconciliation made visible*: the payoff of P0's `controllers.md` reading, now something you can trigger with `kubectl`.

| # | Drill | By hand | What you must be able to say afterwards |
|---|---|---|---|
| 1.C1 | [**Delete a managed pod**](../labs/01/13-delete-a-managed-pod.md) | `kubectl delete pod` under a Deployment | Which controller recreated it, what it compared (desired vs actual replica count), and why deleting the *pod* is futile against a *Deployment* |
| 1.C2 | [**Break a Service's endpoints**](../labs/01/17-break-the-endpoints.md) | delete the EndpointSlice; then a selector typo | That endpoints are reconciled from pod readiness, not configured — diagnosed from `describe` alone |
| 1.C3 | [**Botch a rollout, then roll back**](../labs/01/22-botch-a-rollout-and-roll-back.md) | roll a broken image, `rollout undo` | The Deployment→ReplicaSet history mechanism, and why the old ReplicaSet was kept around |
| 1.C4 | [**Static-pod control-plane blip**](../labs/01/04-static-pod-blip.md) | `mv` a manifest out of `/etc/kubernetes/manifests` and back ([module 1.1](#m1-1)) | That the control plane is itself reconciled by a kubelet watching a directory |

**1.C3 is the capstone's rehearsal** — the incident note you write there is this drill, documented properly.

---

<a id="talks"></a>
## 4. Talks

Full entries, with runtimes, under [debugging](../strands/talks.md#debugging) in the talk index.

- **CrashLoopBackoff, Pending, FailedMount and Friends** (Thompson) — the systematic triage talk: for each bad pod state, which object to inspect and in what order. Labelled beginner, structurally sound, and *exactly* the right talk this early. Watch it during module 1.3.
- Optional, watch-now-reread-later: **Logs Told Us It Was DNS… It Wasn't DNS** (Bernaille) — the best debugging talk in the corpus, but its payoff (conntrack, kernel descent) lands properly after P7. Watching it now plants the *method*; you will re-watch it in [P11](11-synthesis.md).

---

<a id="ecosystem"></a>
## 5. Ecosystem

**Helm** — the package manager, treated for its internals rather than re-taught (module 1.5 is the hands-on).

- **Hands-on:** module 1.5 — a chart with a subchart, upgrade, rollback.
- **Internals note:** Helm is **entirely client-side**. There is no operator, no CRD, no reconcile loop — the release is an object on the cluster and nothing watches it. That makes it the deliberate foil for [Flux](04-controllers.md) in P4, which *does* reconcile, and the whole GitOps argument is visible in the gap module 1.5 opens. Where the release lives and what an upgrade diffs are [the labs'](../labs/01/20-helm-upgrade-and-release-state.md) to answer, and [the checklist](#checklist) asks you for both.
- **Maturity:** CNCF **graduated**. The default packaging tool for the ecosystem; `kustomize` (also here, built into `kubectl`) is the templating-free alternative, not a competitor for the same job.

---

<a id="ckad-block"></a>
## 6. ⏱ CKAD drill block — 1–2 weeks

> **This section is a different activity from everything above.** Everything above optimises for referents and fluency; this optimises for **speed and correctness under a clock**. Do not blend them. Do not read source during this block. When it ends, it ends.

Domain weights, exam mechanics, the practice-resource verdicts and the speed tactics live in the [certs strand](../strands/certs.md#ckad) and are **not restated here**. What follows is only this phase's relationship with the exam.

**Why the checkpoint is here:** CKAD is application-developer scope — workloads, config, services, Helm, observability — which is precisely what this phase operated. It is [the lowest-risk of the three exams](../strands/certs.md#ckad-changes): substantively stable, no retired topics to dodge.

**A genuine alignment, worth noticing.** CKAD's *Application Environment, Configuration and Security (25%)* lists **SecurityContexts and Capabilities** — which you did **by hand in [P0](00-linux-primitives.md)** and again as manifest fields in module 1.3. Most candidates memorise these; you can derive them. Likewise Helm sits in *Application Deployment (20%)* and you authored a real chart, not a `helm install` demo.

**What NOT to drill:**
- **Ingress, not Gateway API.** Gateway API is a **CKA** topic; drilling it for CKAD is wasted time ([Recent changes](../strands/certs.md#ckad-changes)).
- **The `k` alias and completion are pre-provisioned in the exam** — do not spend practice time building muscle memory for setup that is already done for you.
- **Nothing about etcd, the scheduler internals, or RBAC administration** — those are CKA/CKS scope. Weights and the drill list: [Speed tactics](../strands/certs.md#speed-tactics), [Practice resources](../strands/certs.md#practice).

**The harness** — the clock, the rules and the task list are [the drill block](../labs/01/26-ckad-drill-block.md), which runs on a **fresh** cluster it did not build.

**Exit:** CKAD passed. If not, that is a drill-block problem, not a phase problem — the gate below is independent of it, [by standing rule](../strands/certs.md#rules).

---

<a id="capstone"></a>
## 7. Capstone

**A nontrivial Helm-deployed application, plus a written incident note from a rollout you deliberately broke.**

Two artifacts, because this phase installs the habit every later capstone leans on: *trace it, then write it down*.

1. **[The chart](../labs/01/23-the-multi-service-app.md)** — grown from module 1.5's, not started fresh. A multi-service app deployed by one `helm install`, exposed via MetalLB, reachable in a browser.
2. **[The incident note](../labs/01/24-the-incident-note.md)** — drill 1.C3, documented properly. One page: symptom, the objects you inspected in order, the mechanism, the fix. This is the format [P6](06-kubelet-node.md), [P8](08-storage.md) and [P11](11-synthesis.md) capstones escalate.

**No `file:line` citations required here** — this phase is deliberately above the source. The trace is in terms of *objects and controllers*, not code. That standard returns in P2.

---

<a id="checklist"></a>
## 8. Checklist

Concrete demonstrable outputs. No item says *understand* or *know*; each is an artifact, a timed production, or a falsifiable claim.

**Produce from a blank cluster, under time:**
- [ ] A Deployment, Service and ConfigMap-configured app exposed via NodePort — **under 4 minutes**, from memory, no docs.
- [ ] Diagnose a wedged rollout and roll it back from `kubectl` output alone — **under 3 minutes**.
- [ ] A Pod with a dropped-and-re-added capability and `runAsNonRoot`, proven with `capsh` inside — **under 3 minutes**.

**Produce as a written artifact:**
- [ ] The Helm-deployed multi-service app (chart committed) reachable in a browser.
- [ ] The one-page rollout incident note from drill 1.C3.
- [ ] The kubeadm "what it generated and where" map from module 1.1 — the input P3 consumes.
- [ ] A single small Go program exercising all six primer constructs, with its table test passing.

**Falsifiable claims — write the answer, then verify:**
- [ ] What `resourceVersion` may and may not be used for, per `api-conventions.md`.
- [ ] Where Helm stores a release, and the three inputs `helm upgrade` diffs.
- [ ] Which manifest fields map to which P0 primitive (cgroup / capability / mount) — at least three.
- [ ] Why deleting a Pod under a Deployment does not remove it, in terms of what reconciles.

**Cert:**
- [ ] CKAD passed.

---

<a id="gate"></a>
## 9. Gate

You may advance to [P2](02-etcd.md) when:

1. **A cluster is running that you stood up by hand, and you can locate what `kubeadm` generated.** The static-pod manifests, the PKI, the kubeconfigs — named and mapped. This is objective and it is [P3](03-api-machinery.md)'s prerequisite, not busywork: P3 reads these files.
2. **The rollout incident note is complete**, and the Helm chart deploys the multi-service app cleanly. The standard is a note another person could follow to reproduce your diagnosis.
3. **No chaos drill remains mysterious** — specifically 1.C1: if you cannot say which controller recreated the pod and what it compared, **stay here.** Every reconciliation conversation from P2 onward assumes this is reflexive.

**CKAD is deliberately not a gate condition** — it is a milestone in a different track ([standing rule](../strands/certs.md#rules)). A phase that produced a hand-built cluster, a real chart, and a written incident has succeeded regardless of an exam booking.

The shallowness is the point. You now have the referents — objects, controllers, rollouts, a control plane you can see the parts of — that make [P2](02-etcd.md)'s descent into etcd, and everything below it, land on something already familiar rather than on nothing.
