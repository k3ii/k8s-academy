# Ecosystem either/or picks, CNCF maturity tiers, and resource footprints

Resolves [#6](../../issues/6). Tiers verified against the live CNCF project lists and per-project
landscape pages on **2026-08-17** — not from blog posts, which go stale within months. Footprints are
upstream chart/manifest defaults plus measured community reports, not vendor marketing.

Lab ceiling from the map ([#1](../../issues/1)): **~9.9GB RAM, 6 cores, one Proxmox node**, minus
`hopper`, `carthage` and `jeremie`. Realistically the Kubernetes cluster VMs get **~6–7GB**, and after
k0s control plane, kubelet, containerd, CoreDNS and a CNI, the **add-on budget is ~3–4GB**. Every number
below should be read against that figure, not against 9.9GB.

---

## Verdict 1 — GitOps: **Flux is the module. Argo CD is a one-session comparison lab.**

**Mechanism.** Flux's GitOps Toolkit decomposes into four single-purpose controllers, each with its own
CRD and its own reconcile loop:

- `source-controller` polls Git/OCI/Helm/Bucket and publishes an **immutable artifact tarball** on an
  in-cluster HTTP endpoint. It is the only component that speaks Git.
- `kustomize-controller` / `helm-controller` consume that artifact by reference, build, and apply with
  **server-side apply**, tracking ownership via a field manager and pruning from an **inventory recorded
  in `.status`**.
- `notification-controller` fans events out.

That is a textbook controller chain: watch → build desired state → SSA diff → apply → record status
conditions → requeue on `spec.interval` (minimum 60s). It is exactly the pattern the learner is going to
hand-write in Rust on the `kube-rs` build track, which makes Flux the reference implementation for
another module rather than a standalone detour.

Argo CD is a different animal: one privileged application-controller holding a **watch-based live-state
informer cache** of the whole cluster, a `repo-server` that fork/execs Helm and Kustomize and caches
rendered manifests in **Redis**, and a three-layer cache (manifest / live-state / diff-result) feeding a
bespoke diff-and-health engine. Full reconciliation runs on a ~120s timer plus up to 60s jitter. This is
sophisticated and worth *seeing* — but it teaches "how this one engine works," not "how Kubernetes
controllers work."

**Multi-tenancy.** Flux uses the API server's own machinery: a tenant gets a namespace and a
ServiceAccount, and each `Kustomization`/`HelmRelease` sets `spec.serviceAccountName`, causing the
controller to **impersonate** it. Isolation is RBAC, enforced by the API server — which reinforces
CKS-relevant RBAC learning instead of competing with it. Argo CD instead layers `AppProject` +
Casbin-style RBAC (`argocd-rbac-cm`) + Dex/OIDC groups in front of one highly-privileged controller.
Powerful, but Argo-specific, and it teaches you Argo's authz model rather than Kubernetes'.

**Footprint — decisive.** Flux's upstream manifests ship explicit defaults:
`source-controller` 50m/64Mi, the other three 100m/64Mi requests, **1000m/1Gi limits each**. Four
controllers = ~350m CPU / 256Mi requested, with measured idle around **~30Mi per controller
(<150Mi total)**. Argo CD's upstream manifests and Helm chart ship **`resources: {}` — no requests, no
limits, on every component.** On a 9.9GB node that is not a neutral default, it is an unbounded
application-controller one bad sync away from an OOM cascade. Realistic Argo CD `core-install`
(controller + repo-server + redis + applicationset, no UI, no Dex) still lands ~600Mi–1Gi.

**Verdict.** Flux is primary and stays installed through the GitOps module. Argo CD gets one session:
`core-install.yaml`, drive a single `Application`, then a second pass with the full install to look at
the resource-tree/health UI — which is a genuine one-time visualisation aid for what a diff engine
computes — then **tear it down**. Argo CD is what the learner will meet in industry, so it cannot be
skipped, but it must not be co-resident with Flux. The UI is a crutch precisely because it lets you
click Sync without ever forming a reconcile-loop mental model; look at it *after* Flux has taught the
loop, never before.

**Currency notes.** Argo CD 3.0 GA'd 2025-05-06 (fine-grained per-resource-kind RBAC); the line is well
past 3.x by now. The hub-and-spoke `argocd-agent` has **not** landed in core Argo CD — it is still
`argoproj-labs`, and the productised version is Akuity's commercial platform. Flux's corporate sponsor
Weaveworks collapsed in early 2024; core maintainers moved to **ControlPlane**, which now drives
development and ships the `flux-operator` (lifecycle automation, `ResourceSet` templating, sharding) on
top of upstream CNCF Flux. Both are CNCF Graduated and neither tier has moved.

---

## Verdict 2 — Policy: **Kyverno is the engine. Rego is taught off-cluster. The admission chain is taught with no engine at all.**

This one only resolves cleanly if you separate three different learning goals that "Gatekeeper vs
Kyverno" conflates.

**Goal A — the admission chain itself.** Neither project should teach this, because both hide it. The
mechanism is `AdmissionReview` request/response, JSON patches, `failurePolicy`, `timeoutSeconds`,
`matchPolicy`, and mutating-before-validating ordering. Teach it by **hand-writing an admission webhook
with `kube-rs`** (joins straight onto the Rust build track, costs ~20Mi to run) and then by
**`ValidatingAdmissionPolicy`** — CEL, evaluated in-process by kube-apiserver, GA in Kubernetes 1.30,
with `MutatingAdmissionPolicy` now stable in 1.36. Footprint: **zero**. This is the single best
depth-per-megabyte trade in the whole module.

**Goal B — Rego.** Teach OPA **standalone**, off-cluster: `opa eval` against saved `AdmissionReview`
JSON on `hopper`. Rego's partial evaluation, bundles and decision logs are worth real time, and none of
it needs a cluster. Zero footprint, and it decouples "learning Rego" from "running Gatekeeper."

**Goal C — a production policy engine in-cluster.** Here **Kyverno wins**, on five grounds:

1. **Surface area.** One CRD family covers `validate`, `mutate`, `generate`, `cleanup` and
   `verifyImages`. Gatekeeper is validation-first; its mutation support is newer and peripheral. If the
   learner installs one engine, Kyverno exercises mutating webhooks and generated resources too.
2. **Its best mechanism is a teaching moment Gatekeeper doesn't offer.** Kyverno's **webhook-controller
   rewrites Kyverno's own `ValidatingWebhookConfiguration`/`MutatingWebhookConfiguration` at runtime**,
   narrowing the rules to only the GVKs the installed policies actually match. Watching that object
   mutate as you add and remove policies teaches webhook scoping and blast radius better than any static
   config can.
3. **The controller split maps onto a real distributed-systems distinction.** `admission-controller` (the
   only mandatory component) is the synchronous path; `background-controller` exists because
   `generate` and `mutate-existing` **cannot** happen inside an admission response and must be
   reconciled after the fact; `reports-controller` writes `PolicyReport`s from background scans. That
   "what can and cannot be done synchronously in a webhook" boundary is the lesson.
4. **It double-serves the supply-chain module.** Kyverno `verifyImages` does Cosign verification
   in-admission, so the signing module needs **no additional cluster component** — no Sigstore
   policy-controller, no second webhook. At 9.9GB, one install serving two modules is worth real points.
5. **Footprint and momentum.** Gatekeeper's chart defaults to **3 controller-manager replicas at
   100m/512Mi each plus an audit pod at 512Mi ≈ 2Gi requested** — it must be trimmed to 1+1 (~1Gi)
   before it is even installable here. Kyverno requests 100m/128Mi (admission) + 3×100m/64Mi = **320Mi
   total**, and the admission-controller alone is a legitimate minimal install at 128Mi. Kyverno reached
   **CNCF Graduated on 2026-03-24**; Gatekeeper has no independent CNCF tier at all and has been visibly
   losing ground (Adevinta publicly migrated off it citing OPA memory behaviour).

**What is genuinely lost by not installing Gatekeeper**, and should be covered as reading rather than a
lab: the `ConstraintTemplate` → generated-CRD → `Constraint` indirection; `input.review.object` as the
most direct exposure to a raw AdmissionReview payload anywhere in the ecosystem; the **audit controller**
as a separate code path re-evaluating existing objects from a cache (enforcement-now vs detection-later);
and the `Config`/`SyncSet` mechanism that replicates cluster state into OPA's in-memory cache at
`data.inventory.*` for referential constraints — whose **cache staleness is a genuine TOCTOU hole** and
is the sharpest single idea in Gatekeeper. If there is slack in the budget, a trimmed
one-replica Gatekeeper for exactly that one experiment is the best possible use of ~600Mi.

Note both projects now generate native VAP/CEL rather than owning enforcement: Gatekeeper's
`K8sNativeValidation` engine (stable v3.18+) emits `ValidatingAdmissionPolicy` + bindings from
ConstraintTemplates, and Kyverno does the equivalent for a subset of its policies. The direction of
travel is that third-party engines become **policy authoring and orchestration layers over in-apiserver
CEL** — which is itself the most current thing the module can teach.

---

## Verdict 3 — Istio: **sidecar mode teaches the internals; ambient mode is the second lab and the escape hatch.**

**Sidecar is the only mode that can teach what the requirement asks for.** The goal is Envoy/xDS
internals and how interception *actually* works, and sidecar mode gives a 1:1 pod-to-proxy mapping you
can put your hands on:

- `istio-init` (or the CNI plugin running the same logic without a privileged init container) writes NAT
  chains into the pod's own netns: **`ISTIO_INBOUND`** on PREROUTING passes the exempt ports (15008,
  15090, 15021, 15020) straight through and sends everything else via **`ISTIO_IN_REDIRECT`** to Envoy's
  inbound listener on **15006**; **`ISTIO_OUTPUT`** on OUTPUT passes traffic already originating from
  Envoy's own **UID/GID 1337** (the loop-breaker) and redirects the rest via **`ISTIO_REDIRECT`** to
  **15001**. A learner can `kubectl exec` into one pod, run `iptables-save -t nat`, and read the whole
  interception story off the screen.
- `istioctl proxy-config listeners|routes|clusters|endpoints` then dumps what **xDS** actually pushed to
  *that* proxy — LDS (sockets) / RDS (HTTP routing) / CDS (upstream clusters, pools, LB policy) / EDS
  (backend IPs) — over one persistent gRPC ADS stream per proxy from `pilot-discovery` inside istiod,
  which computes **delta** pushes (a scale event triggers an incremental EDS update, not a full rebuild).

Ambient mode structurally removes both of those handles. There is no per-pod proxy to exec into: a single
per-node Rust **ztunnel** DaemonSet serves every pod on the node, and the L7 path only exists at all if
you deploy a **waypoint** (an ordinary Envoy, per namespace or service). Ambient is the better teacher
of *architecture* — per-node vs per-pod cost scaling, L4 identity separated from L7 policy, **HBONE**
(HTTP/2 `CONNECT` inside mTLS on **port 15008**) — but it is a much harder first exposure to
interception.

**Correct the mechanism note before it reaches the curriculum:** ztunnel redirection is **not Geneve**.
The documented default is `istio-cni`'s node agent entering the pod's network namespace and installing
**iptables TPROXY/REDIRECT rules with connection marks** in that netns, then handing ztunnel a **raw file
descriptor for the namespace over a Unix domain socket** so one per-node process can open listeners
(15008 HBONE / 15006 plaintext / 15001) *inside* every pod's netns without a sidecar. That
cross-namespace-socket trick is ambient's real party piece and is a genuinely great internals hook — but
it is a different mechanism from tunnel encapsulation, and teaching Geneve here would be teaching a myth.

**Footprint.** Istio's own benchmark (1000 rps, 1KB payload): sidecar Envoy **~0.20 vCPU / 60Mi per
pod**; waypoint Envoy **~0.25 vCPU / 60Mi per namespace**; ztunnel **~0.06 vCPU / 12Mi per node**
(20–50Mi under real connection load). Solo.io's aggregate benchmark puts ambient L4-only at **~1% of
sidecar memory and CPU**, and ambient-with-waypoints at **~10% memory / ~15% CPU** of sidecar. Because
ztunnel is per-node, its cost is flat in pod count; sidecar cost is linear.

The fixed cost both modes share is **istiod, whose default request is 500m CPU / 2Gi memory with no
limit** — and that request, not the data plane, is what actually threatens this lab. On a 1-node,
20-pod mesh istiod idles far below 2Gi; **override the request to ~512Mi** or the scheduler will refuse
to place anything else.

Worked estimates against a ~3–4GB add-on budget:

| Mode | istiod | Data plane | Total |
|---|---|---|---|
| Sidecar, bookinfo scale (~6–8 pods) | ~512Mi (overridden) | 6–8 × 60Mi ≈ 0.4–0.5Gi | **~1.0Gi** |
| Sidecar, 20 pods | ~512Mi | 20 × 60Mi ≈ 1.2Gi (2.6Gi at the default 128Mi request) | **~1.7–3.1Gi** |
| Ambient, any pod count | ~512Mi | 1 ztunnel (12–50Mi) + 1–3 waypoints (60–180Mi) | **~0.6–0.75Gi** |

**Verdict.** Do the internals in **sidecar mode**, but cap the mesh at **bookinfo scale (~6–8 pods)** and
override istiod's request. Then, on the same istiod, flip the namespace to ambient
(`istio.io/dataplane-mode=ambient`, injection removed) as lab two and **measure the drop** — the
before/after number *is* the lesson about per-pod vs per-node data planes, and it lands far harder than
reading either architecture in isolation. Ambient is also the escape hatch: if sidecar mode at 20 pods
OOMs the node, that is a scheduled-under-contention incident the curriculum wants anyway, and ambient is
the documented remediation.

Ambient has been **GA since Istio 1.24 (Nov 2024)** and is production-viable in 2026 (ztunnel throughput
improved ~75% over four releases), but sidecar mode is still what most Istio quick-starts and
troubleshooting guides assume — another reason it belongs first.

---

## Project table

Footprints are **realistic small-install minimums**, not vendor recommendations. "per node" marks
DaemonSets, which multiply — the single most under-estimated cost at this ceiling. Charts marked
*(no defaults)* ship `resources: {}`, so the figure is what you should set, not what you get.

| Project | CNCF tier (date) | Realistic minimum footprint | Internals hook | Production note |
|---|---|---|---|---|
| **Helm** | Graduated (2020-05-01) | **0 in-cluster.** CLI only — v3 removed Tiller | Release state is a **gzipped protobuf in a Secret** (`sh.helm.release.v1.<name>.v<n>`); `helm get manifest` vs `--dry-run=server`; three-way strategic-merge on upgrade. Read one Secret by hand to kill the "Helm is magic" instinct | Universal, boring, safe. Its weakness is templating YAML as text, which is why Kustomize/CUE/jsonnet keep re-appearing |
| **Argo CD** | Graduated as **Argo** umbrella (2022-12-06) | `core-install` ~600Mi–1Gi; full +server+dex ~1–1.5Gi. **(no defaults)** — unbounded by default | Three-layer cache (manifest / live-state informer / diff-result) feeding the diff+health engine; `argocd app diff`; sync waves and hooks; ~120s+jitter reconcile timer | Dominant enterprise GitOps tool; the UI is a real operational asset. Umbrella tier covers Workflows/Events/Rollouts too, so "Argo is graduated" says nothing about any one of them |
| **Flux** | Graduated (2022-11-30) | 4 controllers: 350m / **256Mi requested**, 1Gi limit each; **<150Mi measured idle** | Artifact handoff: source-controller tars a revision and serves it over HTTP; kustomize-controller applies with **server-side apply** + field-manager ownership and prunes from the `.status` inventory; tenant **impersonation** via `spec.serviceAccountName` | Graduated and healthy, but its sponsor Weaveworks died in 2024 — continuity came from maintainers moving to ControlPlane, not from the tier |
| **Istio** | Graduated (2023-07-12) | istiod **500m/2Gi default request** (override to ~512Mi); sidecar 60Mi/pod; ztunnel 12–50Mi **per node**; waypoint ~60Mi/ns | `istio-init` iptables chains (`ISTIO_INBOUND`/`ISTIO_OUTPUT`/`ISTIO_REDIRECT`, ports 15006/15001, UID 1337 loop-break) + **xDS** LDS/RDS/CDS/EDS delta pushes over one ADS gRPC stream. Ambient: istio-cni passing a **netns fd over a Unix socket** so ztunnel opens listeners inside pod namespaces; **HBONE** = HTTP/2 CONNECT in mTLS on 15008 | The most capable and the most operationally demanding thing on this list. Graduation did not make it simple — the existence of ambient mode is Istio admitting its own sidecar overhead was a problem |
| **Linkerd** | Graduated (2021-07-28) | Control plane 3 pods, **(no defaults)** — budget ~300–500Mi; proxy **17–26Mi/pod** idle; `linkerd-viz` bundles **its own Prometheus** (+0.5–1Gi) | `linkerd2-proxy` is Rust, not Envoy — read it as the counter-example to Envoy's generality; identity via **CSR to the identity controller signed by the trust anchor**; discovery is an internal gRPC API, **not xDS** | Simpler and far lighter than Istio (CNCF benchmarks: ~5–9× less proxy memory, ~8× less CPU than Envoy), but the commercial model tightened around stable releases — check what "open source Linkerd" means before adopting |
| **Cilium** | Graduated (2023-10-11) | agent **300–500Mi per node** measured (creeps upward), operator ~128–256Mi, +Hubble relay 128Mi + UI ~128Mi | eBPF at tc ingress/egress and XDP; **kube-proxy replacement** implements Services in BPF maps instead of iptables/IPVS — verify with `cilium bpf lb list` and `bpftool prog show`; policy keyed on **security identities, not IPs** | Graduated and the de facto modern CNI, but needs kernel-version awareness and its memory grows with node/pod/policy churn. Requires the most Linux knowledge of anything here |
| **Prometheus** | Graduated (2018, 2nd ever) | Standalone lab **~400Mi–1Gi + a PVC**; full `kube-prometheus-stack` **1.5–2.5Gi** + node-exporter per node. **(no defaults)** on the core components | `relabel_configs` — where service discovery becomes targets, and the one part everybody skips; then head block → **WAL** → 2h block compaction; `rate()` over counters and why gauges lie | The default. Its scaling limits (single-node TSDB, no native HA) are why Thanos/Mimir/Cortex exist — tier tells you nothing about that ceiling |
| **Grafana** | **Not CNCF at all.** Grafana Labs is a CNCF member; Grafana/Loki/Tempo/Mimir were never donated | 250–512Mi request, 1Gi limit; CPU spiky (a single dashboard render can want ~1–2 cores) | Datasource proxy: how a panel becomes a PromQL query on the wire; dashboards-as-code provisioning. Thinnest mechanism of anything on this list | Industry-standard dashboarding while sitting entirely outside CNCF — **exhibit A for tier-as-poor-proxy**. Watch the AGPL/licensing history |
| **OpenTelemetry** | **Graduated 2026-05-11** (announced 2026-05-21) — recent, tiers in older posts are wrong | Collector: DaemonSet 256Mi/512Mi per node, gateway Deployment 1Gi/4Gi; Operator 64Mi + 64Mi rbac-proxy | Collector pipeline as a **DAG of receivers → processors → exporters**; W3C `traceparent` context propagation across a process boundary; operator auto-instrumentation injected via init container + env vars | Second-highest-velocity CNCF project and the de facto telemetry standard, but **maturity varies by signal and language** — traces are solid, logs and some language SDKs are not. Graduation is project-level, not signal-level |
| **Falco** | Graduated (2024-02-29) | **512Mi request / 1Gi limit per node**, 100m–1000m CPU; +falcosidekick ~128Mi | Syscall visibility three ways — **modern eBPF (CO-RE)** vs legacy eBPF vs kernel module — then libsinsp's state engine and rule evaluation. The real lesson is the **cost**: ~1–5% CPU under normal load, and `falco_drops` when the ring buffer can't keep up. Dropped events are silent policy failure | The runtime-detection standard and CKS-relevant. Kernel-module driver has no BPF verifier protecting you; prefer modern eBPF |
| **OPA** | Graduated (2021-01-29) | **0 as `opa eval` CLI**; in-cluster server ~128–256Mi | Rego evaluation, **partial evaluation**, bundle distribution, decision logs. It is a general decision engine that happens to be usable for Kubernetes — teach it off-cluster | Widely used well beyond Kubernetes (API authz, Terraform, CI). Rego's learning curve is its main adoption tax |
| **Gatekeeper** | **No independent tier** — a subproject under graduated OPA | Chart default **3 replicas × 100m/512Mi + audit 512Mi ≈ 2Gi**; trim to 1+1 ≈ 1Gi (~270Mi observed idle) | `ConstraintTemplate` → generated CRD → `Constraint`; `input.review.object` is the rawest AdmissionReview exposure available; the **audit controller** as a separate cached code path; `Config`/`SyncSet` replicating cluster state to `data.inventory.*` for referential constraints — and the **cache-staleness TOCTOU** that implies | Losing ground to Kyverno (Adevinta migrated off publicly). Inheriting OPA's "graduated" badge is a category error — Gatekeeper was never assessed |
| **Kyverno** | **Graduated 2026-03-24** — very recent, most comparisons predate it | admission 100m/128Mi (only mandatory component) + 3 × 100m/64Mi = **320Mi requested**, ~600Mi observed | The **webhook-controller rewrites Kyverno's own webhook configurations at runtime** to match installed policies — watch the object change as you add policies. Then: why `generate`/`mutate-existing` must live in the background-controller and cannot be answered inside an admission response | Now graduated with strong adoption (Bloomberg, Coinbase, LinkedIn, Spotify). YAML-native lowers the barrier; the flip side is policies get verbose fast |
| **cert-manager** | Graduated (TOC vote 2024-09-29, announced 2024-11-12) | **(no defaults)** — budget controller 64Mi/256Mi, webhook 32Mi/128Mi, cainjector 64Mi ≈ **160Mi requested** | The CR chain `Certificate → CertificateRequest → Order → Challenge`, then **ACME HTTP-01** (solver pod + temporary Ingress) vs **DNS-01** (TXT record), plus SelfSigned/CA issuers and the Secret renewal loop. On an isolated NAT'd bridge, HTTP-01 against Let's Encrypt **cannot work** — use pebble or a CA issuer, and make that constraint the lesson | Near-universal for TLS in Kubernetes. Explicitly ships no resource requests, which its own best-practice docs flag |
| **Sigstore / Cosign** | **Not CNCF** — hosted by **OpenSSF** (Linux Foundation) | **Cosign CLI: 0.** policy-controller webhook 100m/128Mi req, 256Mi limit — **and you don't need it if Kyverno is installed** | Keyless flow: OIDC token → **Fulcio** issues a short-lived X.509 binding the identity → signature + cert logged to **Rekor** → verification checks the chain, the SCT, the **Merkle inclusion proof** and the signed entry timestamp. "Where does trust actually come from" in five moving parts | *The* signing standard — Kubernetes signs its own releases with it — while carrying **no CNCF tier whatsoever**. Exhibit B |
| **Syft / Grype** | **Not CNCF** — Anchore projects | **0** — CLI only (transient memory spikes on large images) | SBOM cataloguers reading package DBs inside image layers; then PURL/CPE matching against a vuln DB — which is exactly where **false positives** are manufactured | Widely used, vendor-led, no foundation tier. Run on `hopper`, never in-cluster |
| **Trivy** | **Not CNCF** — Aqua project. (Stale posts calling it "CNCF Sandbox" are wrong; it is on none of the three lists) | CLI **0**; `trivy-operator` scan Jobs 100m/100Mi req → 500m/500Mi limit (bursty); trivy-server 200m/512Mi req | Same matching pipeline as Grype, plus misconfiguration and secret scanning. Compare its SBOM to Syft's on the same image and explain the divergence | The most-used scanner in CI, entirely outside CNCF. Exhibit C |
| **Chaos Mesh** | **Incubating** (since 2022-02-16 — no movement in 4+ years) | controller-manager 250m/512Mi + **chaos-daemon 100m/256Mi per node** ("light" profile) + dashboard 100m/128Mi. **No database** | `chaos-daemon` enters the target pod's **netns/pid namespace** to inject faults — `tc netem` for network chaos, a FUSE/hook layer for IO chaos, CRI calls for PodChaos. It is a namespace-manipulation lesson wearing a chaos costume | The right choice for constrained environments: CRD-only state, no backing store. Stuck at Incubating for years without that meaning it is unfit |
| **Litmus** | **Incubating** (since 2022-01-11 — also static) | ChaosCenter min **1 core / 1GiB**, recommended **2 vCPU / 8GB**, **plus a mandatory MongoDB** (+1–2GB) and a PVC (20Gi recommended) | Experiments as Kubernetes **Jobs** driven by `ChaosEngine`/`ChaosExperiment`; **litmus-probes** encode the steady-state hypothesis — the most genuinely chaos-engineering idea in either tool | Richer workflow/UI story than Chaos Mesh. **Does not fit this lab** — read the architecture, run the ideas via Chaos Mesh |
| **kube-rs** | **Sandbox** (since 2021-11-16) | **0** as a library; a controller you build with it runs at **~10–30Mi RSS** — itself a teaching point about Go controller overhead | `Controller` runtime = `watcher` stream → reflector/`Store` → scheduler/queue → `reconcile` with requeue. Because nothing is scaffolded for you, it forces you to confront `resourceVersion`, `Bookmark` events and watch-restart semantics that client-go hides | Sandbox because it is a single-language niche, **not** because it is unproven. It is the only serious Rust Kubernetes client — there is no more-mature alternative to graduate to |
| **k0s** | **Sandbox** (accepted 2025-01-19) | controller **1GB / 1 vCPU**; worker **0.5GB / 1 vCPU**; single-node controller+worker **1GB**. ~7% less memory and ~47% less disk than kubeadm | A **single static binary** supervising the control-plane components as child processes, plus the manifest-deployer directory that makes "drop a YAML on disk" a valid apply path. Compare `ps` on a k0s controller against a kubeadm one | Sandbox, yet a CNCF-conformant distro shipped and supported by Mirantis in production. Its light footprint is a **structural asset** for this lab, not a curiosity |
| **etcd** | Graduated (2020-11-24) | Standalone learning: **512Mi–1GB / 1 core**. Production dedicated: **8GB+**. **Disk fsync latency matters more than RAM** | Raft append/commit/apply; **MVCC revisions** over a b-tree keyspace on a boltdb backend; watch streams from a revision; **compaction vs defrag** as different operations; quorum arithmetic and lease TTLs | The single highest depth-per-megabyte topic available. Run it **standalone, off-cluster, no Kubernetes at all** — the map already flags this and the footprint confirms it |
| **containerd** | Graduated (2019-02-28) | Tens of MB idle per node; **embedded in k0s**, nothing extra to install | CRI plugin → content/snapshotter/tasks services → **a shim per pod sandbox** → runc creating namespaces and cgroups. Drive it directly with `ctr` and `crictl`, and read overlayfs layering in the snapshotter | Invisible infrastructure, which is the point. Nearly every cluster runs it |
| **CoreDNS** | Graduated (2019-01-24) | kubeadm manifest **100m / 70Mi request, 170Mi limit**; ×2 replicas ≈ **140Mi** | The Corefile **plugin chain, whose order is semantic**; the `kubernetes` plugin watching Services/EndpointSlices to answer A/SRV per the DNS spec; then `ndots:5` + search domains — the cause of a large share of all "slow Kubernetes" tickets | Default in every distribution. Cheap, and among the highest-leverage debugging knowledge in the whole curriculum |
| **MetalLB** | **Sandbox** (accepted 2021-09-14) | controller 50m/64Mi + **speaker 50m/64Mi per node** ≈ 130–260Mi | **L2 mode**: the elected speaker answers **ARP/NDP** for the VIP (memberlist election). **BGP mode**: speaker peers with a router and advertises /32s. On a NAT'd bridge with no physical port, L2 is the only option — and the ARP-vs-BGP distinction explains exactly why | Sandbox for 5 years while being the de facto bare-metal LoadBalancer for on-prem and homelab Kubernetes. **Exhibit D**, and the clearest one |

---

## Where CNCF tier is a poor proxy for production readiness

This is the part worth teaching explicitly, because the tier ladder measures **project governance**, not
**fitness for your cluster**.

1. **Graduated says nothing about operability, and often correlates inversely.** Istio and Cilium are
   both Graduated and are the two heaviest, most Linux-knowledge-hungry things on the list. Graduation
   assesses adoption, contributor diversity across employers, a completed third-party security audit,
   documented governance and release discipline. It does not assess resource cost, day-2 burden, or
   whether it fits in 9.9GB. Nothing in the criteria could have stopped Istio from needing 2Gi for
   istiod by default.

2. **Sandbox does not mean immature, and here it usually means "niche."** **MetalLB** has been Sandbox
   for five years while being the standard bare-metal LoadBalancer. **k0s** is Sandbox and is a
   Mirantis-supported, CNCF-conformant production distro. **kube-rs** is Sandbox and is the only serious
   Rust Kubernetes client — there is nothing more mature to graduate to. All three are load-bearing in
   this curriculum specifically *because* of what they do, not despite their tier.

3. **Not being in CNCF at all is not a signal.** **Grafana** is the industry-default dashboard and was
   never donated (Grafana Labs is merely a member). **Sigstore/Cosign** is *the* artifact-signing
   standard — Kubernetes signs its own releases with it — and lives at OpenSSF. **Trivy**, **Syft** and
   **Grype** are the default scanners and are vendor-led with no tier anywhere. Which foundation hosts a
   project is partly a corporate and legal decision, and reading it as a quality score is simply an
   error.

4. **Tier is per-project, never per-feature, and it lags.** Istio graduated in July 2023; **ambient
   mode inside graduated Istio only reached GA in 1.24, in November 2024**. OpenTelemetry graduated in
   May 2026 while its logs signal and several language SDKs remain materially less mature than its
   traces. A Graduated project routinely contains alpha subsystems, and the tier was awarded to the
   project, not to the subsystem you are about to depend on. **Always check the feature's own maturity.**

5. **Subprojects inherit a badge they were never assessed for.** **Gatekeeper** has no independent CNCF
   maturity level; it rides under Graduated OPA. **Cosign** rides under Sigstore at OpenSSF. "OPA is
   graduated, so Gatekeeper is production-grade" is a category error — and in this case a costly one,
   since Gatekeeper's momentum has visibly declined while its parent's tier has not moved a millimetre.

6. **Tier does not track who is left to maintain the code.** **Flux** stayed Graduated straight through
   Weaveworks' collapse in early 2024; continuity came from maintainers relocating to ControlPlane, and
   the tier would have looked identical had they not. Conversely, **Chaos Mesh** and **Litmus** have both
   sat at Incubating since early 2022 — four and a half years of stasis at the same rung tells you
   considerably more about each project's trajectory than the rung itself does. **Read commit velocity,
   maintainer affiliation diversity and release cadence; the tier is a lagging summary at best.**

7. **Sometimes the right answer has no tier because it is upstream Kubernetes.**
   `ValidatingAdmissionPolicy` (CEL, GA in 1.30) and `MutatingAdmissionPolicy` (stable in 1.36) can now
   replace a Graduated policy engine for a large class of rules at **zero footprint and zero operational
   surface**. Both Gatekeeper and Kyverno are converging on *generating* these rather than owning
   enforcement. "Which CNCF project solves this" is occasionally the wrong question, and noticing that is
   the most valuable habit in this entire module.

---

## What the footprint reality forces on the module

- **One "big rock" at a time, two at absolute most.** The big rocks are Cilium, Istio, the Prometheus
  stack, and Falco. Any three of them together, once DaemonSets multiply across nodes, exceed the
  add-on budget. Sequence them; tear down between.
- **Fewer nodes for DaemonSet-heavy modules.** Cilium, Falco, node-exporter and the MetalLB speaker all
  cost per node. Run those modules on a **1-controller + 1-worker** (or single-node) cluster so the cost
  is paid once, and reserve a 3-node cluster for the topics that genuinely need it — scheduling and
  eviction, MetalLB L2 failover, etcd quorum.
- **Skip `kube-prometheus-stack` entirely at first.** Standalone Prometheus with a short scrape list and
  15m retention (~400–600Mi) teaches `relabel_configs`, the WAL and PromQL just as well. The operator
  bundle, Alertmanager and Grafana are an observability-**capstone** cost, not a starting cost.
- **Litmus is out; Chaos Mesh is in.** A mandatory MongoDB plus a recommended 8GB does not fit next to
  anything. Litmus becomes an architecture read.
- **The supply-chain module is nearly free.** Cosign, Syft, Grype and Trivy are all CLIs — run them on
  `hopper` at zero cluster cost, and use Kyverno `verifyImages` for the one in-cluster enforcement
  demo instead of adding Sigstore's policy-controller.
- **Spend the reclaimed budget on etcd standalone.** No Kubernetes, ~1GB, and the deepest material in
  the curriculum. The RAM ceiling is not merely survivable here — it actively pushes the syllabus toward
  its highest-value topics.

---

### Sources

Tiers: [CNCF graduated & incubating projects](https://www.cncf.io/projects/),
[CNCF sandbox projects](https://www.cncf.io/sandbox-projects/), and per-project landscape pages
(fetched 2026-08-17);
[OpenTelemetry graduation](https://www.cncf.io/announcements/2026/05/21/cloud-native-computing-foundation-announces-opentelemetrys-graduation-solidifying-status-as-the-de-facto-observability-standard/),
[Kyverno graduation](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/),
[cert-manager graduation](https://www.cncf.io/announcements/2024/11/12/cloud-native-computing-foundation-announces-cert-manager-graduation/),
[Falco graduation](https://www.cncf.io/announcements/2024/02/29/cloud-native-computing-foundation-announces-falco-graduation/),
[Sigstore at OpenSSF](https://blog.sigstore.dev/sigstore-openssf-graduation/).

Mechanism & footprint: [Flux controller manifests](https://github.com/fluxcd/source-controller/blob/main/config/manager/deployment.yaml),
[Flux multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/),
[Argo CD HA/sizing](https://argo-cd.readthedocs.io/en/stable/operator-manual/high_availability/),
[Argo CD diff engine](https://argo-cd.readthedocs.io/en/stable/operator-manual/reconcile/),
[Gatekeeper sync/Config](https://open-policy-agent.github.io/gatekeeper/website/docs/sync),
[Gatekeeper VAP integration](https://open-policy-agent.github.io/gatekeeper/website/docs/validating-admission-policy/),
[Kyverno architecture](https://kyverno.io/docs/introduction/how-kyverno-works/),
[Kyverno scaling](https://kyverno.io/docs/installation/scaling/),
[Istio performance & scalability](https://istio.io/latest/docs/ops/deployment/performance-and-scalability/),
[Istio HBONE](https://istio.io/latest/docs/ambient/architecture/hbone/),
[ztunnel traffic redirection](https://istio.io/latest/docs/ambient/architecture/traffic-redirection/),
[Istio 1.24 ambient GA](https://istio.io/latest/blog/2024/ambient-reaches-ga/),
[Solo.io ambient cost benchmark](https://www.solo.io/blog/reduce-cloud-cost-istio-ambient-mesh),
[k0s system requirements](https://docs.k0sproject.io/stable/system-requirements/),
[etcd hardware guidance](https://etcd.io/docs/v3.5/op-guide/hardware/),
[cert-manager best practice (no default resources)](https://cert-manager.io/docs/installation/best-practice/),
[Falco driver comparison](https://falco.org/blog/choosing-a-driver/),
[Litmus installation sizing](https://docs.litmuschaos.io/docs/getting-started/installation),
[Chaos Mesh Helm values](https://github.com/chaos-mesh/chaos-mesh/blob/master/helm/chaos-mesh/values.yaml),
[ValidatingAdmissionPolicy GA](https://kubernetes.io/blog/2024/04/24/validating-admission-policy-ga/),
[MutatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/).

**Verify before publishing:** Flux's per-controller defaults were confirmed from upstream manifests but
change between releases — re-check the exact version pinned. Gatekeeper's and Kyverno's *observed* idle
figures (~270Mi / ~600Mi) come from one vendor engineering blog, not a controlled benchmark. Falco's
"1–5% CPU" is a community range; the authoritative Falco eBPF-vs-module PDF could not be retrieved.
