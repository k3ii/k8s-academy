# Platform-engineering stack footprints — synthesis and P12 topology

Resolution material for [#14](https://github.com/k3ii/k8s-academy/issues/14). Two research rounds
were run in parallel; both are reproduced in full below this synthesis. Round A covers Crossplane,
KRO, vcluster and Helm; Round B covers Flagger, Backstage and the secrets trio. Every number in both
rounds was read out of the project's own chart, manifest or Go source at a pinned tag — no vendor
marketing, no blog posts, and gaps marked `[UNVERIFIED]` rather than estimated.

The ceiling, restated: **~9.5GB spendable RAM, 6 cores (i5-8400T, 1 thread/core), 95G disk**, one
topology at a time.

---

## 1. The headline: P12 wants a topology that does not exist yet

[#8](https://github.com/k3ii/k8s-academy/issues/8) gave P12 the placeholder line "`pair`, everything
else torn down," which was an estimate — the phase did not exist when that research ran. With the
numbers in, **`pair` is the wrong shape**, and the reason is interesting enough to record.

#8's standing guidance is *prefer `pair` over `workhorse` for DaemonSet-heavy modules*, because
per-node agent cost is paid once per node and dropping a node buys back more than the node's own RAM.
That logic is correct and it **inverts for P12**, because nothing in P12 is a DaemonSet. The entire
stack — Flux's four controllers, Crossplane core, a Crossplane function, KRO, Flagger, sealed-secrets,
two vcluster syncers — is **single-replica Deployments and StatefulSets**. There is no per-node
multiplier to avoid. What there *is*, on a two-node topology, is the OS + containerd + kubelet tax paid
twice for no benefit, and 5.0GB fragmented into a 3072MB bucket and a 2048MB bucket that a 640Mi
vcluster pair and a 384Mi Crossplane install must be hand-placed between.

### Recommended: a new named topology, `platform`

| Name | Shape | RAM | Disk | Purpose |
|---|---|---|---|---|
| **platform** | 1 × 6144MB / 4c / 40G, control plane untainted | 6.0GB | 40G | P12 — GitOps, platform APIs, multi-tenancy, progressive delivery |

Same sizing as the existing `nested` topology, different purpose (that one runs kind inside; this one
is a real single-node kubeadm cluster). One OS tax, one kubelet, and all 6.0GB in a single schedulable
bucket. 40G is comfortably inside 95G on its own.

**Why single-node is not a compromise here.** The obvious objection is that multi-tenancy wants more
than one node. It does not: vcluster's syncer translates tenant pods into a **namespace** on the host
cluster, not onto a particular node, so the mechanism the module teaches — two views of one pod — is
fully visible on one node. Nothing else in P12 cares about node count either. Progressive delivery is
traffic weights; GitOps is reconciliation; platform APIs are controllers.

### And P12 runs as two lab groups, not one long-lived install

Even at 6.0GB, installing everything at once is unnecessary and — given the unverified RSS figures
below — reckless. Split the phase's cluster life in two, with a teardown between:

| Group | Contents | Requests (minimised) |
|---|---|---|
| **A — delivery** | Flux (4 controllers) · Helm · SOPS · sealed-secrets · Flagger + loadtester + podinfo · Istio (reused pattern from P9) · Prometheus (reused from P6) | ~1.9GB |
| **B — platform API and tenancy** | KRO · Crossplane + 1 function · 2 × vcluster | ~1.4GB |

Neither group needs the other's heavy items: Group B has no use for Istio + Prometheus (~1.15GB
together), and Group A has no use for two vcluster syncers. Against a ~1.0–1.3GB single-node cluster
baseline, each group sits near 2.5–3.2GB of the 6.0GB — enough headroom that observed RSS overshooting
requests is survivable rather than fatal.

Both groups co-resident would land around 3.9GB of requests plus baseline. That probably fits. It
should still not be done, because the one number the whole phase rests on is unmeasured (§5).

---

## 2. Install-or-read, per project

| Project | Verdict | Cost, minimised | CNCF tier |
|---|---|---|---|
| **Helm** | **Install — free** | 0 pods, ≤10 Secrets per release | Graduated 2020-05-01 |
| **SOPS** | **Install — free** | **0 pods, 0 MiB** (decrypts inside Flux's `kustomize-controller`) | Sandbox 2023-05-17 |
| **KRO** | **Install** — and teach it *first* | 1 pod, 128Mi | **None** — Kubernetes SIG subproject, no independent tier |
| **Crossplane** | **Install-minimised** — no provider needed | 3 pods, ~384Mi | Graduated **2025-10-28** |
| **vcluster** | **Install-minimised** — 2 tenants | 4 pods, 640Mi, 2×2Gi PVC | **Not a CNCF project** — Loft Labs vendor OSS |
| **Flagger** | **Install** — reuses Istio and Prometheus | 4 pods idle / 6 mid-canary, 224Mi | Graduated (inherited from Flux, 2022-11-30) |
| **sealed-secrets** | **Install-minimised** | 1 pod, 32Mi req / 128Mi limit | **Not a CNCF project at all** — absent from `landscape.yml` |
| **External Secrets Operator** | **Read** — or one minimised lab, `kubernetes` provider only | 3 pods, ~96Mi, **1.9MB of CRDs** | Sandbox 2022-07-26, **no promotion in four years** |
| **Backstage** | **Read, don't install** | — | Incubating 2022-03-15 |
| **OpenBao / Vault** | **Cut** | (2 pods, 10GiB PVC) | — |
| **In-cluster OCI registry** | **Cut** | (1 pod `resources: {}`, 10GiB to be non-lossy) | — |

### The five findings that changed the plan

**1. Crossplane v2 needs no provider at all — the feasibility question, answered better than the ticket assumed.** v2.0.0 made Compositions able to include *any* Kubernetes resource natively, so an XRD + Composition emitting `Deployment`s and `ConfigMap`s works with core Crossplane plus one function pod: **no cloud account, no credentials, no provider CRDs.** In v1 this required `provider-kubernetes`. The composition lab is therefore fully self-contained.

**2. But functions are now mandatory, and every function pod ships `resources: {}`.** The `mode` enum in the Composition CRD has exactly one value — `Pipeline`. `mode: Resources` is **removed from the schema**, not deprecated, so there is no such thing as a zero-function composition lab. And reading Crossplane's deployment builder at v2.3.4, the string `Resources` appears nowhere in `internal/controller/pkg/runtime/*`; the default `DeploymentRuntimeConfig` has an empty spec. So every function and provider pod lands **BestEffort, zero request, no limit** — the hazard class that ruled out Argo CD, now on pods you cannot avoid. **A `DeploymentRuntimeConfig` override is non-optional on this node**, and that makes it a teaching beat rather than a footnote: the platform you are building has a pod-sizing problem of its own.

**3. ESO does not drag a secret store in behind it.** The ticket assumed Vault or a cloud account was mandatory. ESO ships a `kubernetes` provider that reads from "either a remote cluster or **the local one where the operator runs in**", so the entire real mechanism — `SecretStore` + `ExternalSecret` + `refreshInterval` reconciliation + RBAC-scoped store access — is teachable for **zero additional pods**. The premise is refuted. (If you *did* install OpenBao: 2 pods, `resources: {}` on both, and a **10GiB PVC** — that is the thing that would have blown the budget, and it teaches Vault rather than ESO.)

**4. No chart registry is needed, ever.** `HelmChart.spec.sourceRef.kind` accepts `GitRepository` in source-controller's kubebuilder enum, and the API notes that for git sources "the chart version is ignored — the git revision *is* the version." So **a local bare git repo on the Proxmox host is a complete chart delivery path.** The twuni/Distribution chart, by contrast, ships `resources: {}` *and* `persistence.enabled: false` — a limit-free BestEffort pod that loses every chart you push on restart, or 10GiB to be non-lossy. It does not earn its RAM. If `oci://` mechanics are a hard objective, `docker run -p 5000:5000 registry:3.0.0` on the Proxmox host puts them outside the cluster's memory budget entirely.

**5. Backstage's disqualifier is the build, not the runtime.** Upstream scaffolds `NODE_OPTIONS: --max-old-space-size=8192` into every new app's CI workflow, and there is an issue reporting `yarn tsc` failing at ~4GB *with* that ceiling set. On 9.5GB minus a running cluster, that build cannot happen — not on the host, not in a Kaniko job, and no `--set` fixes it. The runtime figure, from Red Hat Developer Hub's shipped defaults (the only vendor that ships sizing for a living), is **1.25GiB requests / 3.5GiB limits across 2 pods** — 13% of the node reserved for one application. The official chart itself ships `resources: {}` on the Node backend, which is worse than Argo CD's case because a Node heap grows until something kills it.

---

## 3. Two curriculum decisions the numbers forced

**KRO is taught before Crossplane, not after.** The ticket framed KRO as "a lighter alternative — is it mature enough to be primary?" The answer to that question is no (§4), but the numbers suggest a better use for it than a footnote. KRO is 1 pod and 128Mi with **no packages, no providers, no functions, no revisions, no OCI protocol** — the learner sees "custom resource in, child resources out" with nothing in the way. Then Crossplane's extra machinery arrives with a reason to exist rather than as unexplained ceremony. Sequencing it second also means the `DeploymentRuntimeConfig` lesson from finding 2 lands as "here is what that machinery costs you", which is the phase's thesis in miniature.

**helm-controller's drift detection is OFF by default, and that becomes a lab beat rather than a correction.** The naive framing — "helm-controller makes a chart into desired state" — is only half right. `GetMode()` returns `DriftDetectionDisabled` when unset, so out of the box the controller re-runs Helm actions when *the desired state changes* and will not notice someone hand-editing a Deployment it installed. Only at `mode: enabled` does it server-side dry-run apply and correct. The lab writes itself: `kubectl scale` the deployment, watch nothing happen, turn on drift detection, `kubectl scale` again, watch it snap back. That single beat teaches the difference between *converging on change* and *converging continuously*, which is the distinction the whole phase is about.

---

## 4. Maturity, stated honestly

Three of P12's projects are not what a CNCF-tier reflex would predict, and the phase should say so out loud:

- **KRO has no CNCF tier of its own** — it is absent from `landscape.yml` entirely, inheriting Kubernetes' umbrella as a SIG Cloud Provider subproject. Applied against the test that rejected kube-rs, it **splits**: it passes governance decisively (Kubernetes SIG subproject, cross-vendor OWNERS spanning AWS, Google, Microsoft and Red Hat) and fails maturity decisively (v0.9.3, still `api/v1alpha1`, a README that warns "we may introduce breaking changes", and demonstrated churn including a **rename of its central CRD** from `ResourceGroup` to `ResourceGraphDefinition`). Contrast exercise, not primary vehicle — which is exactly the role §3 gives it.
- **vcluster is not a CNCF project.** It appears in the landscape as a directory listing with no `project:` field — a Loft Labs product with an Apache-2.0 core and a commercial edition. Visible consequences: two distros removed in seven minor versions, the per-tenant CoreDNS-embedding optimisation is a Pro feature, and **the chart's default image is the commercial `vcluster-pro` build**. That last one should be an explicit, discussed choice in the lab (`repository: loft-sh/vcluster-oss`), not a default the learner absorbs silently.
- **sealed-secrets is not in the CNCF landscape at any tier** — zero hits when grepping `landscape.yml`. Single-vendor governance, and Bitnami's 2025 registry withdrawal is a live demonstration of what that risks: the Backstage chart in the same research round pins `bitnamilegacy/postgresql` as an explicit workaround for it. It is nevertheless one of the most widely deployed secrets tools in Kubernetes, and the mechanism it teaches is portable even if the implementation is not.

Against those, **Crossplane graduated on 2025-10-28** — ten months ago as of this writing, which means any material written before late 2025 describes it as Incubating. Helm graduated 2020-05-01. Flagger inherits Flux's graduation rather than holding its own.

The pattern worth naming in the phase: **platform engineering's tooling is markedly less mature than the layers below it.** P8's CSI spec is a stable contract; P12's stack includes an alpha API, a vendor product, and a non-foundation controller. That is a fact about the field, not an accident of selection, and it is a better lesson than reciting tier badges.

---

## 5. Stale material, and the one gap that matters

**Three levers that older material will recommend and that no longer exist:**

1. **"Use k3s inside the vcluster because it's lighter."** k3s support was removed in vcluster v0.33; k0s in v0.26. There is exactly one distro now. Any material recommending the swap predates v0.33.
2. **Crossplane's `mode: Resources`** (native inline patch-and-transform). Gone from the CRD schema. Every composition needs a function pipeline.
3. **ESO requires an external secret store.** It does not — see finding 3.

**The gap that matters:** *observed idle RSS is unverified for every controller in both rounds*, and most consequentially for the **vcluster syncer pod** — a real `kube-apiserver` plus `kube-controller-manager` plus kine/SQLite in a single Go process. The two-tenant answer rests on its 256Mi *request*, while the chart's own default limit is **4Gi — sixteen times the request**, which tells you the authors do not expect 256Mi to be the working set. vcluster publishes no idle figure; its smallest published profile (1 CPU / 2GiB) is a KWOK synthetic-load *upper bound*, explicitly labelled as such.

Two consequences, both written into the lab rather than left as caveats:

- **Drop the vcluster memory limit from 4Gi to ~1Gi.** This is the single most important override in the phase. It converts an unbounded-growth risk into a clean OOMKill on one tenant pod — which is itself a good lesson, and a cheap one.
- **The first step of the multi-tenancy lab is `kubectl top pod -n vcluster-a`.** It takes thirty seconds and it measures the number the whole module rests on. If a single tenant idles above ~600Mi, drop to one tenant plus a written walkthrough of the second.

Similarly unverified and worth measuring rather than trusting: allocatable memory on the guest after OS, containerd and kubelet reservations (`kubectl describe node`), and the apiserver RSS cost of ESO's 1.9MB CRD bundle if ESO is ever installed.

There is also one **five-minute check worth running before building a lab on it**: `crossplane composition render` starts function runtimes as local **Docker** containers, which would let the composition mechanism be taught with no cluster at all. The code path is verified; whether it works against Docker or Podman on Debian 13 is not.

---

## 6. What P12 loses, and what replaces it

| Cut | Replaced by |
|---|---|
| **Backstage** | Flux + a CRD + a template repo as the golden path. Not a budget substitute — on the mechanism axis it is *strictly more* interesting, because Backstage's scaffolder is a one-shot linear task runner with no reconciliation loop, no drift detection and no desired-state comparison. Read about Backstage for catalog modelling and developer UX; the contrast with Flagger and Flux in the same phase is the lesson. |
| **In-cluster OCI registry** | A local bare git repo as a `GitRepository` chart source, and `docker run registry:3.0.0` on the Proxmox host if `oci://` mechanics are a hard objective. |
| **OpenBao / Vault** | ESO's `kubernetes` provider, if ESO earns a lab at all. If OpenBao belongs in the curriculum it belongs in its own module with its own justification, not smuggled in as a dependency. |
| **A cloud provider for Crossplane** | Nothing — Crossplane v2 composes native Kubernetes resources directly. |
| **vcluster's k3s distro** | Nothing available. One distro, and its cost is the number in Round A §3.1. |

Nothing in P12's scope is dropped for want of capacity. The one project that does not fit — Backstage — turns out to be the one whose mechanism payload was thinnest, which is a convenient result but not a manufactured one: the build ceiling and the scaffolder's lack of a control loop are independent findings.

---

*Below: the two research rounds in full, as produced, including their own `[UNVERIFIED]` inventories
and source indexes.*

---

# Round A — Crossplane, KRO, vcluster, Helm

Target node: single Proxmox host, ~9.5 GB spendable RAM, 6 cores (i5-8400T, 1 thread/core), 95 G disk.
Labs run one cluster at a time on Debian 13 guests. Module pair for multi-tenancy: 3072 MB control plane + 2048 MB worker.

**Method.** Every number below was read out of the project's own chart / manifest / Go source at a
pinned tag, fetched from GitHub. File paths and tags are cited inline. Where a component ships no
resource requests at all, that is stated as a hazard rather than smoothed over. Nothing is estimated;
gaps are marked `[UNVERIFIED]` and collected at the end.

Note on method limits: GitHub's unauthenticated API rate limit was exhausted partway through, and the
web-search budget for the session was exhausted. Everything after that point was obtained by shallow
`git clone` of the upstream repos (which is why some citations are repo-relative paths at a tag rather
than URLs) and by direct `WebFetch` of docs pages. No number below is second-hand from a blog post or
vendor marketing page.

---

## 1. Crossplane

**Version read: `v2.3.4`** (latest release at time of writing, published by the crossplane org).
Chart: `cluster/charts/crossplane/values.yaml` @ `v2.3.4`.

### 1.1 Core install — what actually gets scheduled

Two Deployments, one replica each. The webhook is **not** a separate pod: `webhooks.enabled: true`
(values.yaml:88-90) makes the *core crossplane pod* serve the webhook, backed by
`cluster/charts/crossplane/templates/service.yaml` + `secret.yaml`. There is no CRD conversion
webhook and no install Job.

| Component | Kind | Replicas | Memory request | Memory limit | CPU request | CPU limit | Source |
|---|---|---|---|---|---|---|---|
| `crossplane` (init container `core init`) | initContainer | — | 256Mi | 1024Mi | 100m | 500m | `templates/deployment.yaml:85-86` → `resourcesCrossplane` (values.yaml:122-133) |
| `crossplane` (container `core start`) | Deployment | 1 | **256Mi** | **1024Mi** | 100m | 500m | `templates/deployment.yaml:149-150` → `resourcesCrossplane` |
| `crossplane-rbac-manager` | Deployment | 1 | **256Mi** | **512Mi** | 100m | 100m | `resourcesRBACManager` (values.yaml:162-173); enabled by `rbacManager.deploy: true` (values.yaml:93-94) |

The init container and the main container share the same `resourcesCrossplane` block, so the pod's
effective memory request is `max(init, sum(containers))` = 256Mi, not 512Mi.

**Core totals: 2 pods, 512Mi requests, 1536Mi limits.**

The RBAC manager is **still a separate Deployment in v2.3.4** and is still on by default. It was not
merged into the core controller.

Two `emptyDir` caches are mounted on the crossplane pod: `packageCache` (`sizeLimit: 20Mi`) and
`functionCache` (`sizeLimit: 512Mi`). Both default to `medium: ""` — i.e. **disk, not RAM**
(values.yaml:144-160). Setting `medium: Memory` would put up to 532Mi on a `tmpfs` and charge it to
the node's memory; the values file explicitly recommends that only "for Crossplane development".
Leave both alone.

### 1.2 CRD count

**21 CRDs** in core Crossplane v2.3.4 (`cluster/crds/`, counted): 7 in `apiextensions.crossplane.io`
(CompositeResourceDefinition, Composition, CompositionRevision, EnvironmentConfig,
ManagedResourceDefinition, ManagedResourceActivationPolicy, Usage), 9 in `pkg.crossplane.io`
(Provider/ProviderRevision, Configuration/ConfigurationRevision, Function/FunctionRevision,
DeploymentRuntimeConfig, ImageConfig, Lock), 3 in `ops.crossplane.io` (Operation, CronOperation,
WatchOperation), 2 in `protection.crossplane.io` (Usage, ClusterUsage).

21 is modest — it is not in Argo-CD/Istio territory and should not meaningfully move apiserver memory
on a 3 GB control plane. The real CRD risk in Crossplane is *providers*: a cloud provider family
(provider-aws-ec2 and friends) installs hundreds. That risk does not apply here because, per §1.4,
this lab needs no cloud provider.

### 1.3 The composition model changed — functions are now mandatory

This is verified against the CRD schema, not against docs prose.

`cluster/crds/apiextensions.crossplane.io_compositions.yaml` @ `v2.3.4`, lines 79-89:

```yaml
              mode:
                default: Pipeline
                enum:
                - Pipeline
                type: string
```

and lines 269-270:

```yaml
            - message: an array of pipeline steps is required in Pipeline mode
              rule: self.mode == 'Pipeline' && has(self.pipeline)
```

The `mode` enum contains exactly one value. `mode: Resources` — native inline patch-and-transform —
**is gone from the API schema**, not merely deprecated. The v2.0.0 release notes list "Native patch and
transform within composition (`mode: Resources`)" under removed features, with
`crossplane beta convert pipeline-composition` offered as the migration.

Consequence for footprint: **every Composition requires at least one function, and each installed
`Function` package becomes its own Deployment.** The Crossplane docs state it plainly: "Installing a
Function creates a function pod. Crossplane sends requests to this pod to ask it what resources to
create" (docs.crossplane.io/latest/composition/compositions/). Crossplane talks to it over gRPC.

**Function and provider pods ship with no resource requests at all.** I read the deployment builder
directly. In `internal/controller/pkg/runtime/` @ `v2.3.4` — `runtime.go`, `runtime_function.go`,
`runtime_provider.go`, `runtime_defaults.go`, and `runtime_override_options.go` — the string
`Resources` **does not appear once**. `functionDeploymentOverrides()` (`runtime_function.go:186-218`)
sets ports, env, and image, and `DeploymentWithOptionalReplicas(1)` (`runtime.go:214`) sets one
replica; nothing sets `corev1.ResourceRequirements`. `internal/initializer/deployment_runtime_config.go`
creates a `DeploymentRuntimeConfig` named `default` with an **empty spec** (line 41).

So every function pod and every provider pod lands as **`resources: {}` — BestEffort QoS, zero request,
no limit.** This is the same class of hazard that ruled out Argo CD in the earlier round, and here it
applies to the pods you cannot avoid installing. On a 2–3 GB guest a BestEffort pod is the first thing
the kubelet evicts under pressure and, having no limit, is also free to be the thing that *causes*
the pressure. Mitigation is a `DeploymentRuntimeConfig` — see the verdict.

| Function (current release) | Pods | Memory request | Memory limit |
|---|---|---|---|
| `function-patch-and-transform` v0.10.9 | 1 | **none** (`resources: {}`) | none |
| `function-go-templating` v0.12.3 | 1 | **none** | none |
| `function-auto-ready` v0.7.0 | 1 | **none** | none |

Actual RSS of a function pod: `[UNVERIFIED]`.

### 1.4 Is a provider needed at all? No.

**This is the decisive finding for the lab's feasibility, and the answer is better than the ticket
assumed.** Crossplane v2.0.0's headline change (verified from the v2.0.0 release notes):

> "Compositions can now include any Kubernetes resource, e.g. `Deployment`, `Configmap`, `Secret`,
> custom resources - anything from the Kubernetes API, not just Crossplane-defined resources."

In Crossplane v1 you needed `provider-kubernetes` to have a Composition create a native `Deployment`
or `ConfigMap`. In v2 you do not. An XRD + Composition whose pipeline emits native Kubernetes objects
works with **core Crossplane plus one function pod and no provider whatsoever**. No cloud account, no
credentials, no provider CRDs.

If you nonetheless want the provider (e.g. to teach the managed-resource/`Object` model, or to show
`ProviderConfig`):

- `provider-kubernetes` **v1.3.0** — needs no cloud credentials. `examples/cluster/provider/config-in-cluster.yaml`
  @ `v1.3.0` is three lines: `spec.credentials.source: InjectedIdentity`. It uses its own
  ServiceAccount against the local apiserver. `examples/cluster/provider/provider-in-cluster.yaml`
  binds that SA to `cluster-admin`.
- Cost: **1 pod, `resources: {}`** (its own `examples/deploymentruntimeconfig.yaml` sets no resources
  either), plus **9 CRDs** (`package/crds/`: `Object`, `ObservedObjectCollection`, `ProviderConfig`,
  `ProviderConfigUsage` in both `kubernetes.crossplane.io` and the v2 namespaced
  `kubernetes.m.crossplane.io` group, plus `ClusterProviderConfig`).
- Observed RSS: `[UNVERIFIED]`.

### 1.5 The zero-footprint alternative worth knowing about

The Crossplane v2 CLI is a separate repo (`crossplane/cli`, read at `main` @ 2026-08-14) and it has a
GA local renderer: `cmd/crossplane/composition/composition.go:29` registers `Render`, and
`cmd/crossplane/main.go:91` keeps `crossplane render` as a hidden top-level alias with the comment
"Hidden top-level alias for render, since it's GA but has moved."

`cmd/crossplane/render/render.go` starts each function as a **local Docker container**
(`StartFunctionRuntimes`, `RewriteAddressesForDocker` rewriting `localhost` to
`host.docker.internal`, `AnnotationKeyRuntimeDockerNetwork`). So an XRD + Composition can be
authored, rendered, and iterated on **with no Kubernetes cluster and no in-cluster Crossplane at all**,
on a Debian guest with Docker. That makes it possible to teach the *composition mechanism* at zero
cluster cost and then install Crossplane only for the "it reconciles, it self-heals" half of the lesson.

### 1.6 CNCF maturity

**Graduated, 2025-10-28.** From `cncf/landscape` `landscape.yml` (repo read at 2026-08-14),
lines 4214-4229: `project: graduated`, `accepted: '2020-06-25'`, `incubating: '2021-09-14'`,
`graduated: '2025-10-28'`. Graduation is the CNCF's top tier and requires committer diversity, a
security audit (Crossplane has two Ada Logics audits, 2023-03-23 and 2023-07-27), and demonstrated
production adoption — for a curriculum this means Crossplane is a safe thing to teach as
industry-standard rather than as a bet. Graduation is also very recent (ten months ago), so material
written before late 2025 will describe it as Incubating.

### 1.7 Verdict — **install-minimised**

The composition lab fits, and it fits without a cloud account. Budget **3 pods** for the minimum viable
lab (crossplane, crossplane-rbac-manager, one function) — not the 2 pods the docs' "default pods" page
implies.

Overrides to apply:

```yaml
# helm install crossplane crossplane-stable/crossplane -n crossplane-system --create-namespace -f this
rbacManager:
  deploy: false            # -1 pod, -256Mi request; safe in a single-admin lab where you are cluster-admin.
                           # Cost: XRD-derived aggregated ClusterRoles are no longer auto-created,
                           # so a non-admin "app team" persona in the lab would need hand-written RBAC.
resourcesCrossplane:
  requests: { cpu: 100m, memory: 192Mi }
  limits:   { cpu: 500m, memory: 512Mi }
packageCache:
  medium: ""               # leave on disk (default) — do NOT set Memory
functionCache:
  medium: ""               # leave on disk (default) — 512Mi sizeLimit would otherwise be RAM
```

And — non-optional on this node — pin the function pods, because they ship unbounded:

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: default            # Crossplane creates this name with an empty spec; overwrite it
spec:
  deploymentTemplate:
    spec:
      selector: {}
      template:
        spec:
          containers:
            - name: package-runtime
              resources:
                requests: { cpu: 25m, memory: 64Mi }
                limits:   { cpu: 250m, memory: 256Mi }
```

Use exactly **one** function (`function-patch-and-transform`) rather than the common
`function-go-templating` + `function-auto-ready` pair; that is one pod instead of two. Skip
`provider-kubernetes` entirely unless the managed-resource model is itself a learning objective.

Resulting budget: 3 pods, ~256Mi + 64Mi = **320Mi requests / 768Mi limits**, 21 CRDs. That is
comfortable even on the 3072 MB control plane.

---

## 2. KRO (kube-resource-orchestrator)

**Version read: `v0.9.3`** (latest release). Repo is **`kubernetes-sigs/kro`** — it moved out of
`awslabs`. Chart: `helm/values.yaml` @ `v0.9.3`.

### 2.1 Footprint

One Deployment, one container, one replica. **No webhook, no init container, no Job, no sidecar** —
verified by reading `helm/templates/` @ `v0.9.3`, which contains only `deployment.yaml`,
`cluster-role.yaml`, `cluster-role-binding.yaml`, `serviceaccount.yaml`, `metrics-service.yaml`,
`pprof-service.yaml`, `servicemonitor.yaml`, `_helpers.tpl`. `helm/templates/deployment.yaml` has a
single container (line 34-35) and no `initContainers`.

| Component | Kind | Replicas | Memory request | Memory limit | CPU request | CPU limit | Source |
|---|---|---|---|---|---|---|---|
| `kro` controller | Deployment | 1 | **128Mi** | 1024Mi | **256m** | 1000m | `helm/values.yaml:73-79` (`deployment.resources`) |

**Total: 1 pod, 128Mi request, 1024Mi limit.** That is a quarter of Crossplane's core request and
genuinely is the lighter option — the "lighter alternative" positioning survives contact with the
chart, which is not always the case.

Two footnotes worth flagging. The **CPU request of 256m** is odd — larger than Crossplane's 100m, and
on a 6-core box that is 4% of the machine reserved for an idle controller; harmless but worth trimming.
And `rbac.mode` defaults to **`unrestricted`** — "Grants cluster-wide full access to all resources"
(values.yaml:38-48), with the file itself noting "Recommended setting is aggregation, but unrestricted
remains the default for backwards compatibility." Set `rbac.mode: aggregation` in the lab; it costs
nothing and it is a teachable moment about default-permissive operators.

### 2.2 CRD count

**2 static CRDs**: `kro.run_resourcegraphdefinitions.yaml` (27 KB) and
`internal.kro.run_graphrevisions.yaml` (30 KB), both in `helm/crds/` @ `v0.9.3`.

But the count is *dynamic*: **kro generates one new CRD per ResourceGraphDefinition you apply.** From
`README.md` @ `v0.9.3`: "When a ResourceGraphDefinition is applied to the cluster, the kro controller
verifies its specification, then dynamically creates a new CRD and registers it with the API server."
So a teaching cluster with five RGDs has seven CRDs. Still small, but the growth is user-driven rather
than fixed, and each registration triggers an apiserver discovery/OpenAPI rebuild.

### 2.3 Mechanism — same family as Crossplane, different implementation

Same *category*: composition-as-controller. You declare an abstraction, the cluster gains a real CRD
for it, and a controller reconciles instances of that CRD into child objects. A learner who
understands a Crossplane XRD+Composition understands a kro ResourceGraphDefinition.

Three differences that matter, and the first is a footprint difference:

1. **Per-abstraction controllers run in-process, not as pods.** README: "kro then deploys a dedicated
   controller to respond to instance events on the CRD. This microcontroller is responsible for
   managing the lifecycle of resources defined in the ResourceGraphDefinition." Reading
   `pkg/dynamiccontroller/dynamic_controller.go` and `watch_manager.go` @ `v0.9.3`, these
   "microcontrollers" are goroutines and watches inside the single kro pod — not Deployments. This is
   the exact inverse of Crossplane, where every function is a pod. Cheaper, but it means every
   abstraction's informer cache lives inside one container with a 1024Mi limit, so memory growth is
   concentrated and OOM takes out *all* your abstractions at once. Tunables exist
   (`KRO_DYNAMIC_CONTROLLER_DEFAULT_RESYNC_PERIOD` defaults to 36000s, `KRO_CLIENT_QPS`,
   `dynamicControllerConcurrentReconciles: 1`).
2. **CEL expressions instead of a function pipeline.** kro has no package manager, no OCI packages,
   no gRPC function protocol, no `DeploymentRuntimeConfig`. Dependency ordering is inferred from the
   expression graph rather than declared.
3. **No managed-resource concept.** Crossplane's `Provider`/managed-resource machinery — reconciling
   an *external* system and drift-correcting it — has no kro equivalent. kro composes Kubernetes
   objects; to reach a cloud you compose *another operator's* CRs (ACK, ASO, Config Connector). For an
   in-cluster-only lab that distinction is invisible, which is precisely why it is worth stating out
   loud rather than letting learners infer equivalence.

### 2.4 Maturity — apply the kube-rs test

| Test | kro | Verdict |
|---|---|---|
| Hit 1.0? | No. **v0.9.3**; 28 tags from v0.1.0 to v0.9.3 | Fail |
| API stability | **`api/v1alpha1`** — still alpha. Both `api/v1alpha1/resourcegraphdefinition_types.go` and `api/internal.kro.run/v1alpha1/` @ `v0.9.3` | Fail |
| Explicit stability promise? | README FAQ #5: "kro's API is currently at `v1alpha1`. As kro evolves, **we may introduce breaking changes** to improve the API." | Fail |
| Breaking changes in practice | The core CRD was renamed from `ResourceGroup` to `ResourceGraphDefinition`, and a second CRD (`GraphRevision`) was added between v0.8.x and v0.9.0 (`internal.kro.run_graphrevisions.yaml` first appears in the v0.9.0 docs snapshot). Rough minor-version cadence with schema churn — the versioned docs tree shows the RGD CRD growing from 13.8 KB at v0.7.0 to 27.2 KB at v0.9.3 | Fail |
| Foundation / governance | **Pass, and this is where it differs from kube-rs.** `README.md:9`: "kro is a subproject of Kubernetes SIG Cloud Provider." `OWNERS` @ `v0.9.3` lists approvers `sig-cloud-provider-leads` + `kro-maintainers`; `OWNERS_ALIASES` shows genuinely cross-vendor maintainership — `a-hilaly`, `jlbutler` (AWS/ACK lineage), `barney-s`, `cheftako` (Google), `matthchr` (Azure Service Operator), `bridgetkromhout` (Microsoft), `jakobmoellerdev` (Red Hat), plus reviewers `michaelhtm`, `n3wscott`. Kubernetes-project governance, k8s Slack `#kro`, biweekly public community meeting with recorded minutes | **Pass** |
| Own CNCF maturity tier | **None.** kro does not appear in `cncf/landscape` `landscape.yml` at all (grepped the full 1.1 MB file; the only hit for "kro" is an unrelated mention inside another project's description). It inherits Kubernetes' CNCF-Graduated umbrella as a SIG subproject but carries **no independent tier** | n/a |

**Direct answer: contrast exercise, not the primary teaching vehicle.** kro splits the kube-rs test —
it passes the governance half decisively (a Kubernetes SIG subproject with AWS + Google + Microsoft +
Red Hat maintainers is a much stronger signal than kube-rs had) but fails the maturity half just as
decisively (pre-1.0, `v1alpha1`, a written warning of breaking changes, and demonstrated schema churn
including a rename of its central CRD). Teaching it as the primary vehicle means the curriculum's
worked examples break on a minor bump; teaching Crossplane (Graduated, `v2`, stable API) as primary
and kro as a 30-minute "here is the same idea in a quarter of the RAM and a fifth of the concepts"
contrast is the right split.

### 2.5 Verdict — **install** (as a contrast exercise)

128Mi/1 pod is cheap enough that it can coexist with anything. It is arguably the *better* first
exposure to composition-as-controller precisely because it strips away packages, providers, functions,
and revisions — the learner sees "custom resource in, child resources out" with nothing in the way, and
then Crossplane's extra machinery has a reason to exist.

```yaml
rbac:
  mode: aggregation          # not the default; default is cluster-wide full access
deployment:
  resources:
    requests: { cpu: 50m, memory: 128Mi }
    limits:   { cpu: 500m, memory: 512Mi }
```

---

## 3. vcluster

**Version read: `v0.36.1`** (latest release). Chart: `chart/values.yaml` @ `v0.36.1` (1337 lines).
Docs cross-checked against `loft-sh/vcluster-docs` @ `main` (2026-08-14).

### 3.1 What one virtual cluster actually costs

Everything except CoreDNS is **one container in one pod**. From
`vcluster-docs/vcluster/introduction/architecture.mdx`:

> "All of these components run together in a single container within a StatefulSet pod. The API server,
> controller manager, data store, and syncer are one unified process. CoreDNS deploys as a separate pod
> in the same namespace."

and the doc gives the literal expected output:

```
NAME                                 READY   STATUS    AGE
vcluster-0                           1/1     Running   5m
vcluster-coredns-6b9f8d6f6b-xk2p9    1/1     Running   5m
```

I confirmed this against `chart/templates/statefulset.yaml` @ `v0.36.1`: line 132-133 declares
`containers:` with exactly one entry, `- name: syncer`; line 128-129 pulls in
`vcluster.k8s.initContainers`, which (per `chart/templates/_init-containers.tpl`) is a single
short-lived container named `kubernetes` that does nothing but `cp -r /kubernetes/. /binaries/`.

| Component | Kind | Memory request | Memory limit | CPU request | Other | Source |
|---|---|---|---|---|---|---|
| init container `kubernetes` (binary copy, then exits) | initContainer | 64Mi | 256Mi | 40m | — | `values.yaml:339-345` (`controlPlane.distro.k8s.resources`) |
| `vcluster-0` container `syncer` = kube-apiserver + kube-controller-manager + kine/SQLite + syncer | StatefulSet | **256Mi** | **4Gi** | 200m | ephemeral-storage req 1Gi / limit 10Gi | `values.yaml:654-664` (`controlPlane.statefulSet.resources`) |
| `vcluster-coredns` | Deployment (created *inside* the vcluster, synced out as a real host pod) | **64Mi** | **170Mi** | 20m | 1 replica | `values.yaml:548-556` (`controlPlane.coredns.deployment.resources`); `coredns.enabled: true` at values.yaml:508-509 |
| `data` PVC | volumeClaimTemplate | — | — | — | **5Gi** | `values.yaml:695-700`; enabled via `auto` — see §3.3 |

**Per virtual cluster: 2 running pods, 320Mi memory requests, 220m CPU requests, 4.17Gi memory
limits, 5Gi disk.**

No scheduler process. `controlPlane.distro.k8s.scheduler.enabled: false` (values.yaml:328-329), and the
architecture doc explains why: "By default, vCluster reuses the Control Plane Cluster's scheduler to
reduce resource usage." Enabling the virtual scheduler adds a process inside the same container.

**No hidden policy objects.** `policies.resourceQuota.enabled` and `policies.limitRange.enabled` are
both `auto` (values.yaml:1149, 1177-1178). Reading `chart/templates/limitrange.yaml:1` and
`chart/templates/resourcequota.yaml:1`, each renders only when the *other* one is literally `"true"` —
so with both left at `auto`, **neither object is created**. This matters: the LimitRange's
`defaultRequest` is `memory: 128Mi, cpu: 100m, ephemeral-storage: 3Gi`, which would otherwise be
stamped onto every tenant workload pod and inflate scheduling on a 2048 MB worker. Do not turn either
on in this lab.

**No addon pods in the default mode.** `deploy.localPathProvisioner.enabled: true`,
`deploy.cni.flannel.enabled: true`, and `deploy.kubeProxy.enabled: true` look alarming
(values.yaml:924-955) but belong to *private-nodes* mode; `privateNodes.enabled: false` is the default
(values.yaml:870), and `vcluster-docs/vcluster/configure/vcluster-yaml/deploy.mdx:30` tags the CNI
section `<TenancySupport privateNodes="true" />`. All `integrations.*` are `false`. `deploy.metricsServer`
is `false`.

### 3.2 Backing store: **embedded SQLite**, and this is verified from the template logic

`chart/templates/_backingstore.tpl` @ `v0.36.1` counts how many backing stores are enabled and then:

```
{{- else if or (eq $backingStores 0) .Values.controlPlane.backingStore.database.embedded.enabled -}}
{{- true -}}
```

Every one of the five backing-store options in `values.yaml` is `enabled: false`
(`database.embedded`, `database.external`, `etcd.embedded`, `etcd.external`, `etcd.deploy`), so
`$backingStores == 0` and the embedded-database branch is taken. The values file says so in its own
comment at line 348: "If not defined will use embedded database as a default backing store," and line
351-353 identifies it: "Embedded defines that an embedded database (**sqlite**) should be used."
The architecture doc agrees: "A **data store**, which stores all API resources. By default, an embedded
SQLite database is used."

**So: SQLite via kine, in-process, in the same container. Not etcd.** This is the cheap case, and it
is the current default — I checked, it has not flipped. Every etcd flavour is opt-in:

- `backingStore.etcd.embedded.enabled: true` → etcd raft inside the same container (no extra pod, but
  a real etcd write path and fsync cost).
- `backingStore.etcd.deploy.enabled: true` → **an extra StatefulSet pod**, image `registry.k8s.io/etcd:3.6.8-0`,
  requests `cpu: 20m, memory: 150Mi` and **no memory limit at all** (values.yaml:439-443 sets only
  `requests`), plus its own **5Gi** PVC (values.yaml:461-467). Avoid on this node — a request-only,
  limit-free etcd next to a 2 GB budget is exactly the wrong shape.

### 3.3 Distro: k8s only. k3s and k0s are both gone.

`values.yaml` @ `v0.36.1` contains **no `k3s:` or `k0s:` key at all** — only
`controlPlane.distro.k8s` (values.yaml:296-345), image `ghcr.io/loft-sh/kubernetes:v1.36.0`. I bisected
the chart across tags to date the removals, and the docs confirm both in one sentence
(`vcluster-docs/vcluster/configure/vcluster-yaml/control-plane/README.mdx:12`):

> "Kubernetes (K8s) is the only supported distribution. **K0s** support was removed in vCluster `v0.26`
> and **K3s** support was removed in `v0.33`."

My chart bisection matches exactly: `k0s:` present through v0.25.0, absent from v0.26.0; `k3s:` present
through v0.32.0, absent from v0.33.0.
`vcluster-docs/vcluster/manage/upgrade/distro-migration.mdx:18-20` adds the migration caution.

**Consequence for the curriculum: "use k3s inside the vcluster because it's lighter" is no longer an
available lever.** Any lab material or blog post recommending it predates v0.33 and will not apply.
There is exactly one distro and its cost is the numbers in §3.1. On the plus side, "what's inside the
virtual control plane" is now a simpler thing to teach.

Also worth knowing before you write the install command: the **default image is the commercial build**.
`controlPlane.statefulSet.image.repository: "loft-sh/vcluster-pro"`, and the values comment says "It
defaults to the vCluster pro repository that includes the optional pro modules that are turned off by
default. If you still want to use the pure OSS build, set the repository to `loft-sh/vcluster-oss`."
For a teaching lab that should be an explicit, discussed choice rather than a default the learner
absorbs silently.

### 3.4 Mechanism claim: confirmed. The pods are real host pods.

The curriculum's claim — a vcluster's pods are real pods on the host cluster, synced by the syncer, so
the learner can put the fake apiserver and the real pods side by side — is exactly what the docs
describe. From `vcluster-docs/vcluster/_fragments/how-does-syncing-work.mdx`:

> "Since a tenant cluster lacks actual worker nodes and its own network, syncing is the process by which
> vCluster replicates resources between the tenant cluster and the Control Plane Cluster. This
> capability is handled by a component called the **syncer**... By default, vCluster only syncs low-level
> resources, such as **pods**, secrets, configmaps, or services."

> "If the resource is being asked to sync from the tenant cluster to the Control Plane Cluster, vCluster
> copies the resources from the tenant cluster and sends it to the Control Plane Cluster to be created."

And the translation is visible and teachable — the same fragment documents it precisely:

- **Name rewritten** to `NAME-x-NAMESPACE-x-VCLUSTER_NAME`
- **Namespace rewritten** to the namespace where the vcluster control plane lives
- **Labels/annotations added**, prefixed `vcluster.loft.sh/` — `object-host-name`, `object-namespace`,
  `object-uid`, `managed-by: vcluster`
- **References rewritten** (service names, secret names) to match the rewritten names

`architecture.mdx` adds: "A syncer component translates workload resources from each tenant cluster into
a dedicated namespace on the underlying cluster. Each tenant sees only their own namespaces, pods, and
services. The translated copies are invisible to them." And: "All resources synchronized to the Control
Plane Cluster namespace carry owner references back to the tenant cluster."

This is a genuinely excellent lab: `kubectl --context=vcluster get pod` shows `nginx`, and
`kubectl --context=host -n vcluster-a get pod` shows `nginx-x-default-x-vcluster-a` with
`vcluster.loft.sh/managed-by: vcluster`. Two views of one pod. The abstraction is inspectable rather
than asserted.

### 3.5 How many fit on a 3072 MB / 2048 MB pair?

**Scheduling arithmetic (definitive).** 320Mi memory + 220m CPU requests per vcluster.

Rough allocatable on a Debian 13 guest running kubelet + containerd, after OS and kubelet reservations:
~2.4–2.6 GB on the 3072 MB node and ~1.4–1.6 GB on the 2048 MB node
(`[UNVERIFIED]` — depends on your kubelet `--system-reserved`/`--kube-reserved` and whether the CP node
also runs the apiserver in-cluster; measure with `kubectl describe node`). Against that:

| vclusters | Memory requests | CPU requests | Pods | PVCs |
|---|---|---|---|---|
| 1 | 320Mi | 220m | 2 | 5Gi |
| **2** | **640Mi** | **440m** | **4** | **10Gi** |
| 3 | 960Mi | 660m | 6 | 15Gi |
| 4 | 1280Mi | 880m | 8 | 20Gi |

**Two fits with room to spare, and that is the answer the multi-tenancy module needs.** Three fits on
requests. Four fits on requests but I would not promise it.

**The honest caveat, and it is the one that matters.** 256Mi is a *scheduling* number. The thing behind
it is a real `kube-apiserver` plus a real `kube-controller-manager` plus kine in one Go process, and
that combination does not idle at 256Mi. The default limit is **4Gi**, sixteen times the request — the
chart authors clearly do not expect 256Mi to be the working set. Two vclusters at their default limits
could each claim 4Gi on a node that has 2.5Gi. **Actual idle RSS of a `v0.36.1` vcluster syncer pod:
`[UNVERIFIED]`** — vcluster publishes no idle-footprint figure, and its
`vcluster/deploy/control-plane/sizing-and-performance.mdx` starts at a "Dev / sandbox" profile of
**1 CPU / 2 GiB limits** (P1), which is a synthetic-load ceiling under KWOK fake nodes, not an idle
measurement (the doc is explicit that "the load is simulated, not real" and results are "an upper
bound").

So the operational answer is: **two tenants, with the limits pulled down so that overcommit fails
loudly instead of taking the node with it.**

### 3.6 CNCF maturity

**Not a CNCF project.** vcluster appears in `cncf/landscape` `landscape.yml` at lines 9278-9287 as a
plain entry — `name`, `description`, `homepage_url`, `repo_url`, `logo`, `crunchbase` — with **no
`project:` field and no `extra.accepted`/`incubating`/`graduated` dates.** Compare Crossplane
(`project: graduated`, line 4216) and Helm (`project: graduated`, line 7487) in the same file. Landscape
inclusion is a directory listing, not a maturity tier; vcluster is a Loft Labs product with an
Apache-2.0 core and a commercial edition.

What that implies for adoption: no CNCF-neutral governance, no CNCF security audit, and a roadmap set
by one vendor with a paid tier — visible right here in the removal of two distros in seven minor
versions, in the CoreDNS-embedded-in-control-plane optimisation being a Pro feature
(`architecture.mdx:186`: "With vCluster Pro, CoreDNS can be embedded directly into the control plane
pod, reducing the per-tenant footprint"), and in the default image being `vcluster-pro`. For a
curriculum this is fine — it is the de-facto standard for virtual clusters and the mechanism it teaches
(syncer-based tenancy) is real and transferable — but it should be labelled as vendor OSS, not as a
foundation project, and material more than a year old should be treated as suspect.

### 3.7 Verdict — **install-minimised.** Two tenants, and the mechanism lab is worth it.

This is the cheapest of the three per unit of insight, and it is not close. One virtual Kubernetes
control plane for 320Mi of requests and 2 pods, backed by SQLite, with the syncer's translation visible
from the host side — a multi-tenancy module built on this is real, not theory.

```yaml
# vcluster.yaml — per tenant
controlPlane:
  statefulSet:
    image:
      repository: loft-sh/vcluster-oss   # default is the commercial vcluster-pro build
    resources:
      requests: { cpu: 150m, memory: 256Mi }
      limits:   { memory: 1Gi, ephemeral-storage: 4Gi }   # default limit is 4Gi mem / 10Gi ephemeral
    persistence:
      volumeClaim:
        size: 2Gi                        # default 5Gi; ×2 tenants on a 95G disk
  coredns:
    deployment:
      resources:
        requests: { cpu: 20m, memory: 64Mi }
        limits:   { cpu: 200m, memory: 170Mi }
  # leave backingStore entirely unset -> embedded SQLite (do NOT enable etcd.deploy)
  # leave distro.k8s.scheduler.enabled: false -> reuse the host scheduler
policies:
  resourceQuota: { enabled: false }      # explicit; "auto" already yields nothing, but be explicit
  limitRange:    { enabled: false }
```

Sequencing notes for the lab:

- Put both vcluster **control planes on the 3072 MB node** (untaint it) and let tenant workloads land on
  the 2048 MB worker. Two apiservers on a 2 GB guest is the configuration most likely to fail.
- Dropping the memory limit from 4Gi to 1Gi is the single most important override. It converts an
  unbounded-growth risk into a clean OOMKill on one tenant pod — which is itself a good lesson.
- **First lab step should be `kubectl top pod -n vcluster-a`.** The idle RSS is the one number I could
  not verify, it is the number the whole module rests on, and measuring it takes thirty seconds. If a
  single tenant idles above ~600Mi, drop to one tenant plus a written walkthrough of the second.
- Do not enable the virtual scheduler, embedded/deployed etcd, LimitRange, ResourceQuota, or
  `deploy.metricsServer`. Each is a real addition and none is needed to teach the syncer.

---

## 4. Helm as a platform-engineering abstraction layer

Scoped as instructed: no chart-authoring or templating-syntax material here. Sources are Helm
**v3.19.0** (checked out and read), Flux **flux2 @ main (2026-08-07)** / **helm-controller v1.6.3** /
**source-controller v1.9.4**, and the **twuni/docker-registry** chart **v3.0.0**.

### 4.1 Zero in-cluster footprint — confirmed

**Zero pods, zero CRDs, zero controllers.** Helm 3 is a client. `grep -rli tiller cmd/ pkg/` at
`v3.19.0` returns only unrelated hits in test fixtures and `pkg/repo/index.go` — there is no server
component in the tree. Rendering happens in the CLI process: `pkg/action/install.go:305` builds render
values and line 317 calls `i.cfg.renderResources(...)` locally, then the result is applied through a
client-go client built from the local kubeconfig.

**State: Secrets, in the release namespace.** `pkg/action/action.go:386-390` — the driver switch's
default arm is `case "secret", "secrets", "":` → `driver.NewSecrets(...)`. So with `HELM_DRIVER` unset
you get Secrets (ConfigMaps, SQL, and in-memory are the alternatives).
`pkg/storage/storage.go:35` defines `HelmStorageType = "sh.helm.release.v1"`;
`pkg/storage/driver/secrets.go:254` stamps `Type: "helm.sh/release.v1"`. The Secret name is
`sh.helm.release.v1.<release>.v<revision>` and the payload is the gzipped, base64'd release object —
which includes the fully rendered manifest, so a Secret's size scales with your chart's output.

**One Secret per revision, capped at 10.** `pkg/cli/environment.go:43`:

```go
// defaultMaxHistory sets the maximum number of releases to 0: unlimited
const defaultMaxHistory = 10
```

(The comment is stale — the value is 10, not 0.) It is wired in at line 97 as
`MaxHistory: envIntOr("HELM_MAX_HISTORY", defaultMaxHistory)` and exposed as `--history-max` on both
`upgrade` (`cmd/helm/upgrade.go:275`) and `rollback` (`cmd/helm/rollback.go:87`).

So: **history accumulates, but bounded at 10 Secrets per release**, not unbounded. A release upgraded
40 times keeps 10. On a 95 G disk and a small etcd this is real but minor — ten Secrets each holding a
gzipped copy of a rendered manifest, so tens to low hundreds of KB per release. If you want it smaller,
`--history-max 3` or `export HELM_MAX_HISTORY=3` in the lab profile. Worth showing learners
`kubectl get secret -l owner=helm` once: "your release history is just objects in your cluster" lands
better as a demonstration than as a sentence.

### 4.2 Getting charts into an isolated cluster

| Option | Pods | Memory request | Disk | Verdict |
|---|---|---|---|---|
| **Local chart directory** (`helm install ./chart`) | **0** | **0** | 0 beyond the git working copy | Confirmed zero cost. **Use this.** |
| **Flux `GitRepository` → `HelmChart` → `HelmRelease`** | 0 *additional* (reuses source-controller + helm-controller you already have) | 0 additional | git clone + tarball in source-controller's cache | **Use this for the GitOps lab.** No registry needed. |
| **In-cluster OCI registry** (twuni/docker-registry 3.0.0 = Distribution 3.0) | **1** | **none — `resources: {}`** | 0 by default (emptyDir); **10Gi** if you enable the PVC | **Does not earn its RAM.** Skip. |

**Local directory: confirmed zero.** `helm install ./chart` renders in-process and applies via the API.
Nothing is installed. The only cluster-side artefact is the release Secret from §4.1.

**Flux from git: the registry is unnecessary, and this is verified from the API schema.**
`source-controller` **v1.9.4**, `api/v1/helmchart_types.go:100-116`:

```go
type LocalHelmChartSourceReference struct {
	// Kind of the referent, valid values are ('HelmRepository', 'GitRepository',
	// 'Bucket').
	// +kubebuilder:validation:Enum=HelmRepository;GitRepository;Bucket
	Kind string `json:"kind"`
```

`GitRepository` is a first-class `HelmChart` source. source-controller clones the git repo, packages
the chart directory into a tarball, and serves it as an Artifact; helm-controller installs from that.
Line 38-39 confirms the semantics: "Version is the chart version semver expression, **ignored for
charts from GitRepository and Bucket sources**" — i.e. the git revision *is* the version. So on an
isolated homelab with no external network path, **a git repo (even a local bare repo on the Proxmox
host) is a complete chart delivery mechanism**. There is no registry in that path at all.

**In-cluster OCI registry: real footprint, and the hazard is the familiar one.** Helm 3 does speak OCI
natively, so this works — but from `twuni/docker-registry.helm` @ v3.0.0 (`Chart.yaml`: `version: 3.0.0`,
`appVersion: 3.0.0`, image `registry:3.0.0`):

- `values.yaml:4` — `replicaCount: 1`. One Deployment, one container
  (`templates/deployment.yaml`); no sidecar, no init container.
- `values.yaml:58` — **`resources: {}`**, with the boilerplate comment "We usually recommend not to
  specify default resources... This also increases chances charts run on environments with little
  resources, such as Minikube." Zero request, no limit, BestEffort QoS. Same hazard class as the
  Crossplane function pods and as Argo CD in the earlier round.
- `values.yaml:69-73` — `persistence.enabled: false`, `size: 10Gi`. **The default is an emptyDir**, so
  every chart you push is lost when the pod restarts. Making it useful means a 10Gi PVC.
- Idle RSS of `registry:3.0.0`: `[UNVERIFIED]`.

**Recommendation: local chart directory for authoring labs, Flux-from-git for the GitOps/delivery lab,
no in-cluster registry.** The registry buys one thing the git path does not — teaching `helm push` /
`oci://` mechanics — and it costs a limit-free BestEffort pod plus 10Gi to be non-lossy. On a node
where RAM is the binding constraint, that trade is bad. If OCI-registry mechanics are a hard learning
objective, do them against a `docker run -p 5000:5000 registry:3.0.0` on the Proxmox host, outside the
cluster's memory budget entirely.

### 4.3 Flux `helm-controller`

**Cross-check with the earlier Flux round, not a new finding.** flux2 pins helm-controller **v1.6.3**
(`manifests/bases/helm-controller/kustomization.yaml`). From
`helm-controller` v1.6.3 `config/manager/deployment.yaml:62-68`:

| Component | Memory request | Memory limit | CPU request | CPU limit |
|---|---|---|---|---|
| `helm-controller` | **64Mi** | **1Gi** | 100m | 1000m |

flux2's `manifests/bases/helm-controller/patch.yaml` does **not** touch resources; it adds
`--events-addr`, the ServiceAccount, `priorityClassName: system-cluster-critical`, and
`GOMEMLIMIT` sourced from `limits.memory`. That last one is worth noting on a small node: Go's soft
memory limit is set to **1Gi**, so the runtime will happily let the heap grow toward 1Gi before GC'ing
aggressively. If you shrink the limit, GOMEMLIMIT follows automatically — which is the right behaviour,
but it means the limit is doing double duty as a GC tuning knob.

**Included in a default bootstrap: yes.** flux2 `pkg/manifestgen/install/options.go:46`:

```go
Components: []string{"source-controller", "kustomize-controller", "helm-controller", "notification-controller"},
```

helm-controller is one of the four defaults; the `image-reflector-controller` and
`image-automation-controller` are the opt-in extras. So if Flux is already installed in the curriculum,
helm-controller is **already running and already paid for** — the incremental cost of the
Helm-as-desired-state lab is zero pods.

**Mechanism — and one correction to the framing.** The reconciliation-loop framing is right:
`docs/spec/v2/helmreleases.md:1235-1239` — "`.spec.interval` is a required field that specifies the
interval at which the HelmRelease is reconciled, i.e. the controller ensures the current Helm release
matches the desired state." And the header: "The `HelmRelease` API allows for controller-driven
reconciliation of Helm releases via Helm actions such as install, upgrade, test, uninstall, and
rollback. In addition to this, it detects and corrects cluster state drift from the desired release
state."

But **drift correction is off by default**, and the curriculum should not claim otherwise.
`api/v2/helmrelease_types.go:334-341`:

```go
// GetMode returns the DiffMode set on the Diff, or DiffModeDisabled if not set.
func (d DriftDetection) GetMode() DriftDetectionMode {
	if d.Mode == "" {
		return DriftDetectionDisabled
	}
	return d.Mode
}
```

`docs/spec/v2/helmreleases.md:838-861` fills in the behaviour: only when
`.spec.driftDetection.mode` is `warn` or `enabled` does the controller "compare the manifest from the
Helm storage with the current state of the cluster using a **server-side dry-run apply**"; only at
`enabled` will it "attempt to correct the drift by creating and patching the resources based on the
server-side dry-run apply result."

So out of the box, helm-controller re-runs Helm actions when *the desired state changes* (chart version,
values), and it does **not** notice someone hand-editing a Deployment it installed. To get the
self-healing behaviour the lab wants to demonstrate you must set `spec.driftDetection.mode: enabled`
explicitly. That is a good lab beat in itself — `kubectl scale` the deployment, watch nothing happen,
turn on drift detection, `kubectl scale` again, watch it snap back.

### 4.4 Helm vs Crossplane compositions vs KRO — the mechanism difference

A chart is **a function from values to text, evaluated on the operator's laptop.** `helm install`
renders templates locally (`pkg/action/install.go:317`), applies the resulting manifest, and writes a
gzipped copy of that manifest into a Secret (§4.1). The abstraction — "a WebApp with a database and an
ingress" — exists in the chart's `values.yaml` schema, in the author's head, and in the release Secret's
frozen output. **It does not exist in the cluster's API.** A Composition or a kro
ResourceGraphDefinition inverts this: applying it **registers a new CRD**, and applying an instance of
that CRD hands control to **a controller that runs forever**, converging children toward the parent's
spec. The concrete consequences:

- **Drift.** With Helm, nothing is watching. `kubectl edit` a chart-installed Deployment and the change
  simply persists; Helm learns about it at the next `helm upgrade`, and then only via a three-way merge
  against the stored manifest. With a Composition or an RGD, the controller's next reconcile
  overwrites the edit — self-healing is the default posture, not a feature. Flux's helm-controller can
  buy Helm most of this back, but only with `driftDetection.mode: enabled` (§4.3), and it is bolted on
  from outside rather than intrinsic.
- **Is there a live API object for the abstraction?** Helm: no. `kubectl get webapp` returns
  `error: the server doesn't have a resource type "webapp"`. The nearest thing is
  `helm list` — a CLI query over Secrets, not an API resource. Crossplane/kro: yes.
  `kubectl get webapp my-app -o yaml` returns a real object with a real spec, real `status.conditions`,
  and real events. Everything that consumes the Kubernetes API — RBAC, admission control, `kubectl
  wait`, watches, ArgoCD/Flux, an operator, a dashboard — can see and act on the abstraction. This is
  the single largest difference and the reason platform teams reach past Helm.
- **Who can self-service it.** Helm requires the consumer to hold the *union* of every permission the
  chart's output needs, plus a Helm binary, plus registry/repo access, plus the values file. The blast
  radius of "let the app team install this chart" is the whole chart. Crossplane/kro require exactly
  one RBAC grant: `create` on `webapps`. The controller holds the powerful permissions; the consumer
  holds a narrow one. A namespaced XR or RGD instance is a delegation boundary — the platform team
  ships an API and keeps the credentials. Helm has no equivalent, which is precisely why
  `helm install` tends to stay in the platform team's hands and Backstage-style portals end up
  wrapping it in CI.
- **What each can express.** Helm can do anything a template can: conditionals, loops, arbitrary text
  manipulation, lookups, hooks with weights and ordering, subchart composition. What it *cannot* do is
  anything that depends on state that does not exist yet — you cannot template in the ID of a resource
  the cluster has not created, wait for it, and use the result, because rendering happens once, before
  anything is applied. Composition-as-controller inverts exactly this: Crossplane's function pipeline
  gets the observed state of already-created children on each reconcile, so a child can consume
  another child's `status`, and kro infers ordering from the CEL expression graph for the same reason.
  Multi-step provisioning with real dependencies is the thing Helm structurally cannot express and
  compositions exist to express. Conversely, compositions are worse at raw text-shaping: Crossplane
  needs a `function-go-templating` pod to do what a chart does natively, and kro is limited to CEL.
- **Failure surface.** A Helm failure is a CLI exit code in whoever ran it — ephemeral, invisible to
  the cluster. A composition failure is `status.conditions` on a named object plus Kubernetes events —
  alertable, queryable, and visible to the consumer who asked for it.

The one-line version for the curriculum: **Helm packages *what to create*; a Composition or RGD
publishes *an API for asking* — and an API has a controller behind it, a status, and an RBAC verb.**
That is why Helm remains the right tool for shipping the platform's own components (§4.2 —
including the controllers above) and the wrong tool for exposing the platform's abstractions to its
users.

### 4.5 CNCF maturity

**Graduated, 2020-05-01.** `cncf/landscape` `landscape.yml` lines 7485-7496: `project: graduated`,
`accepted: '2018-06-01'`, `incubating: '2018-06-01'`, `graduated: '2020-05-01'`. (Accepted directly at
Incubating, graduated two years later. Cure53/Trail of Bits security audit 2019-04-19, Ada Logics
fuzzing audit 2023-03-31.)

---

## 5. Summary table

| | Crossplane v2.3.4 | KRO v0.9.3 | vcluster v0.36.1 (per tenant) | Helm v3.19.0 |
|---|---|---|---|---|
| Pods, minimum viable lab | **3** (core + rbac-manager + 1 function) | **1** | **2** (syncer + coredns) | **0** |
| Memory requests, chart default | 512Mi core + 0 (function `resources: {}`) | 128Mi | 320Mi | 0 |
| Memory requests, minimised | ~320Mi | 128Mi | 320Mi | 0 |
| Memory limits, chart default | 1536Mi core + unbounded functions | 1024Mi | 4.17Gi | — |
| Memory limits, minimised | 768Mi | 512Mi | ~1.17Gi | — |
| CRDs | 21 (+9 if provider-kubernetes) | 2 static + 1 per RGD | 0 on host | 0 |
| `resources: {}` hazard | **Yes** — all function and provider pods | No | No | Registry option: yes |
| Disk | emptyDir caches only | none | 5Gi PVC (→2Gi) | ≤10 Secrets/release |
| CNCF tier | **Graduated 2025-10-28** | **None** (k8s SIG subproject) | **Not a CNCF project** | **Graduated 2020-05-01** |
| Verdict | install-minimised | install (contrast only) | install-minimised, **2 tenants** | install (free) |

Running all four simultaneously at minimised settings: ~320 + 128 + 640 (two vclusters) = **~1.1 GB of
requests**, well inside the ceiling. The constraint is not the sum of requests — it is the unbounded
limits, which is why every override above pins one.

---

## 6. `[UNVERIFIED]` items, collected

Each of these is a gap I could not close from a primary source, not an estimate.

1. **Observed idle RSS of the Crossplane core controller pod** at v2.3.4. Request is 256Mi, limit
   1024Mi; the actual working set is unmeasured. Crossplane publishes no figure
   (docs.crossplane.io/latest/guides/pods/ lists the two pods and gives no resource guidance).
2. **Observed idle RSS of a Crossplane function pod** (`function-patch-and-transform` v0.10.9,
   `function-go-templating` v0.12.3, `function-auto-ready` v0.7.0). They ship `resources: {}`, so there
   is not even a request to anchor against.
3. **Observed idle RSS of the `provider-kubernetes` v1.3.0 pod.** Also `resources: {}`.
4. **Observed idle RSS of the KRO controller** at v0.9.3, and how it grows per registered
   ResourceGraphDefinition (each adds informers/watches inside the one 1024Mi-limited container).
5. **Observed idle RSS of a vcluster v0.36.1 syncer pod** — apiserver + controller-manager +
   kine/SQLite + syncer in one process. **This is the most important gap in the document**, because the
   two-tenant answer in §3.5 rests on requests (320Mi) while the chart's own limit (4Gi) implies the
   authors expect far more. vcluster publishes no idle number; its smallest published profile
   (1 CPU / 2 GiB) is a synthetic-load *ceiling* measured with KWOK fake nodes, explicitly labelled
   "an upper bound," not an idle measurement. **Measure with `kubectl top pod` as the first step of the
   lab.**
6. **Allocatable memory on the 3072 MB and 2048 MB Debian 13 guests** after OS + containerd + kubelet
   reservations. I used ~2.4–2.6 GB and ~1.4–1.6 GB as working figures; these depend on your kubelet
   `--system-reserved` / `--kube-reserved` and on whether the control-plane node also runs the apiserver
   in-cluster. Confirm with `kubectl describe node`.
7. **Observed idle RSS of `registry:3.0.0`** (Distribution 3.0) in the twuni chart. Ships
   `resources: {}`. Moot if you follow the recommendation to skip the in-cluster registry.
8. **Exact release dates** for Crossplane v2.0.0, vcluster v0.26.0 / v0.33.0, and the KRO tag history.
   The GitHub API rate limit was exhausted before I could pull `published_at` for these. The *content*
   claims that depend on them are all independently verified from files (the v0.26/v0.33 distro removals
   from `control-plane/README.mdx:12` and from chart bisection across tags; the v2.0.0 removals from the
   release-notes page) — only the calendar dates are missing.
9. **Whether the KRO project has a published API-graduation plan or target for `v1beta1`/`v1`.** The
   README commits to "clear migration paths, deprecation notices" but names no version or date; I found
   no roadmap document in the repo at `v0.9.3`.
10. **Date KRO moved from `awslabs/kro` to `kubernetes-sigs/kro`.** The repo's `created_at` is
    2024-09-12 and it is unambiguously under `kubernetes-sigs` now with SIG Cloud Provider OWNERS, but I
    could not date the transfer without the API.
11. **Whether `crossplane composition render` needs a container runtime that is available on the lab
    guests.** The code path is verified (it starts function runtimes as Docker containers, rewriting
    addresses to `host.docker.internal`), but whether it works against Podman or rootless Docker on
    Debian 13 is untested. Worth a five-minute check before building a lab around it, because if it
    works it is the zero-footprint option.

---

# Round B — Flagger, Backstage, the secrets trio

Node budget: **~9.5 GB spendable RAM, 6 cores (i5-8400T, 1 thread/core), 95 G disk.** One cluster at a time, Debian 13 guests. Curriculum already installs **Istio**, **Prometheus**, and **Flux** in earlier phases.

Method: every default number below was read out of the actual chart `values.yaml` / template / install manifest in the upstream repo at a named tag, fetched via the GitHub contents API. Observed-consumption numbers are labelled `observed-not-default` and sourced to specific issues. CNCF tiers come from `cncf/landscape` `landscape.yml` on `main` (the authoritative machine-readable source), not from marketing pages.

> **Tooling caveat for this round:** the WebSearch budget for the session was exhausted before I could look for community blog-post measurements. All numbers here come from repo files, GitHub issue bodies, GHCR registry manifests, and `landscape.yml`. Where that left a gap, the item is listed as `[UNVERIFIED]` rather than estimated. See the final section.

---

## 1. Flagger

**Read at:** `fluxcd/flagger` **v1.44.0** (chart `version: 1.44.0`, `appVersion: 1.44.0`).

### Components and memory

| Component | Pods | Requests (mem/cpu) | Limits (mem/cpu) | Source |
|---|---|---|---|---|
| Flagger controller | 1 | **32Mi** / 10m | **512Mi** / 1000m | `charts/flagger/values.yaml` L147–153; `templates/deployment.yaml` L22 (`replicas: {{ .Values.leaderElection.replicaCount }}`, default `1`) |
| flagger-loadtester | 1 | **64Mi** / 10m | **none** ⚠️ | `charts/loadtester/values.yaml` L31–34, `replicaCount: 1` (chart 0.38.0, image `ghcr.io/fluxcd/flagger-loadtester:0.38.0`) |
| podinfo demo (primary) | 2 | 64Mi / 100m each = **128Mi** | 512Mi / 2000m each = 1Gi | `kustomize/podinfo/deployment.yaml` L70–76; `hpa.yaml` `minReplicas: 2`, `maxReplicas: 4` |
| podinfo demo (canary, only during a run) | +2 | +**128Mi** | +1Gi | same; Flagger scales the green deployment up for the analysis window |
| *(optional)* bundled Prometheus | 1 | 128Mi / 10m | **none** ⚠️ | `templates/prometheus.yaml`; gated on `prometheus.install`, **default `false`** (`values.yaml` L170–181) |

### Totals

- **Steady state (idle, reusing existing Prometheus + Istio): 224Mi of requests across 4 pods.**
- **During a canary run: 352Mi of requests across 6 pods.**
- Worst case if everything pinned its limit: ~2.5Gi (dominated by podinfo's 512Mi × 4, which idles nowhere near that). The controller itself is capped at 512Mi.
- CRDs: `charts/flagger/crds/crd.yaml` = **66,573 bytes**. Note `crd.create: false` in values — the chart expects CRDs applied separately.

**Hazards:** the loadtester and the *optional* bundled Prometheus both ship **requests but no limits**. Neither is a `resources: {}` case — the controller itself is fully specified, which is unusually well-behaved. The bundled Prometheus also pins a stale image (`docker.io/prom/prometheus:v2.41.0`) and uses an `emptyDir` with `retention: 2h`.

### Service mesh dependency — **CONFIRMED with a nuance, and it favours the curriculum**

Verbatim from `docs/gitbook/usage/deployment-strategies.md` @ v1.44.0:

> * **Canary Release** (progressive traffic shifting) — Istio, Linkerd, App Mesh, NGINX, Skipper, Contour, Gloo Edge, Traefik, Kuma, Gateway API, Apache APISIX, Knative
> * **A/B Testing** (HTTP headers and cookies traffic routing) — Istio, App Mesh, NGINX, Contour, Gloo Edge, Gateway API
> * **Blue/Green** (traffic switching) — **Kubernetes CNI**, Istio, Linkerd, App Mesh, NGINX, Contour, Gloo Edge, Gateway API
> * **Blue/Green Mirroring** (traffic shadowing) — Istio, Gateway API
> * **Canary Release with Session Affinity** — Istio, Gateway API
>
> "For Canary releases and A/B testing you'll need a Layer 7 traffic management solution like a service mesh or an ingress controller. **For Blue/Green deployments no service mesh or ingress controller is required.**"

So:

1. **Progressive traffic shifting — the interesting mechanism — does require an L7 provider.** It cannot be done with plain Kubernetes Services.
2. **Istio is a first-class provider and the only one that supports all five strategies.** The curriculum's existing Istio is directly reusable; Flagger needs **no stack of its own**. `meshProvider: ""` in values, set to `istio`.
3. **There is a genuine no-mesh mode:** `spec.provider: kubernetes` (`meshProvider=kubernetes`), Blue/Green via L4 service switching. Confirmed by `docs/gitbook/tutorials/kubernetes-blue-green.md`: "For applications that are not deployed on a service mesh, Flagger can orchestrate Blue/Green style deployments with Kubernetes L4 networking." This is a useful fallback lab if Istio is torn down, but it teaches switching rather than shifting.

### Metrics — reuses existing Prometheus

- `metricsServer: "http://prometheus:9090"` (`values.yaml` L24) — points at an existing Prometheus by default.
- `prometheus.install: false` — it *can* ship its own (see table) but does not by default.
- `docs/gitbook/usage/metrics.md`: "Flagger comes with two builtin metric checks: HTTP request success rate and duration… The builtin checks are available for every service mesh / ingress controller and are **implemented with Prometheus queries**." Custom checks via `MetricTemplate` can target Datadog, CloudWatch, New Relic, Graphite etc.
- **Prometheus is effectively required for metric-driven analysis, and the curriculum's existing instance satisfies it.** Install with `--set metricsServer=http://prometheus.<ns>:9090` and leave `prometheus.install=false`.
- Note for the mesh-free lab: the tutorial's built-in checks work off the app's own `http_request_duration_seconds` histogram scraped by Prometheus, not mesh telemetry — so the no-mesh path still needs Prometheus, just not Istio.

### Maintainership and relationship to Flux

- `MAINTAINERS` @ v1.44.0: **Sanskar Jaiswal** (Independent), **Stefan Prodan** (ControlPlane — also a core Flux maintainer), **Takeshi Yoneda** (Tetrate). Originally a Weaveworks project; Weaveworks is gone and the project did not go with it.
- Lives in the Flux org: `github.com/fluxcd/flagger`.
- **Flagger and Flux are independent at runtime.** Flagger is its own controller with its own CRDs (`Canary`, `MetricTemplate`, `AlertProvider`); it neither requires Flux nor is required by it. The relationship is governance: `landscape.yml` records Flagger with `parent_project: Flux` and **no independent maturity key**, i.e. it is a Flux subproject and inherits Flux's tier. For the curriculum that is a plus — same governance, same maintainer, same Slack, and the GitOps engine you already run is the natural way to deliver `Canary` objects.

### CNCF maturity

**Graduated (inherited, as a Flux subproject).** Flux: accepted to Sandbox **2019-07-15**, Incubating **2021-03-12**, **Graduated 2022-11-30** (most recent tier change) — `landscape.yml`, Flux entry. Flagger itself carries `parent_project: Flux` and no separate tier. *Implication:* Graduated is the CNCF's top tier — sustained multi-vendor maintainership, completed security audits, documented governance and adopters. This is as low-risk as open-source infrastructure adoption gets; Flagger's inheritance is slightly softer than a standalone graduation but it shares Flux's maintainer bench and release machinery.

### Verdict — **INSTALL**

224Mi of requests at idle, 352Mi during a canary run, hard-capped controller at 512Mi. That is ~2–4% of the node for the single best mechanism-per-MB item in this whole round: a real reconciliation loop that reads metrics, makes a promote/rollback decision, and manipulates traffic weights. It reuses Istio and Prometheus, both already installed, and needs nothing of its own. Install with:

```
--set metricsServer=http://prometheus.<ns>:9090   # reuse existing Prometheus
--set meshProvider=istio                          # reuse existing Istio
--set prometheus.install=false                    # default, but be explicit
```

and put a limit on the loadtester (`--set resources.limits.memory=128Mi`) to close the unbounded-pod hazard. Optionally cap podinfo's limits down from 512Mi — nothing in the lab needs that headroom.

---

## 2. Backstage

**Read at:** `backstage/charts` tag **`backstage-2.10.0`** (chart `version: 2.10.0`), plus `backstage/backstage` `main`, plus `redhat-developer/rhdh-chart` `main`.

### What the official chart actually ships

| Component | Pods | Requests (mem/cpu) | Limits (mem/cpu) | Source |
|---|---|---|---|---|
| Backstage backend | 1 (`replicas: 1`, L130) | **`resources: {}` — NONE** 🚨 | **NONE** 🚨 | `charts/backstage/values.yaml` L238 |
| PostgreSQL (subchart, **`enabled: false`** by default) | 1 when enabled | 256Mi / 250m | **`limits: {}` — none** ⚠️ | dep `bitnami/postgresql` **12.10.0**; `bitnami/charts@postgresql/12.10.0` `values.yaml` L446–450 |

**Flag it explicitly:** the Backstage container ships `resources: {}` — **no requests and no limits at all**. This is the same class of finding that decided against Argo CD in the earlier round, and it is worse here, because unlike a Go controller this is a Node.js process whose heap will grow until something kills it. The scheduler will happily place it as a best-effort pod on a node with 200Mi free and then the kubelet will evict something.

The chart's own commented-out suggestion (added by `backstage/charts#27`, whose author says "Looked over my local developer deployment that has a number of added plugins… Set memory fairly high comparatively"):

```yaml
# resources:
#   limits:
#     memory: 1Gi
#     cpu: 1000m
#   requests:
#     memory: 250Mi
#     cpu: 100m
```

### Database

- **The chart does bundle PostgreSQL — as an optional subchart that is OFF by default.** `Chart.yaml`: `- condition: postgresql.enabled, name: postgresql, repository: oci://registry-1.docker.io/bitnamicharts, version: 12.10.0`. `values.yaml` L479: `enabled: false`. `templates/backstage-deployment.yaml` L159–171 only injects `POSTGRES_HOST/PORT/USER/PASSWORD` `{{- if .Values.postgresql.enabled }}`. A bare `helm install` therefore gives you a Backstage pod with **no database configured**.
- Bitnami postgresql 12.10.0 defaults: `architecture: standalone`, image `postgresql:15.4.0-debian-11-r10`, `persistence.size: 8Gi`, primary requests 256Mi/250m, **no limits**.
- Operational hazard: chart 2.10.0 overrides the DB image to `docker.io/bitnamilegacy/postgresql` (L484) as an explicit workaround for `bitnami/charts#35164` — Bitnami's 2025 registry withdrawal. You are pulling from a legacy-tagged mirror.
- **SQLite is possible but explicitly dev-only.** Verbatim from `packages/create-app/templates/default-app/app-config.yaml.hbs` L122–126:
  ```yaml
    # This is for local development only, it is not recommended to use this in production
    # The production database configuration is stored in app-config.production.yaml
    database:
      client: better-sqlite3
      connection: ':memory:'
  ```
  `:memory:` means the entire catalog is rebuilt from scratch on every restart. It removes the Postgres pod but does not remove the memory problem — it moves the catalog *into* the Node heap.

### Real footprint — what the only vendor shipping defaults actually sets

Red Hat Developer Hub is a productised Backstage distribution. `redhat-developer/rhdh-chart` `charts/backstage/values.yaml` (`main`) — these are shipped defaults, not marketing:

| RHDH component | Requests | Limits |
|---|---|---|
| Backstage backend container | **1Gi** / 250m | **2.5Gi** / 1000m + `ephemeral-storage: 5Gi` |
| `install-dynamic-plugins` **initContainer** | 256Mi / 250m | 2.5Gi / 1000m + `ephemeral-storage: 5Gi` |
| PostgreSQL primary (`postgresql.enabled: true`) | 256Mi / 250m | 1024Mi / 250m, `persistence.size: 1Gi` |
| **Total** | **≈1.25 Gi requests, 2 pods** | **≈3.5 Gi limits** |

A vendor that ships Backstage for a living requests **1 GiB for the backend alone** and allows it 2.5 GiB. That is the most credible sizing figure available and it is a default, not a guess.

### Observed consumption — `observed-not-default`

All of these are OOM-tail heap sizes (a ceiling, not a baseline) — labelled as such:

- `backstage/backstage#26776` (2024-09-18): backend reached **~4.24 GB** heap (`Mark-sweep 4237.2 (4453.9) MB`) then `FATAL ERROR: Reached heap limit`.
- `#6485` (2021-07-15): backend at **~4.08 GB** heap OOM after enabling the LDAP org reader.
- `#27700` (2024-11-18): operator set `--max-old-space-size=524` and `--max-semi-space-size=8` and *still* saw monotonic growth to the container limit and crash. Also documents needing `NODE_OPTIONS=--no-node-snapshot` for the scaffolder on Node 20 — i.e. the scaffolder specifically fights the Node runtime.
- `#27347` TechDocs memory leak; `#23047` OOM collating TechDocs for search; `#20385` OOM on certain search queries. Memory pressure is a recurring, multi-year, multi-subsystem theme, not a one-off.

### **Build cost — this is the disqualifying factor**

Backstage is not `helm install` and done. `backstage.io/docs/deployment/docker` gives two paths, both requiring a full `yarn install` plus a build: a **host build** (recommended: `yarn install`, `yarn tsc`, `yarn build:backend`, then package) or a **multi-stage Docker build** (all three stages inside Docker, "typically slower"). Base image `node:24-trixie-slim`; `package.json.hbs` `engines: { node: "22 || 24" }`.

The decisive number is one that upstream **scaffolds into every new Backstage app**. `packages/create-app/templates/default-app/.github/workflows/ci.yml`:

```yaml
    runs-on: ubuntu-latest
    env:
      CI: true
      NODE_OPTIONS: --max-old-space-size=8192
```

…covering `yarn install --immutable`, `yarn backstage-cli repo lint`, `yarn tsc:full`, `yarn backstage-cli repo test`, `yarn build:all`, and `yarn build-image`. **The project's own default for building a freshly scaffolded app is an 8 GB V8 heap ceiling on a 16 GB runner.** (`backstage/backstage` `.github/workflows/ci.yml` sets the same 8192 for the monorepo.)

And the ceiling is not theoretical headroom: `#21982` (2023-12-22) reports `yarn tsc` on a real app hitting the limit at **~4.07 GB** and **still failing with `--max-old-space-size=8192` set**.

**On a node with 9.5 GB spendable total, running a Kubernetes control plane, Istio, Prometheus and Flux, a build that upstream expects to be allowed 8 GB of heap and is observed to peak above 4 GB cannot happen.** Not in-cluster, not on the host, not in a Kaniko job. There is no `--set` that fixes this.

### Disk

- `ghcr.io/backstage/backstage:latest` (the chart's default image) **exists** — GHCR amd64 manifest `sha256:0e0dd79a…`, 17 layers, **333 MB compressed**. But this is the project's **demo/example app**: no integrations, no auth provider, no templates of your own. Useful for a screenshot, useless as the golden path the curriculum wants.
- Upstream chart with bundled Postgres: **8Gi PVC** by default (RHDH sets 1Gi).
- RHDH sets `ephemeral-storage: 5Gi` limits on both the backend and its init container — a signal about how much scratch space a real Backstage churns through.

### CNCF maturity

**Incubating.** Accepted to Sandbox **2020-09-08**; promoted to **Incubating 2022-03-15** (most recent tier change — over four years ago as of Aug 2026, with no graduation). Security audit 2022-08-23. `landscape.yml`, Backstage entry. *Implication:* Incubating means CNCF-verified real production adopters and healthy contribution, but no graduation-level review of governance, security posture, or long-term maintainer diversity — and Backstage's practical adoption story is that most organisations run a fork they build and maintain themselves, which is exactly the cost profile Incubating fails to warn you about.

### Is the Software Templates / scaffolder mechanism interesting? **No — it is templating plus sequential API calls.**

From `backstage.io/docs/features/software-templates/`: the scaffolder gives you "the ability to load skeletons of code, template in some variables, and then publish the template to some locations like GitHub or GitLab." A template is a list of **steps with inputs**. Each execution is a **one-shot linear task with a unique ID**, cancellable mid-flight. Built-in actions are `fetch:template`, `publish:github`, `catalog:register`. **There is no reconciliation loop, no desired-state comparison, no drift detection, no self-healing.** It runs once, top to bottom, and then it is done.

This is the crux, and it settles the question: the mechanism the curriculum is *about* — declarative desired state plus a controller that continuously reconciles toward it — is precisely the mechanism the scaffolder **does not have**. Flux + a CRD + a template repo does not merely approximate Backstage's golden path; on the mechanism axis it is strictly *more* interesting, because it has the control loop that Backstage's scaffolder lacks. Backstage's real teaching payload is catalog modelling (entity kinds, relations, ownership) and developer UX — both valuable, neither mechanistic, and both readable from documentation without spending a gigabyte.

### Verdict — **READ, DON'T INSTALL. The curriculum's stated default is confirmed, and the numbers are not close.**

Plainly: **Backstage does not fit, and the disqualifier is the build, not the runtime.**

- **Runtime, if you could magic up an image:** the honest figure is RHDH's, **~1.25 GiB of requests and ~3.5 GiB of limits across 2 pods** — **13% of the node reserved and 37% of the node allowed**, for one application, on a box that also has to run a Kubernetes control plane, Istio, Prometheus and Flux. The absolute floor using the chart's own commented suggestion plus bundled Postgres is ~506Mi of requests, but that floor is fiction: the container ships `resources: {}`, real deployments are observed hitting 4 GB+ heaps, and the 250Mi request buys you nothing but a best-effort pod that gets OOM-killed.
- **Build:** upstream ships `--max-old-space-size=8192` as the default for building a scaffolded app, and real builds are observed failing even at that ceiling. **9.5 GB total, minus a running cluster, cannot host it.** Cross-building elsewhere and pushing an image is possible in principle but means the lab's central artefact is produced off-node, which defeats the point of a homelab module and adds a registry to the curriculum.
- **Payload:** the one mechanism you would be buying — the scaffolder — is a linear task runner, not a controller. Flux + a CRD + a template repo teaches strictly more mechanism for zero additional RAM.

Read about it. Spend the paragraph on catalog modelling and on why the scaffolder is *not* a control loop — the contrast with Flagger and Flux in the same phase is itself the lesson.

---

## 3. Secrets management: SOPS / sealed-secrets / External Secrets Operator

### 3a. SOPS

**Read at:** `getsops/sops` (latest release **v3.13.3**); `fluxcd/kustomize-controller` **v1.9.4**; `fluxcd/flux2` **v2.9.4**.

| Component | Pods | Requests | Limits |
|---|---|---|---|
| `sops` CLI | **0** | **0** | **0** |
| In-cluster decryption | **0 additional** — runs inside the already-running Flux `kustomize-controller` | 0 additional | 0 additional |
| *(context)* `kustomize-controller` you already run | (1, pre-existing) | 64Mi / 100m | 1Gi / 1000m |

**Is it purely a CLI with zero in-cluster footprint? YES — verified structurally.** The `getsops/sops` repo root at `main` contains **no Helm chart, no `deploy/`, no `manifests/`, no Kubernetes YAML of any kind**. It has `cmd/` (the CLI) plus provider packages (`age`, `pgp`, `kms`, `azkv`, `gcpkms`, `hcvault`, `hckms`) and a `keyservice` gRPC package. (`keyservice` *can* be run as a daemon for remote key operations, but SOPS ships no Kubernetes manifests for it and nothing in the Flux path needs it.)

**Flux native SOPS support — CONFIRMED.** `fluxcd/kustomize-controller` `docs/spec/v1/kustomizations.md`, section **`### Decryption`**, verbatim:

> "In order to store Secrets safely in Git repositories you can use an encryption provider and the optional field `.spec.decryption` to configure decryption for Secrets that are a part of the Kustomization.
>
> **The only supported encryption provider is [SOPS](https://getsops.io/).** With SOPS you can encrypt your secrets with [age](https://github.com/FiloSottile/age) or [OpenPGP](https://www.openpgp.org) keys, or with keys from Key Management Services (KMS), like AWS KMS, Azure Key Vault, GCP KMS or OpenBao/Vault."

Decryption happens **inside the kustomize-controller process** that Flux already runs (defaults per `kustomize-controller.deployment.yaml` v1.9.4: requests 100m/64Mi, limits 1000m/1Gi). No sidecar, no webhook, no extra Deployment, no CRD.

**In a cluster that already runs Flux, SOPS costs literally nothing.** Zero pods, zero MiB of requests, zero CRDs, zero additional images pulled. Local cost: one static Go binary on the workstation and an `age` keypair.

**CNCF maturity: Sandbox.** Accepted **2023-05-17** (donated by Mozilla; `landscape.yml` SOPS entry — `project: sandbox`, no `incubating` key, so no tier change since acceptance). *Implication:* Sandbox is the entry tier — no CNCF review of governance, adopters, or security beyond basic hygiene. In SOPS's case the risk profile is unusually benign for a Sandbox project: it is a mature, widely-deployed CLI with a decade of history and a *Graduated* project (Flux) depending on it natively, so Flux's own maintenance interest underwrites it.

---

### 3b. sealed-secrets (Bitnami)

**Read at:** `bitnami/sealed-secrets` (repo has **moved** from `bitnami-labs/sealed-secrets`) tag **v0.38.4**; chart `version: 2.19.0`, `appVersion: 0.38.1`.

| Component | Pods | Requests | Limits |
|---|---|---|---|
| sealed-secrets controller | **1** (`templates/deployment.yaml` L16 `replicas: 1`, one container) | **`requests: {}` — NONE** 🚨 | **`limits: {}` — NONE** 🚨 |

`helm/sealed-secrets/values.yaml` L191–193, verbatim:
```yaml
resources:
  limits: {}
  requests: {}
```

**Flag it: no requests, no limits.** Milder than Backstage — this is a single small Go controller, not a Node.js app — but it is still a best-effort pod. Worth teaching *as* a hazard.

Nice detail that makes the fix effective: `templates/deployment.yaml` L167–177 derives **`GOMAXPROCS` from `resources.limits.cpu`** and **`GOMEMLIMIT` from `resources.limits.memory`**. Setting a limit does not just cap the cgroup; it tells the Go runtime to garbage-collect against it. Overriding resources here is genuinely load-bearing.

**Complete pod inventory: 1.** No webhook, no cert-controller, no init containers, no sidecars, no Jobs. Templates directory contains only RBAC, service, optional ingress/PDB/networkpolicy/servicemonitor/prometheusrule/dashboards. **1 CRD, 6,659 bytes** (`crds/bitnami.com_sealedsecrets.yaml`) — the smallest CRD footprint of anything in this round.

**Mechanism worth teaching — yes, and it is a real one:** the controller generates an RSA keypair at startup and **keeps the private key in-cluster, never leaving it**; `kubeseal` fetches only the public certificate and encrypts **client-side**, so the operator never handles the decryption key; the resulting `SealedSecret` CR is safe to commit to a public repo; and the controller runs a **genuine reconciliation loop** turning `SealedSecret` → `Secret`, with key renewal/rotation over time. Asymmetric crypto, a controller with a secret of its own, client-side encryption, and a control loop — for one pod and one 6.7 KB CRD.

**CNCF maturity: not a CNCF project.** Grepping `landscape.yml` for `sealed`/`Sealed` returns **zero hits** — it is not in the CNCF landscape at any tier. Maintained by Bitnami (repo now `bitnami/sealed-secrets`, not archived). *Implication:* single-vendor governance with no foundation-level neutrality, adopter verification, or security-audit requirement, and Bitnami's 2025 registry withdrawal is a live demonstration of single-vendor supply-chain risk (see the `bitnamilegacy/` workaround in the Backstage chart above). It is nevertheless one of the most widely deployed secrets tools in Kubernetes, and the mechanism it teaches is portable even if the implementation is not.

---

### 3c. External Secrets Operator

**Read at:** `external-secrets/external-secrets` tag **v2.9.0** (`values.yaml` read at that tag; note that tag's `Chart.yaml` declares `version: "2.8.0" / appVersion: "v2.8.0"` while `main` declares `2.9.0 / v2.9.0` — see UNVERIFIED #13).

| Component | Pods | Requests | Limits | Source |
|---|---|---|---|---|
| Main controller | **1** (`replicaCount: 1` L36) | **`resources: {}` — NONE** 🚨 | **NONE** 🚨 | `values.yaml` L287 |
| Webhook (`webhook.create: true` L495) | **1** (`replicaCount: 1` L500) | **`resources: {}` — NONE** 🚨 | **NONE** 🚨 | `values.yaml` L744 |
| cert-controller (`certController.create: true` L764) | **1** (`replicaCount: 1` L767) | **`resources: {}` — NONE** 🚨 | **NONE** 🚨 | `values.yaml` L956 |
| **Total** | **3 pods** | **0Mi requested** | **unbounded** | |

**Flag it, three times over.** Confirmed by `templates/`, which contains `deployment.yaml`, `webhook-deployment.yaml`, and `cert-controller-deployment.yaml` — three separate Deployments, all defaulting to `resources: {}`. Upstream's own commented-out suggestion, identical at all three sites:
```yaml
  # requests:
  #   cpu: 10m
  #   memory: 32Mi
```
So the maintainers' own view is ~32Mi each, ~96Mi for the trio — but nothing enforces it and nothing caps it.

**CRD weight is the hidden cost.** `installCRDs: true` by default, and `deploy/crds/bundle.yaml` is **1,949,635 bytes** — **~1.9 MB of CRD YAML**, versus 66.6 KB for Flagger and 6.7 KB for sealed-secrets (≈29× and ≈293× respectively). CRDs of that size inflate `kube-apiserver` RSS through OpenAPI schema aggregation and cached schemas — on a single-node cluster the apiserver shares the same 9.5 GB. You can trim it: `crds.createClusterExternalSecret/createClusterSecretStore/createClusterGenerator/createClusterPushSecret/createPushSecret` are all individually disableable (each requires the matching `processX: false`). The magnitude of the apiserver saving is `[UNVERIFIED]`.

Webhook nuance worth knowing: the `webhook.create` comment warns "If set to false, `crds.conversion.enabled` should also be set to false otherwise the kubeapi will be hammered because the conversion is looking for a webhook endpoint." Since `crds.conversion.enabled: false` is **already** the default in 2.9.0 ("Conversion is disabled by default as we stopped supporting v1alpha1"), dropping the webhook is feasible here — but the validating webhook that checks `SecretStore`/`ExternalSecret` specs goes with it.

#### Does it need an external store? **REFUTED as a hard cost — and this is the round's biggest surprise.**

ESO ships two providers that need **nothing outside the cluster**:

- **`fake`** — `docs/provider/fake.md`: "We provide a `fake` implementation to help with testing. This provider returns static key/value pairs and nothing else." Zero infrastructure. Teaches the CR plumbing but nothing about auth.
- **`kubernetes`** — `docs/provider/kubernetes.md`: "External Secrets Operator allows to retrieve secrets from a Kubernetes Cluster — **this can be either a remote cluster or the local one where the operator runs in**." A `SecretStore` points at a namespace, RBAC is checked via `SelfSubjectRulesReview`/`SelfSubjectAccessReview`, and a Secret in another namespace becomes the "external" store.

The `kubernetes` provider is the right teaching vehicle: it exercises the **entire real mechanism** — `SecretStore` + `ExternalSecret` + `refreshInterval` reconciliation + RBAC-scoped store access + templated target Secrets — for **zero additional pods and zero additional MB**. No cloud account, no Vault.

#### If you *do* want a real store: costing in-cluster OpenBao

**Read at:** `openbao/openbao-helm` `main` (chart **0.29.1**, `appVersion: v2.6.1`; newest *tag* is **v0.27.0**, whose values still referenced `hashicorp/vault:1.15.2` — the fork was not rebranded at that tag).

| Component | Pods | Requests | Limits | Disk |
|---|---|---|---|---|
| openbao-injector Deployment (`injector.enabled: "-"` → true via `global.enabled: true`, `replicas: 1`) | 1 | **`resources: {}` — NONE** 🚨 (commented: 256Mi) | NONE 🚨 | — |
| openbao server StatefulSet (`standalone.enabled: "-"` → true; `ha.enabled: false`) | 1 | **`resources: {}` — NONE** 🚨 (commented: 256Mi) | NONE 🚨 | **`dataStorage.size: 10Gi`** |
| CSI provider (`csi.enabled: false`), UI (`ui.enabled: false`) | 0 | — | — | — |
| **Default total** | **2 pods** | ~512Mi if you apply upstream's own suggestions | unbounded | **10 GiB PVC** |

Minimum viable teaching config: `injector.enabled=false` + `server.dev.enabled=true` → **1 pod, no PVC, in-memory, pre-unsealed** ("All data is lost on restart - do not use dev mode for anything other than experimenting"). Also note the injector image on `main` is still `hashicorp/vault-k8s:1.7.2` — the fork is incomplete.

**This is indeed the thing that would push the group over.** Default OpenBao alongside ESO = **5 pods, ~600Mi+ of requests, unbounded limits, and 10 GiB of the 95 G disk** — to teach Vault's mechanism, not ESO's.

**CNCF maturity: Sandbox.** Accepted **2022-07-26**; `landscape.yml` shows `project: sandbox` with **no `incubating` key**, so **no tier change in four years**. *Implication:* still the entry tier despite very broad adoption — no CNCF-verified adopter list, no completed security audit requirement, no graduation-criteria governance review. For a component that holds credentials for every secret store in your estate, that gap is worth stating out loud to students.

---

### Secrets group totals

| Scenario | Pods | Requests | Disk |
|---|---|---|---|
| **SOPS only** (Flux already installed) | **0** | **0** | 0 |
| SOPS + sealed-secrets (with 32Mi req / 128Mi limit overrides) | 1 | ~32Mi (limit 128Mi) | 0 |
| \+ ESO with the `kubernetes` provider (32Mi req each) | 4 | ~128Mi | +1.9MB CRDs |
| \+ ESO with OpenBao default | 6 | ~640Mi, unbounded | **+10 GiB PVC** |
| \+ ESO with OpenBao dev mode | 5 | ~384Mi | 0 |

### Recommendation — mechanism taught per MB

1. **SOPS — INSTALL. Non-negotiable, and it is the best item in the entire curriculum on this axis.** Zero pods, zero MiB, and the curriculum's Flux already supports it natively inside `kustomize-controller`. It teaches encryption-at-rest in Git, age keypair management, `--encrypted-regex` partial encryption, and the `.spec.decryption` wiring that makes a GitOps repo safe to make public. Mechanism per MB: undefined, in the good direction. This satisfies the stated zero-cost-teaching-vehicle principle exactly.

2. **sealed-secrets — INSTALL, minimised.** `--set resources.requests.memory=32Mi --set resources.requests.cpu=10m --set resources.limits.memory=128Mi --set resources.limits.cpu=200m` (which also sets `GOMEMLIMIT`/`GOMAXPROCS` correctly). **1 pod, ~128Mi ceiling, 6.7 KB of CRD** buys a genuinely *different* mechanism from SOPS: a controller that holds a private key you never see, client-side asymmetric encryption via `kubeseal`, and a real reconcile loop. Teaching SOPS *and* sealed-secrets together is the point — same problem, two opposite trust models (you hold the key vs. the cluster holds the key) — and the pair costs 128Mi total.

3. **External Secrets Operator — READ, or install-minimised for one lab and uninstall.** If you install it: use the **`kubernetes` provider**, never Vault/OpenBao. `--set resources.requests.memory=32Mi --set webhook.resources.requests.memory=32Mi --set certController.resources.requests.memory=32Mi` plus matching limits, and consider trimming CRDs via `crds.createPushSecret=false` etc. Cost: **3 pods, ~96Mi, ~1.9 MB of CRDs.** That is 3× the pod count of sealed-secrets for a mechanism (poll an external store, project into a Secret, refresh on an interval) that is conceptually *simpler* than sealed-secrets' crypto. **Do not install OpenBao for this.** It doubles the group's cost, adds 10 GiB of disk, and teaches Vault rather than ESO. If OpenBao belongs in the curriculum it belongs in its own module with its own justification.

**Bottom line: install SOPS and sealed-secrets (1 pod, ~128Mi combined), read about ESO.** If ESO earns a lab later, the `kubernetes` provider makes it affordable without Vault — that finding overturns the assumption that ESO necessarily drags a secret store in behind it.

---

## Summary table

| Project | Pods | Requests (as-shipped) | Recommended cost | CNCF tier | Verdict |
|---|---|---|---|---|---|
| **Flagger** (+loadtester +podinfo) | 4 idle / 6 mid-canary | **224Mi** / 352Mi | ~224Mi, controller capped 512Mi | Graduated (inherited from Flux, 2022-11-30) | **INSTALL** |
| **Backstage** | 2 (+1 init) | **`resources: {}`** — real cost ~1.25Gi req / 3.5Gi limits | — | Incubating (2022-03-15) | **READ, DON'T INSTALL** |
| **SOPS** | **0** | **0** | **0** | Sandbox (2023-05-17) | **INSTALL** (free) |
| **sealed-secrets** | 1 | **`resources: {}`** | ~32Mi req / 128Mi limit | **Not a CNCF project** | **INSTALL, minimised** |
| **ESO** | 3 | **`resources: {}` ×3** | ~96Mi + 1.9MB CRDs, `kubernetes` provider only | Sandbox (2022-07-26) | **READ** (or one minimised lab) |
| *(OpenBao, if ESO installed with a real store)* | 2 | **`resources: {}` ×2** | ~512Mi + **10GiB PVC** | — | **DON'T** |

**Total added by the recommended set (Flagger + SOPS + sealed-secrets): 5 pods, ~256Mi of requests, ~640Mi of hard limits, ~0 extra disk beyond images.** Comfortably inside the ceiling. Backstage alone would have cost 5× that and could not be built at all.

---

## `[UNVERIFIED]` items

Every gap, in one place. None of these were estimated.

1. **Steady-state observed RSS of the Flagger controller.** No reliable published measurement found. Default limit 512Mi is a cap, not a measurement.
2. **Steady-state observed RSS of `flagger-loadtester`.** Ships no limit; actual consumption during a `hey` load run unmeasured.
3. **Steady-state observed RSS of the sealed-secrets controller.**
4. **Steady-state observed RSS of the three ESO pods.** Only upstream's commented-out 32Mi suggestion is available, which is a sizing hint from maintainers, not a measurement.
5. **Steady-state observed RSS of an OpenBao server pod.**
6. **Baseline (non-OOM) steady-state RSS of a minimal Backstage backend.** Every published figure I could find is an OOM-tail heap size (4.0–4.2 GB), which is a ceiling. RHDH's 1Gi request is a *vendor default*, the best proxy available, but still not a measurement.
7. **On-disk size of `node_modules` for a freshly scaffolded Backstage app.** The `create-app` template's `yarn.lock` is a 12-line stub (1 `resolution:` entry) — the real lockfile is generated at `yarn install` time — so not even a package count was derivable.
8. **Uncompressed on-disk size of `ghcr.io/backstage/backstage:latest`.** 333 MB compressed across 17 layers is verified from the GHCR manifest; the expansion ratio was not measured.
9. **Peak RAM of `yarn install` specifically**, as distinct from `yarn tsc:full` / `yarn build:all`. The 8192 MB `NODE_OPTIONS` ceiling covers all of them collectively.
10. **Magnitude of the `kube-apiserver` RSS increase caused by ESO's 1.9 MB CRD bundle.** The bundle size is verified; the apiserver impact is asserted directionally only.
11. **Whether SOPS has had any CNCF tier change since 2023-05-17.** `landscape.yml` shows `project: sandbox` with no `incubating` key, which I read as "still Sandbox", but I could not check CNCF TOC minutes to confirm no in-flight promotion.
12. **Whether `openbao-helm` chart 0.29.1 (on `main`, `appVersion v2.6.1`) has been released.** The newest visible tag is `v0.27.0`, whose `values.yaml` still referenced `hashicorp/vault:1.15.2`. The `main` numbers are cited; the released-chart numbers may differ.
13. **ESO's shipped chart version for appVersion v2.9.0.** `Chart.yaml` at tag `v2.9.0` declares `version: "2.8.0"`; `Chart.yaml` on `main` declares `2.9.0`. All `values.yaml` line numbers above are from the file at tag `v2.9.0`. I could not reconcile which version string ships with the published chart.
14. **Flagger controller memory behaviour when watching many `Canary` objects simultaneously.** The curriculum's labs will have 1–2, so the 512Mi cap is very likely ample, but the scaling curve is unmeasured.
15. **Whether the `install-dynamic-plugins` initContainer pattern (RHDH) has an upstream-Backstage equivalent** that would apply to a self-built image. It is a Red Hat addition; I did not verify whether upstream needs anything analogous.
16. **Community-reported measurements generally.** The session's WebSearch budget was exhausted before this round, so no blog-post or conference-talk measurements were consulted for any project. All figures are from repo files, GitHub issue bodies, GHCR manifests, and `cncf/landscape`.

---

### Source index (files actually read, with refs)

- `fluxcd/flagger` @ `v1.44.0`: `charts/flagger/values.yaml`, `charts/flagger/Chart.yaml`, `charts/flagger/templates/deployment.yaml`, `charts/flagger/templates/prometheus.yaml`, `charts/flagger/crds/crd.yaml`, `charts/loadtester/values.yaml`, `charts/loadtester/Chart.yaml`, `kustomize/podinfo/{deployment,hpa}.yaml`, `MAINTAINERS`, `docs/gitbook/usage/{deployment-strategies,metrics}.md`, `docs/gitbook/tutorials/kubernetes-blue-green.md`
- `backstage/charts` @ `backstage-2.10.0`: `charts/backstage/values.yaml`, `charts/backstage/Chart.yaml`, `charts/backstage/templates/backstage-deployment.yaml`; PR `backstage/charts#27`
- `backstage/backstage` @ `main`: `packages/create-app/templates/default-app/app-config.yaml.hbs`, `.../package.json.hbs`, `.../.github/workflows/ci.yml`, `.github/workflows/ci.yml`; issues `#6485`, `#20385`, `#21982`, `#23047`, `#26776`, `#27347`, `#27700`; `backstage.io/docs/deployment/docker`, `backstage.io/docs/features/software-templates/`
- `bitnami/charts` @ `postgresql/12.10.0`: `bitnami/postgresql/values.yaml`
- `redhat-developer/rhdh-chart` @ `main`: `charts/backstage/values.yaml`
- GHCR registry API: `ghcr.io/backstage/backstage:latest` manifest list + amd64 manifest
- `getsops/sops` @ `main`: repository root listing (absence of chart/manifests)
- `fluxcd/kustomize-controller` @ `v1.9.4`: `docs/spec/v1/kustomizations.md` §Decryption; release asset `kustomize-controller.deployment.yaml`
- `fluxcd/flux2` @ `v2.9.4`: `manifests/bases/kustomize-controller/kustomization.yaml`
- `bitnami/sealed-secrets` @ `v0.38.4`: `helm/sealed-secrets/values.yaml`, `helm/sealed-secrets/Chart.yaml`, `helm/sealed-secrets/templates/deployment.yaml`, `helm/sealed-secrets/crds/bitnami.com_sealedsecrets.yaml`, templates directory listing
- `external-secrets/external-secrets` @ `v2.9.0`: `deploy/charts/external-secrets/values.yaml`, `Chart.yaml`, `templates/` listing, `deploy/crds/bundle.yaml` (size), `docs/provider/{fake,kubernetes}.md`, `docs/provider/` listing
- `openbao/openbao-helm` @ `v0.27.0` and `main`: `values.yaml`, `Chart.yaml` (both refs), `charts/openbao/values.yaml`
- `cncf/landscape` @ `main`: `landscape.yml` — entries for Flagger, Flux, Backstage, SOPS, external-secrets; absence of any sealed-secrets entry
