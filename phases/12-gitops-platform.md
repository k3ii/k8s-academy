# Phase 12 — GitOps & platform engineering

> **5–6 weeks.** The only phase that climbs *up*. Eleven phases removed abstraction until `kubectl run nginx` was a cited path from terminal to syscall; this one builds abstraction back — deliberately, for people who will never read that path. It is structurally the cheapest phase to cut and the last one written, and its real deliverable is not the platform but the **critique of the platform**: naming what your abstraction costs the developer who consumes it. Nothing here is new machinery — a platform API is [a CRD plus a controller](04-controllers.md), which you have now written twice by hand. What is new is judgement.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P4 Controllers](04-controllers.md) — Flux *is* the reconcile loop you hand-wrote, and Crossplane's composition engine is a controller that emits managed resources; without P4 both are magic. [P3](03-api-machinery.md) — vcluster ships its own apiserver, and an XRD is a CRD with a structural schema whose admission you already read. [P5](05-scheduler.md) — a vcluster tenant's pods are **real pods on the host, scheduled by the host scheduler**; P5 is what lets you see which half is real. [P8](08-storage.md) — the capstone provisions real storage. [P9](09-service-mesh.md) — Flagger drives canaries **through the mesh**; cut P9 and progressive delivery degrades to Argo Rollouts or is cut with it. |
| **Unlocks** | **Nothing — this is the summit.** There is no P13. The curriculum ends by *using* the mastery it spent eleven phases building, which is a better close than demonstrating it once more. |
| **Source** | **No new `k/k` area** — the machinery is all [Area 4](../strands/source-reading.md#area-4-controllers) (controllers) and [Area 2](../strands/source-reading.md#area-2-api-machinery) (apiserver), already read. What is new is reading the **platform tools' own** Go at pinned tags — `helm-controller`'s drift mode, Crossplane's composition `mode` enum, the vcluster syncer — and re-reading your own [P4](04-controllers.md) operator as the thing every one of them is a variation of. |
| **Build track** | **None** ([artifact table](../strands/build-mechanics.md#artifact-table) lists no P12 artifact) — but the platform you assemble is CRD-plus-controller, and [`build-mechanics#sizing`](../strands/build-mechanics.md#sizing) applies to **your own output**: Crossplane's function pods ship `resources: {}`, so a `DeploymentRuntimeConfig` override is mandatory, not a footnote. The platform you build has a pod-sizing problem of its own. |
| **Ecosystem** | **The heaviest phase — and it does not all fit at once.** Flux · Helm · SOPS · sealed-secrets · Flagger · KRO · Crossplane · 2×vcluster, plus Istio and Prometheus reused from earlier. Run as [**two lab groups with a teardown between**](#ecosystem) ([#14](https://github.com/k3ii/k8s-academy/issues/14)), because both co-resident is unmeasured and unwise. |
| **Cert** | **None.** Nothing in CKAD/CKA/CKS covers this. The last exam was CKS at [P10](10-security.md). |
| **Lab** | [**`platform`**](../strands/lab-topologies.md#platform) — a topology added *for this phase* ([#14](https://github.com/k3ii/k8s-academy/issues/14), not #8). [#8](https://github.com/k3ii/k8s-academy/issues/8)'s "prefer `pair`" rule is for DaemonSet-heavy phases; **nothing here is a DaemonSet**, so a second node would only pay the OS+kubelet tax twice and fragment 5GB into two buckets. One node, one bucket. **First lab step: `kubectl top pod`.** |
| **Labs** | [`labs/12/`](../labs/12/README.md) — 18 exercises, in order; two lab groups with a teardown between, on the single `platform` node. |
| **Strands** | [build](../strands/build-mechanics.md#sizing) · [talks](../strands/talks.md#controllers) · [chaos](../strands/chaos.md#principle) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — a running platform, a cited line, a timed production, or a critique a hostile reader could hold against the artifact. *understand* and *know* appear nowhere; the whole phase turns on the difference between driving a tool and naming what it costs.

By the end you can:

1. **Run a change through GitOps end to end** — commit → Flux `Source` → `Kustomization`/`HelmRelease` → applied — and state, from the controller's source, what happens to a hand-edited resource between reconciles with drift detection off versus on.
2. **Compare the three secret mechanisms on mechanism** — SOPS (envelope encryption, decrypted in-process), sealed-secrets (a controller holding a private key), ESO (a controller reading a store) — and ship the SOPS half at **zero in-cluster cost**.
3. **Expose one vcluster tenant** and point at the *same pod* twice — as a tenant pod in the virtual apiserver and as a real pod in a host namespace — naming which component is real and which is a shim.
4. **Publish a platform API** as a CRD + controller (KRO first, then a Crossplane Composition) that a developer consumes with a `create` on one kind, and cite the `DeploymentRuntimeConfig` line that stops your own function pod from running unbounded.
5. **Drive a metric-gated canary** with Flagger through the [P9](09-service-mesh.md) mesh, with automated rollback on an SLO breach — the same rollout as [P1](01-operate-shallow.md)'s blunt `maxSurge`, seen from the other end ten months on.
6. **Write the critique** — what your abstraction hides, where it leaks, what a real developer would hate, and which of the eleven prior phases' hard-won skill it makes *unnecessary* versus merely *invisible*. This is the deliverable; the platform is the evidence.

---

<a id="modules"></a>
## 2. Modules

No new corpus reading — the machinery is [Area 4](../strands/source-reading.md#area-4-controllers) and [Area 2](../strands/source-reading.md#area-2-api-machinery), read. The reading here is the **tools' own source at pinned tags**, held to the [archaeology drill standard](../strands/source-archaeology.md#drills): every mechanism claim resolves to a line a hostile reader could open, and platform tooling moves fast, so [live-verify before trusting](../strands/source-archaeology.md#stale-paths). The modules run as **two lab groups with a teardown between them** ([#14](https://github.com/k3ii/k8s-academy/issues/14), [§5](#ecosystem)): Group A (delivery) is modules 12.1–12.3, Group B (platform API & tenancy) is 12.4–12.5. The order is a phase-file decision the research left open ([#14](https://github.com/k3ii/k8s-academy/issues/14)); the group boundary settles it.

### Group A — delivery

<a id="m12-1"></a>
### Module 12.1 — GitOps as a delivery model (~1.5 wk)

The [mechanism was P4](04-controllers.md); this is running a delivery model on the reconcile loop already read.

> **Question to answer from the source:** in `helm-controller`, which function returns the drift mode, and what does it return when the field is unset? Cite the line — the default is the whole lab beat. Then: `HelmChart.spec.sourceRef.kind` accepts `GitRepository` in source-controller's enum — cite it, and state why that means **no chart registry is needed** on the isolated bridge (the git revision *is* the chart version).

**Labs** — [`commit → Source → Kustomization → applied`](../labs/12/01-gitops-the-reconcile-loop-you-already-wrote.md) · [Drift detection off by default](../labs/12/02-drift-detection-off-by-default.md) · [12.C1 — a commit is a deploy to everything](../labs/12/03-12c1-a-commit-is-a-deploy-to-everything.md) · [Three ways to not commit a secret](../labs/12/04-three-ways-to-not-commit-a-secret.md)

<a id="m12-2"></a>
### Module 12.2 — Progressive delivery (~0.5 wk)

Flagger against the [P9](09-service-mesh.md) mesh — the same operation as [P1](01-operate-shallow.md)'s rollout, from the other end.

> **Question to answer from observation and source:** which metric query gates the promotion, and where does Flagger read it? Contrast the blast radius with [P1](01-operate-shallow.md)'s `maxSurge`/`maxUnavailable`: the same "replace pods gradually," but one is blind to whether the new pods are *healthy by your definition* and one is not. State the exact difference in what each can express.

**Labs** — [A canary gated on a metric](../labs/12/05-a-canary-gated-on-a-metric.md) · [12.C2 — the metric dies mid-canary](../labs/12/06-12c2-the-metric-dies-mid-canary.md)

<a id="m12-3"></a>
### Module 12.3 — Golden paths, portals, and platform-as-product (~1 wk)

The judgement module. The most valuable content is the **failure mode**, so it is taught through postmortems, not a lab.

> **Question to answer (from the tools against each other):** a Backstage scaffolder template and a Flux-reconciled CRD both "create an app from a form." One converges continuously and one runs once. Which failure does each hide from the developer, and which does it expose? Name a concrete case where the difference bites.

**Labs** — [A golden path with no portal](../labs/12/07-a-golden-path-with-no-portal.md) · [Backstage, read and never installed](../labs/12/08-backstage-read-never-installed.md) · [12.C5 — the leak in the golden path](../labs/12/09-12c5-the-leak-in-the-golden-path.md)

<a id="teardown"></a>
### — teardown —

Tear the delivery stack down before Group B. Istio + Prometheus alone are ~1.15GB; the platform node does not hold both groups honestly ([#14](https://github.com/k3ii/k8s-academy/issues/14)). The teardown is itself a GitOps test: if the cluster does not come back from git, Group A did not actually make git the source of truth.

**Lab** — [The teardown that proves git](../labs/12/10-the-teardown-that-proves-git.md)

### Group B — platform API & tenancy

<a id="m12-4"></a>
### Module 12.4 — Multi-tenancy (~1 wk)

Where a tenancy boundary is, and precisely where it leaks.

> **Question to answer from the source and the cluster:** the vcluster syncer is a `kube-apiserver` + `kube-controller-manager` + kine/SQLite in **one Go process** — which half of a tenant pod is real (the container, on the host, scheduled by the [P5](05-scheduler.md) host scheduler) and which is a shim (the tenant's apiserver view)? Point at the pod in both apiservers. And: what does the 4Gi→1Gi limit convert unbounded growth *into*, and why is that OOMKill the better failure?

**Labs** — [A tenancy boundary and where it leaks](../labs/12/11-a-tenancy-boundary-and-where-it-leaks.md) · [The same pod in two apiservers](../labs/12/12-the-same-pod-in-two-apiservers.md) · [12.C3 — the syncer dies, the host pods live](../labs/12/13-12c3-the-syncer-dies-the-host-pods-live.md)

<a id="m12-5"></a>
### Module 12.5 — Platform APIs (~1.5 wk)

The module the whole build track prepared for. **KRO first, Crossplane second** — the numbers force the order ([#14](https://github.com/k3ii/k8s-academy/issues/14)).

> **Question to answer from the source:** in Crossplane at its pinned tag, the Composition `mode` enum — enumerate its values (there is one) and confirm `Resources` is **absent from the schema**, not deprecated. Then find where the default `DeploymentRuntimeConfig` is created and show its spec is empty — the line that makes your function pod BestEffort. Cite both. This is the phase's thesis in miniature: *the platform you build has the pod-sizing problem you spent P8 learning to see.*

> **Second question (Helm vs Composition, mechanism-level):** a chart is client-side templating that produces a manifest; a Composition publishes an API — `kubectl get webapp` *works*, there is a controller, a status, and one RBAC verb behind it. Under Helm, `kubectl get webapp` simply fails, and self-service needs the **union of every permission the chart applies**. State the four consequences (drift, whether a live API object exists, who can self-service, what each can express) — the last being that Helm structurally cannot depend on state that does not exist yet, because it renders once.

**Labs** — [KRO: custom resource in, children out](../labs/12/14-kro-custom-resource-in-children-out.md) · [Crossplane: the two lines that size your pod](../labs/12/15-crossplane-the-two-lines-that-size-your-pod.md) · [Helm cannot publish an API](../labs/12/16-helm-cannot-publish-an-api.md) · [12.C4 — the function pod with no limits](../labs/12/17-12c4-the-function-pod-with-no-limits.md)

---

<a id="chaos"></a>
## 3. Chaos drills

Anchored in [`chaos.md#principle`](../strands/chaos.md#principle). GitOps changes what chaos *means*: for the first time the failure can be **committed**, so the blast radius is every cluster watching the repo. Every drill here is by hand — the fault is a commit, a rotation, a broken syncer — because recognising your own change's consequence from the system's behaviour is the skill.

| # | Drill | What you must produce afterwards |
|---|---|---|
| 12.C1 | [**Drift, then a bad commit**](../labs/12/03-12c1-a-commit-is-a-deploy-to-everything.md) | Flux reverting the hand-edit once drift is on; the bad commit reconciling *everywhere at once* |
| 12.C2 | [**Kill the metric mid-canary**](../labs/12/06-12c2-the-metric-dies-mid-canary.md) | Flagger's decision with no data — promote, hold, or roll back — named |
| 12.C3 | [**Break the vcluster syncer**](../labs/12/13-12c3-the-syncer-dies-the-host-pods-live.md) | Host pods still running (real) while the tenant view goes dark (shim) |
| 12.C4 | [**Function pod with `resources: {}`**](../labs/12/17-12c4-the-function-pod-with-no-limits.md) | The BestEffort pod's unbounded growth and what reclaimed it |
| 12.C5 | [**A leak in the golden path**](../labs/12/09-12c5-the-leak-in-the-golden-path.md) | Time-to-leak for a fresh consumer — the failure-mode evidence for the critique |

12.C1's second half is the phase's signature drill: **a mistake you commit is a mistake you deploy to everything.** The rest each attack one platform guarantee (metric-gating, tenant isolation, pod bounds, abstraction) at the seam it actually breaks.

---

<a id="talks"></a>
## 4. Talks

The controller talks from [Area 4](../strands/talks.md#controllers) are the mechanism under every tool here; the failure-mode content of module 12.3 leans on the [debugging postmortems](../strands/talks.md#debugging).

- **★ The Life of a Kubernetes Watch Event** ([controllers](../strands/talks.md#controllers)) — the watch → informer → workqueue pipeline that Flux, Crossplane, KRO and Flagger *all* are. Re-watched here as the one mechanism behind four tools: every "GitOps engine" is this loop with a git `Source` in front.
- **★ Don't Write Controllers Like Charlie Don't Does** ([controllers](../strands/talks.md#controllers)) — status-vs-spec confusion, non-idempotent reconciles, requeue misuse. The catalogue of ways the composition engine you're driving can misbehave, and the checklist for critiquing your own CRD's controller.
- **★ Kubernetes Failure Stories** ([debugging](../strands/talks.md#debugging)) — read here for the platform-failure angle: how much of the pain is a platform abstraction that hid the wrong thing at the wrong moment. The evidence base for module 12.3's failure-mode catalogue.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**The ecosystem-heaviest phase — and the one that states its tooling's immaturity out loud.** Everything is minimised and split into two groups with a teardown between, because the [`platform`](https://github.com/k3ii/k8s-academy/issues/8) node holds either group but not both honestly ([#14](https://github.com/k3ii/k8s-academy/issues/14)).

| Group | Contents | Notes |
|---|---|---|
| **A — delivery** | Flux (4 controllers) · Helm · **SOPS** (0 pods — decrypts in-process in `kustomize-controller`) · sealed-secrets · Flagger + loadtester + podinfo · Istio ([P9](09-service-mesh.md) pattern) · Prometheus ([P6](06-kubelet-node.md)) | Helm appears as a **delivery/abstraction layer**, not chart authoring ([P1](01-operate-shallow.md) owns that). `helm-controller` renders a chart as *desired state*. |
| **B — platform API & tenancy** | KRO · Crossplane v2 + 1 function · 2 × vcluster | KRO **first**; Crossplane needs no provider but its function pods need a `DeploymentRuntimeConfig`; vcluster limit dropped 4Gi→1Gi. |

- **Backstage — read, don't install.** The disqualifier is the **build** (`yarn tsc` OOMs at ~4GB, no `--set` fixes it), not the runtime ([#14](https://github.com/k3ii/k8s-academy/issues/14)). Build the golden path from Flux + a CRD + a template repo — on the mechanism axis that is *strictly more* interesting, because the scaffolder has no reconcile loop.
- **Internals note (required):** nothing in this phase adds machinery to Kubernetes. Flux, KRO and Crossplane are controllers; a Composition/XRD is a CRD with a structural schema; vcluster is an apiserver-plus-syncer whose pods are real host pods. **Every piece is machinery you already read, applied — which is why the phase lands as synthesis, and why its risk is judgement, not mechanism.**
- **Maturity, stated out loud ([#14](https://github.com/k3ii/k8s-academy/issues/14)):** **KRO has no CNCF tier** (a Kubernetes SIG subproject, `v0.9.x`, `v1alpha1`, its central CRD recently *renamed*); **vcluster is not a CNCF project** (vendor OSS; the chart's default image is the commercial build, so `repository: loft-sh/vcluster-oss` is an explicit lab choice); **sealed-secrets is absent from the landscape entirely**. The pattern is the lesson: **platform engineering's tooling is markedly less mature than the layers below it** — [P8](08-storage.md)'s CSI is a stable contract; this stack is an alpha API, a vendor product and a non-foundation controller. That is a fact about the field, not an artifact of selection.
- **Three stale levers** to recognise, not try: `mode: Resources` in a Crossplane Composition (removed); "use k3s in the vcluster, it's lighter" (distro removed); "ESO requires an external secret store" (its `kubernetes` provider reads the local cluster).

---

<a id="capstone"></a>
## 6. Capstone

**A working internal platform, plus the critique of it — and the critique is the actual deliverable.**

Reassemble a **lean** co-resident set (Flux + KRO/Crossplane + one vcluster tenant — Istio/Prometheus/Flagger torn down) and build the platform:

1. A developer commits a *small* manifest — "I want an app, a database, and an ingress" — to a git repo.
2. Your CRD + Crossplane Composition + Flux provisions it into a **tenant namespace** with `ResourceQuota` and `NetworkPolicy` enforced, storage from the [P8](08-storage.md) CSI path, drift corrected automatically.
3. The developer **never touches Kubernetes directly** — one `kubectl get webapp`, one `create` verb, no Deployment, no Service, no PVC in their view.

**Cite `file:line` a hostile reader could check** — this phase's citations are the tools' own source at your pinned tags: the `helm-controller` drift-mode default that makes reconciliation continuous, the Crossplane `mode`-enum line and the empty-`DeploymentRuntimeConfig` line that made your own function pod need sizing, and the vcluster syncer's translation. A reader clones each at your stated tag and opens every line; "Crossplane composes it" fails, `runtime/*.go:NNN@tag` passes. The [archaeology standard](../strands/source-archaeology.md#drills) applies to tools, not just `k/k`.

**Then the critique** — a written document, the real deliverable:
- What the abstraction **hides** (correctly) and where it **leaks** (the value that shows through at the worst moment — your 12.C5 evidence).
- What a real developer would **hate** about it — the failure-mode catalogue from 12.3, turned on your own platform.
- Which of the eleven prior phases' hard-won skill your abstraction makes **unnecessary** versus merely **invisible** — the distinction that separates a platform engineer from someone who writes CRDs. A developer who never needs to look is served; a developer who *can't* look when it breaks is trapped.

**Lab** — [The platform, and its critique](../labs/12/18-the-platform-and-its-critique.md)

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] An app under Flux with the drift beat shown both ways — hand-edit ignored (off), then corrected (on) (12.1).
- [ ] A secret shipped via SOPS at zero in-cluster cost, with sealed-secrets and ESO compared on mechanism (12.1).
- [ ] A Flagger canary promoted on an SLO and auto-rolled-back on a breach (12.2).
- [ ] One vcluster tenant pod shown in both apiservers, host namespace named, syncer limit at ~1Gi (12.4).
- [ ] A KRO `ResourceGraphDefinition` and a Crossplane Composition each provisioning children, the function pod sized by `DeploymentRuntimeConfig` (12.5).

**Written artifacts (each is a module's Write-down):**
- [ ] The `commit → Source → Kustomization → applied` path with drift-mode + reconcile-interval lines cited (12.1).
- [ ] The canary metric query + thresholds and the two-line contrast with P1's `maxSurge` (12.2).
- [ ] The golden path (template + CRD + Flux) and the platform-failure-mode catalogue (12.3).
- [ ] The tenant pod in both apiservers + the `top pod` number + the boundary-leak inventory (12.4).
- [ ] The two cited Crossplane lines + the Helm-vs-Composition four-consequence table (12.5).

**Falsifiable claims — write, then verify:**
- [ ] Why a mistake you commit is a mistake you deploy everywhere (12.C1).
- [ ] Which half of a vcluster tenant is real and which is a shim (12.4).
- [ ] Why Helm structurally cannot depend on state that does not exist yet (12.5).

**The deliverable:**
- [ ] The platform critique — what it hides, where it leaks, what a developer would hate, and which prior-phase skill it makes unnecessary versus invisible (Capstone).

---

<a id="gate"></a>
## 8. Gate

The curriculum ends when:

1. **The platform works from the developer's side** — a small committed manifest becomes an app + database + ingress in a quota-and-NetworkPolicy-bounded tenant, drift corrected, with the developer touching no Kubernetes object directly. If provisioning works but the developer still has to `kubectl edit` a Deployment, the abstraction failed and the phase is not done.
2. **Every mechanism claim is cited to the tool's own source** — the drift-mode default, the Crossplane `mode` enum and empty runtime config, the vcluster syncer — each a `file:line` at a stated tag a hostile reader opens. A platform you can drive but not read is a platform you cannot debug at 3am.
3. **The critique exists and is honest** — it names a real leak, a thing a real developer would hate, and at least one prior-phase skill the abstraction makes *invisible* rather than *unnecessary*. If the critique is "it's great," you built a platform and learned nothing; the critique is the phase.

This is the end. Twelve phases ago [P0](00-linux-primitives.md) made a container by hand from `clone`, `unshare` and cgroups, and named `kubectl run nginx` as the target to build toward; [P11](11-synthesis.md) traced that command to exactly those syscalls, cited. This phase hides all of it behind one `create` — and the last thing the curriculum asks is not whether you can build the abstraction, but whether you can say, precisely and against your own work, what it costs the person who trusts it. You have read the whole machine. Now you can say what you are hiding, and from whom.
