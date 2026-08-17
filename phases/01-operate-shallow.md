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

## 2. Modules

The reading (Area 0 items 7–12) is interleaved into the modules that give it something to point at — the whole reason P0 deferred it here. There is **no build-track artifact** this phase; the Go primer that would normally underpin one is instead the closing module, deliberately after everything that does not need it.

### Module 1.1 — Stand up a control plane by hand, with kubeadm (~4 days)

The tool CKA expects, stood up deliberately so that P3 can *read what it left behind*. Do not use a one-command distro here — the point is the parts.

**Read** — [Area 0](../strands/source-reading.md#area-0-foundational) items 11–12, with a question to answer from each:

| Read | Answer from it |
|---|---|
| `staging.md` (item 11) | Why does `staging/src/k8s.io/*` exist, and how does `client-go` get published from inside the monorepo? Two pages that stop months of repo-layout confusion. |
| `local-up-cluster.sh` (item 12) | Not prose — the most honest inventory of what a control plane *is*. **List the flags it passes to each of `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`.** You will meet a third of them again in P3. |

**Do**
1. `kubeadm init` on the control-plane node, `kubeadm join` on the worker. Install a CNI (Cilium or Flannel — thin, since P7 owns networking).
2. **Locate everything it generated:** `/etc/kubernetes/manifests/*.yaml` (the control plane runs as static pods — connect to [P0](00-linux-primitives.md): the kubelet watches a *directory*, not the API), `/etc/kubernetes/pki/` (the CA and every serving/client cert), `/etc/kubernetes/*.conf` (the kubeconfigs).
3. Read one static-pod manifest and match its flags to your `local-up-cluster.sh` list.

**Break it** — `mv /etc/kubernetes/manifests/kube-apiserver.yaml` aside for sixty seconds, watch the kubelet stop the apiserver, then move it back and watch it return. The control plane is *reconciled by a kubelet watching a directory* — that is the single most clarifying thing about how Kubernetes runs itself, and it is a P0 mechanism (a kubelet, static pods) not a new one.

**Write down** — a one-page map of what `kubeadm` generated and where. This map is a required input to [P3](03-api-machinery.md), which reads these files as *source*.

### Module 1.2 — The object model, as referents (~3 days)

Shallow by design: name the parts, do not open the machinery. Every term here is a hook P2–P4 will hang mechanism on.

**Read** — [Area 0](../strands/source-reading.md#area-0-foundational) item 8, `api-conventions.md`, **named sections only** (it is 115 KB — never linear): *Types (Kinds)*, *Spec and Status*, *Typical status properties / Conditions*, *Resource Version*, *Lists*.

> **Question to answer from the source:** the conventions say `resourceVersion` is *opaque* and must not be interpreted by clients. What are you allowed to do with it, and what does the doc explicitly forbid? You will see *why* in [P2](02-etcd.md), where it turns out to be an etcd revision.

**Do**
1. For five different objects (Pod, Deployment, Service, ConfigMap, Node), print `spec` and `status` separately and identify who writes each half.
2. Watch `resourceVersion` change on an object as you edit it (`kubectl get -w -o yaml`). Do not yet ask how — just see that it moves.
3. Explore `kubectl api-resources` and `kubectl explain --recursive`: GVK, namespaced-vs-cluster-scoped, subresources (`/status`, `/scale`).

**Break it** — `kubectl edit` an object's `status` directly and watch a controller stomp it back within seconds. That stomp is the reconcile loop, and it is objective 8 from [P0](00-linux-primitives.md) — you re-read desired state and correct drift.

**Write down** — the spec/status owner for each of the five objects, and the one-sentence `resourceVersion` rule.

### Module 1.3 — Workloads: the controllers you will later read, operated (~4 days)

CKAD's centre of gravity, and a gallery of the controllers P4 dissects. Here you *drive* them; there you read them.

**Do**
1. Deployment with a rolling update: set `maxSurge`/`maxUnavailable`, roll a new image, `kubectl rollout status`, then `kubectl rollout undo`. **Predict the ReplicaSet count at each step before running it.**
2. Probes: liveness vs readiness vs startup. Wire a readiness probe to a togglable endpoint.
3. Config: ConfigMaps and Secrets as env and as mounted volumes; note the Secret volume is a `tmpfs` — a P0 mount, not disk.
4. `securityContext`: `runAsNonRoot`, `drop: [ALL]` then add back one capability. **This is the P0 capability drop as a manifest field** — confirm with `capsh --decode` inside the container.
5. The other workloads by shape: DaemonSet, StatefulSet, Job, CronJob — enough to choose the right one, not to read its controller.

**Break it** — chaos drill [1.C1](#4-chaos-drills): `kubectl delete pod` one of a Deployment's pods and watch the ReplicaSet recreate it; then `kubectl scale` to zero and back. Narrate which controller acted and what it compared. This is level-triggered reconciliation you can now *cause on demand*.

**Write down** — your rolling-update ReplicaSet predictions with actuals, and the capability you dropped with the `capsh` proof.

### Module 1.4 — Services, Ingress, and access (~3 days)

CKAD Services & Networking (20%), operated shallowly. P7 owns the datapath; here you own the *abstractions*.

**Do**
1. Expose one Deployment as ClusterIP, then NodePort, then LoadBalancer via **MetalLB** (L2, the `.200`–`.250` pool from the [capacity plan](https://github.com/k3ii/k8s-academy/issues/8)) — the standard UI-access path for every later phase.
2. `kubectl get endpointslices -w` while scaling the Deployment — watch endpoints appear and drain. Connect to module 1.3's readiness probe: unready pods leave the slice.
3. An Ingress with an ingress controller (ingress-nginx), path- and host-based rules. **CKAD uses Ingress, not Gateway API** — Gateway API is a CKA topic ([Recent changes](../strands/certs.md#cka-changes)).
4. CoreDNS: resolve a Service by name from a pod, read `/etc/resolv.conf`, and connect `ndots`/search-domains back to the [P0](00-linux-primitives.md) DNS path.

**Break it** — chaos drill [1.C2](#4-chaos-drills): delete the EndpointSlice for a Service by hand and watch the endpoint controller rebuild it; then point a Service's selector at a label no pod has and diagnose the empty slice from `kubectl describe` alone.

**Write down** — the four exposure types with the component each needs, and one paragraph on how a readiness probe reaches all the way to a Service's endpoint list.

### Module 1.5 — Helm and kustomize (~3 days)

Package management, required by the brief and an explicit CKAD competency (Application Deployment, 20%).

**Do**
1. `kustomize`: a base plus two overlays (dev/prod) differing by replicas and image. Note it is built into `kubectl apply -k`.
2. **Author a nontrivial Helm chart** — this is the capstone input, so build it here: multiple templates, a `values.yaml` with real conditionals, a helper `_helpers.tpl`, and one **subchart dependency**. Deploy a multi-service app with it.
3. `helm upgrade` with changed values; `helm rollback`; `helm diff` if the plugin is available. Watch what changes and what does not.

**Break it** — `kubectl delete` a resource Helm created, then `helm upgrade` and observe Helm *not* recreate it (three-way merge, not reconciliation). That gap — Helm is a client-side templating-and-release tool with no controller — is exactly the gap [Flux](04-controllers.md) closes in P4, and the contrast is the lesson.

**Write down** — where Helm stored the release (a Secret of type `helm.sh/release.v1`, per namespace) and what `helm upgrade` diffs (old manifest, new manifest, live state).

### Module 1.6 — The Go primer (~ a few days, last)

Deliberately last, deliberately short. The learner can already read Go; this is the floor for reading `k/k` and, later, writing it. Sized in days ([#9](https://github.com/k3ii/k8s-academy/issues/9)), not the multi-week course it is not.

Cover, each with a tiny program that proves it:
- `context.Context` — cancellation and deadlines (it is in every `k/k` function signature).
- Goroutines and channels — a producer/consumer, a `select`, a `sync.WaitGroup`.
- Interfaces and struct embedding — the pattern behind every `k/k` `Interface` type.
- Error wrapping — `fmt.Errorf("...: %w", err)`, `errors.Is`/`errors.As`.
- Generics — enough to read them, since `client-go` now uses them.
- `go mod`, and **table-driven tests** — the universal `k/k` test shape, and the one you will write against `envtest` in P4.

**No lab of its own.** The proof is objective 7 and the checklist item: a single small program using all six. It exists to remove the language as a variable before P2.

---

## 3. Chaos drills

**Hand-driven, every one** — no chaos tool until [P6](06-kubelet-node.md), per [the standing principle](../strands/chaos.md#principle). This phase's drills are all *reconciliation made visible*: the payoff of P0's `controllers.md` reading, now something you can trigger with `kubectl`.

| # | Drill | By hand | What you must be able to say afterwards |
|---|---|---|---|
| 1.C1 | **Delete a managed pod** | `kubectl delete pod` under a Deployment | Which controller recreated it, what it compared (desired vs actual replica count), and why deleting the *pod* is futile against a *Deployment* |
| 1.C2 | **Break a Service's endpoints** | delete the EndpointSlice; then a selector typo | That endpoints are reconciled from pod readiness, not configured — diagnosed from `describe` alone |
| 1.C3 | **Botch a rollout, then roll back** | roll a broken image, `rollout undo` | The Deployment→ReplicaSet history mechanism, and why the old ReplicaSet was kept around |
| 1.C4 | **Static-pod control-plane blip** | `mv` a manifest out of `/etc/kubernetes/manifests` and back (module 1.1) | That the control plane is itself reconciled by a kubelet watching a directory |

**1.C3 is the capstone's rehearsal** — the incident note you write there is this drill, documented properly.

---

## 4. Talks

Full entries, with runtimes, under [debugging](../strands/talks.md#debugging) in the talk index.

- **CrashLoopBackoff, Pending, FailedMount and Friends** (Thompson) — the systematic triage talk: for each bad pod state, which object to inspect and in what order. Labelled beginner, structurally sound, and *exactly* the right talk this early. Watch it during module 1.3.
- Optional, watch-now-reread-later: **Logs Told Us It Was DNS… It Wasn't DNS** (Bernaille) — the best debugging talk in the corpus, but its payoff (conntrack, kernel descent) lands properly after P7. Watching it now plants the *method*; you will re-watch it in [P11](11-synthesis.md).

---

## 5. Ecosystem

**Helm** — the package manager, treated for its internals rather than re-taught (module 1.5 is the hands-on).

- **Hands-on:** module 1.5 — a chart with a subchart, upgrade, rollback.
- **Internals note:** Helm is **entirely client-side**. There is no operator, no CRD, no reconcile loop. A "release" is a **Secret** (`helm.sh/release.v1`, gzipped manifest + values) in the release namespace; `helm upgrade` computes a **three-way merge** (old manifest, new manifest, live cluster state) and PATCHes the diff. Read one release Secret's decoded contents. This is the deliberate foil for [Flux](04-controllers.md) in P4, which *does* reconcile — the whole GitOps argument is visible in the gap module 1.5's Break-it opened.
- **Maturity:** CNCF **graduated**. The default packaging tool for the ecosystem; `kustomize` (also here, built into `kubectl`) is the templating-free alternative, not a competitor for the same job.

---

## 6. ⏱ CKAD drill block — 1–2 weeks

> **This section is a different activity from everything above.** Everything above optimises for referents and fluency; this optimises for **speed and correctness under a clock**. Do not blend them. Do not read source during this block. When it ends, it ends.

Domain weights, exam mechanics, the practice-resource verdicts and the speed tactics live in the [certs strand](../strands/certs.md#ckad) and are **not restated here**. What follows is only this phase's relationship with the exam.

**Why the checkpoint is here:** CKAD is application-developer scope — workloads, config, services, Helm, observability — which is precisely what this phase operated. It is [the lowest-risk of the three exams](../strands/certs.md#ckad-changes): substantively stable, no retired topics to dodge.

**A genuine alignment, worth noticing.** CKAD's *Application Environment, Configuration and Security (25%)* lists **SecurityContexts and Capabilities** — which you did **by hand in [P0](00-linux-primitives.md)** and again as manifest fields in module 1.3. Most candidates memorise these; you can derive them. Likewise Helm sits in *Application Deployment (20%)* and you authored a real chart, not a `helm install` demo.

**What NOT to drill:**
- **Ingress, not Gateway API.** Gateway API is a **CKA** topic; drilling it for CKAD is wasted time ([Recent changes](../strands/certs.md#ckad-changes)).
- **The `k` alias and completion are pre-provisioned in the exam** — do not spend practice time building muscle memory for setup that is already done for you.
- **Nothing about etcd, the scheduler internals, or RBAC administration** — those are CKA/CKS scope. Weights and the drill list: [Speed tactics](../strands/certs.md#speed-tactics), [Practice resources](../strands/certs.md#practice).

**Exit:** CKAD passed. If not, that is a drill-block problem, not a phase problem — the gate below is independent of it, [by standing rule](../strands/certs.md#rules).

---

## 7. Capstone

**A nontrivial Helm-deployed application, plus a written incident note from a rollout you deliberately broke.**

Two artifacts, because this phase installs the habit every later capstone leans on: *trace it, then write it down*.

1. **The chart** (from module 1.5): a multi-service app — at least a frontend, a backend, and a datastore — deployed by one `helm install`, with a subchart dependency, real `values.yaml` conditionals, probes, resource requests/limits, and a ServiceAccount per workload. Exposed via MetalLB and reachable in a browser.
2. **The incident note** (from drill 1.C3): roll out a deliberately broken image (bad probe, or a missing ConfigMap key), observe the rollout wedge, diagnose it *from `kubectl` output alone*, and roll back. Then **write the incident up** — symptom, the objects you inspected in order, the mechanism (Deployment kept the old ReplicaSet, `maxUnavailable` capped the blast radius), and the fix. One page. This is the format [P6](06-kubelet-node.md), [P8](08-storage.md) and [P11](11-synthesis.md) capstones escalate.

**No `file:line` citations required here** — this phase is deliberately above the source. The trace is in terms of *objects and controllers*, not code. That standard returns in P2.

---

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

## 9. Gate

You may advance to [P2](02-etcd.md) when:

1. **A cluster is running that you stood up by hand, and you can locate what `kubeadm` generated.** The static-pod manifests, the PKI, the kubeconfigs — named and mapped. This is objective and it is [P3](03-api-machinery.md)'s prerequisite, not busywork: P3 reads these files.
2. **The rollout incident note is complete**, and the Helm chart deploys the multi-service app cleanly. The standard is a note another person could follow to reproduce your diagnosis.
3. **No chaos drill remains mysterious** — specifically 1.C1: if you cannot say which controller recreated the pod and what it compared, **stay here.** Every reconciliation conversation from P2 onward assumes this is reflexive.

**CKAD is deliberately not a gate condition** — it is a milestone in a different track ([standing rule](../strands/certs.md#rules)). A phase that produced a hand-built cluster, a real chart, and a written incident has succeeded regardless of an exam booking.

The shallowness is the point. You now have the referents — objects, controllers, rollouts, a control plane you can see the parts of — that make [P2](02-etcd.md)'s descent into etcd, and everything below it, land on something already familiar rather than on nothing.
