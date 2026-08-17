# Rust vs Kubernetes: which extension points can Rust actually build?

Resolves [k3ii/k8s-academy#2](https://github.com/k3ii/k8s-academy/issues/2).

Research date: **2026-08-17**. Reference Kubernetes version: **v1.36.3** (latest stable; v1.37 in
rc as of 2026-08-06 — [k/k releases](https://github.com/kubernetes/kubernetes/releases)).
Reference `kube` version: **4.2.0** (2026-07-22).

Everything below was verified against primary sources on the research date. Claims I could
**not** verify are marked **[UNVERIFIED]** and should not be treated as settled.

---

## 1. Extension point verdicts

| # | Extension point | Rust viable? | Crate / approach | Difficulty for a Rust learner | Source |
|---|---|---|---|---|---|
| 1 | **Controller / operator** (reconcile loop over CRDs) | **Yes — first class.** This is kube-rs's core competency | `kube` w/ `runtime` feature (`kube::runtime::Controller`) | **Medium.** The reconciler signature alone (`Arc<K>`, `Arc<Ctx>`, `async fn`, `Result<Action, E>`) forces async + shared ownership on day one | [kube.rs](https://kube.rs/), [docs.rs Controller](https://docs.rs/kube/latest/kube/runtime/struct.Controller.html) |
| 2 | **CRD definition** (`#[derive(CustomResource)]`) | **Yes.** Generates a real structural OpenAPI v3 schema | `kube-derive` + `schemars` **1.x** (schemars 1 required since kube 2.0) | **Easy–Medium.** Every type in the spec must transitively derive `JsonSchema` — the main papercut | [derive docs](https://docs.rs/kube/latest/kube/derive.CustomResource.html), [schemas guide](https://kube.rs/controllers/schemas/), [version table](https://kube.rs/kubernetes-version/) |
| 3 | **CRD validation (CEL)** | **Yes.** `x-kubernetes-validations` emitted declaratively | `#[derive(KubeSchema)]` + `#[x_kube(validation = Rule::new(...))]` | **Easy** once CRDs work | [admission guide](https://kube.rs/controllers/admission/) |
| 4 | **CRD subresources / printer columns / field selectors** | **Yes.** `status`, `scale`, `printcolumn`, `selectable`, `shortname`, `category`, `served`, `storage`, `deprecated` are all derive attributes | `kube-derive` | **Easy** | [derive docs](https://docs.rs/kube/latest/kube/derive.CustomResource.html) |
| 5 | **Multiple CRD versions + conversion webhook** | **Yes, but low-level.** Multi-version needs one module per version + `merge_crds`; the conversion webhook gives you `ConversionReview`/`ConversionRequest`/`ConversionResponse` types and nothing else | `kube::core::conversion`, `kube::core::crd::merge_crds` | **Hard.** You hand-write the conversion logic and the HTTPS server. No scaffolding equivalent to controller-gen's | [kube-core/src/conversion](https://github.com/kube-rs/kube/tree/main/kube-core/src/conversion), [derive docs](https://docs.rs/kube/latest/kube/derive.CustomResource.html) |
| 6 | **Validating + mutating admission webhook** | **Yes.** It is an HTTPS server returning `AdmissionReview`; kube-rs ships the types *and* a runnable example | `kube::core::admission` (`AdmissionReview`, `AdmissionRequest`, `AdmissionResponse`) + any HTTP server (`axum`/`warp`/`hyper`) + `rustls` | **Medium.** The Rust part is easy; the **TLS/cert plumbing is the real work** (see §4) | [examples/admission_controller.rs](https://github.com/kube-rs/kube/tree/main/examples), [kube-core/src/admission.rs](https://github.com/kube-rs/kube/blob/main/kube-core/src/admission.rs) |
| 7 | **Standalone custom scheduler** (watch pods with `spec.schedulerName`, POST a `Binding`) | **Yes.** `Binding` exists as a first-class namespaced resource in `k8s-openapi` 0.28 with `Kind = "Binding"`, `url_path_segment = "bindings"`, `NamespaceResourceScope` | `kube` watcher + `Api<Binding>::create` (or a raw request to the `pods/{name}/binding` subresource) | **Medium.** No off-the-shelf Rust example exists — you write it from the spec | [k8s-openapi Binding](https://docs.rs/k8s-openapi/latest/k8s_openapi/api/core/v1/struct.Binding.html), [Configure Multiple Schedulers](https://kubernetes.io/docs/tasks/extend-kubernetes/configure-multiple-schedulers/) |
| 8 | **kube-scheduler framework plugin** | **NO. Hypothesis CONFIRMED.** The framework is "a set of 'plugin' APIs that are **compiled directly into the scheduler**"; plugins are Go interfaces (`Plugin`, `FilterPlugin`, `ScorePlugin`, …) satisfied in-process | Go only. Out-of-tree plugins (`kubernetes-sigs/scheduler-plugins`) still mean vendoring k/k and shipping **your own Go scheduler binary** | **N/A — impossible in Rust** | [Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/), [KEP-624](https://github.com/kubernetes/enhancements/blob/master/keps/sig-scheduling/624-scheduling-framework/README.md) |
| 9 | **Scheduler extender (HTTP webhook)** | **Yes — ALIVE, not deprecated. Hypothesis CONFIRMED.** `Extender`, `ExtenderManagedResource`, `ExtenderTLSConfig` are all present in the **GA `kubescheduler.config.k8s.io/v1`** API in `release-1.36`, with **no deprecation marker** in the type comments, and `HTTPExtender` is live in `pkg/scheduler/extender.go` on that branch. Verbs: `filterVerb`, `prioritizeVerb`, `bindVerb`, `preemptVerb` | Plain HTTPS server + hand-written `extenderv1` JSON types (no Rust crate for these — you transcribe from `k8s.io/kube-scheduler/extender/v1`) | **Medium.** Cheap to write; the friction is *deploying* it (you must feed kube-scheduler a `KubeSchedulerConfiguration` file, i.e. edit the control-plane static pod / k0s config) | [types.go release-1.36](https://github.com/kubernetes/kubernetes/blob/release-1.36/staging/src/k8s.io/kube-scheduler/config/v1/types.go#L321-L364), [extender.go release-1.36](https://github.com/kubernetes/kubernetes/blob/release-1.36/pkg/scheduler/extender.go), [config API ref](https://kubernetes.io/docs/reference/config-api/kube-scheduler-config.v1/) |
| 10 | **Wasm scheduler plugin** (`kube-scheduler-wasm-extension`) | **Not a Rust path today.** Language-agnostic *in principle*, but the `guest/` SDK is a **Go module** (TinyGo) — no Rust SDK. Repo has one release (`v0.1.0`, 2024-07-23), last push 2025-11-24, 129 stars | — | **Do not build the curriculum on this** | [repo](https://github.com/kubernetes-sigs/kube-scheduler-wasm-extension), [guest/](https://github.com/kubernetes-sigs/kube-scheduler-wasm-extension/tree/main/guest) |
| 11 | **CSI driver** | **Yes, with real precedent.** OpenEBS **Mayastor** is Rust end-to-end (io-engine data plane + `csi-node` daemonset + `csi-controller` deployment), actively maintained (`v2.11.0-rc.0`, 2026-06-01). **DatenLord** also ships a Rust CSI driver | `tonic` + `prost` over vendored `csi.proto`. **No maintained shared crate** — the only bindings crate found, `kflansburg/k8s-csi`, was last touched 2020-07-21 | **Hard.** You generate your own gRPC bindings and implement Identity + Controller + Node services | [Mayastor architecture](https://mayastor.gitbook.io/introduction/basic-architecture), [mayastor-control-plane releases](https://github.com/openebs/mayastor-control-plane/releases), [datenlord](https://github.com/datenlord/datenlord), [k8s-csi (stale)](https://github.com/kflansburg/k8s-csi) |
| 12 | **CSI sidecar model** | Sidecars are prebuilt **Go** binaries in the same pod that reach your driver over a UNIX socket (`--csi-address`, default `/run/csi/socket`). Your driver only has to speak CSI gRPC — hence language-agnostic | external-provisioner / -attacher / -resizer / -snapshotter, node-driver-registrar, livenessprobe | — | [Developing a CSI Driver](https://kubernetes-csi.github.io/docs/developing.html), [external-provisioner](https://github.com/kubernetes-csi/external-provisioner) |
| 13 | **CNI plugin** | **Yes.** CNI spec **v1.1.0** is explicitly "execution of binaries invoked by the container runtime" — JSON on stdin, JSON on stdout, params in env vars (`CNI_COMMAND`, `CNI_NETNS`, …). `libcni`/`cnitool` are runtime-side Go conveniences, not plugin requirements | `rscni-plugin` (successor to `rscni`, renamed 2026-07-30) or `rust-cni` (v0.1.2, 2025-03-06); or hand-roll with `nix`/`rtnetlink`. Precedents: `passcod/cni-plugins`, `masap/rust_cni` (2 commits — toy), `AlyHKafoury/cni-bridge` (experimental) | **Medium–Hard.** The Rust part is easy; the *Linux netns/veth/route* part is the lesson. All crates are low-adoption | [CNI SPEC.md](https://github.com/containernetworking/cni/blob/main/SPEC.md), [spec versions](https://www.cni.dev/docs/spec-upgrades/), [rscni](https://lib.rs/crates/rscni), [rust-cni](https://lib.rs/crates/rust-cni) |
| 14 | **Device plugin** | **Yes technically — but no Rust precedent found.** `DevicePlugin` is plain proto3 gRPC (`GetDevicePluginOptions`, `ListAndWatch`, `Allocate`, `GetPreferredAllocation`, `PreStartContainer`) over a socket in `/var/lib/kubelet/device-plugins/`. API version is still **v1beta1** | `tonic`/`prost` over `k8s.io/kubelet/pkg/apis/deviceplugin/v1beta1/api.proto`. Every real-world plugin found (incl. NVIDIA's) is Go. The now-**archived** Krustlet vendored this proto in Rust — from the kubelet side | **Medium–Hard**, and you're first | [Device Plugins docs](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/), [api.proto](https://github.com/kubernetes/kubelet/blob/master/pkg/apis/deviceplugin/v1beta1/api.proto), [Krustlet archived 2024-09-30](https://www.cncf.io/projects/krustlet/) |
| 15 | **Aggregated API server** (`APIService`) | **Effectively NO in practice.** Nothing in the wire contract is Go-specific (TLS client-cert auth via the aggregation CA, request-header identity, delegated `TokenReview`/`SubjectAccessReview`, OpenAPI discovery) — but there is **no Rust analogue of `k8s.io/apiserver`**, and **no non-Go implementation was found anywhere**. The docs themselves note most extension apiservers "do it by default, leveraging the `k8s.io/apiserver/` package" | — | **Do not put this on the Rust build track.** Read it in Go instead | [Configure the Aggregation Layer](https://kubernetes.io/docs/tasks/extend-kubernetes/configure-aggregation-layer/), [apiserver-builder-alpha](https://github.com/kubernetes-sigs/apiserver-builder-alpha) |
| 16 | **eBPF program / toy datapath** | **Yes.** Pure-Rust, no libbpf, no C | `aya` 0.14.0 (2026-06-24) + `aya-ebpf` 0.2.1 (2026-06-30) + `aya-log` 0.3.0 + `bpf-linker` 0.11.0 (2026-08-12) | **Hard** — see §3. The Rust is fine; the **toolchain** is the tax | [crates.io/aya](https://crates.io/crates/aya), [crates.io/bpf-linker](https://crates.io/crates/bpf-linker), [Aya book](https://aya-rs.dev/book/) |
| 17 | **Leader election** | **Yes, but NOT in `kube`.** Hypothesis partially **REFUTED** — see §2 | `kube-leader-election` (hendrikmaus, active 2026-06-16), `kube-lease-manager` 0.12.0 (2026-06-17), or `kubert::lease` | **Medium** | [availability guide](https://kube.rs/controllers/availability/), [kube#485](https://github.com/kube-rs/kube/issues/485) |
| 18 | **kubectl plugin** | **Yes, trivially.** Any executable named `kubectl-*` on `$PATH` | plain Rust binary; `kubectl-view-allocations` and `kubectl-watch` are real Rust precedents | **Easy** | [kube-rs adopters](https://kube.rs/adopters/) |
| 19 | **Custom kubelet** | Technically done once (Krustlet), but **archived 2024-09-30**. Not a viable track | — | **Avoid** | [CNCF Krustlet](https://www.cncf.io/projects/krustlet/) |

---

## 2. `kube-rs` maturity

**CNCF status.** kube-rs "was accepted to CNCF on **November 16, 2021** at the **Sandbox**
maturity level" ([cncf.io/projects/kube-rs](https://www.cncf.io/projects/kube-rs/)), and it is
**still Sandbox** as of 2026-08-17 — nearly five years without promotion to Incubating. The site
confirms "Hosted by CNCF as a Sandbox Project" ([kube.rs](https://kube.rs/)). Read this as: real
project, real users, but no CNCF-level governance/maturity guarantees.

**Client support level.** kube-rs claims it "satisfies the [client level requirements for a
**Stable Client**]" under the upstream client-library procedure
([kube.rs/stability](https://kube.rs/stability/)). That is the same rubric client-go is judged
against, so this is a meaningful (if self-asserted) claim.

**Release cadence — the important nuance.** Verified from
[GitHub releases](https://github.com/kube-rs/kube/releases):

| Version | Date | Kubernetes target |
|---|---|---|
| 1.0.0 | 2025-05-13 | 1.33 |
| 2.0.0 | 2025-09-08 | 1.34 |
| 3.0.0 | 2026-01-12 | 1.35 |
| 4.0.0 | 2026-06-16 | 1.36 |
| 4.2.0 | 2026-07-22 | 1.36 |

This is **a semver-major release roughly every 3–4 months**, and that is *deliberate policy*, not
instability: "Every 3 months there's a new Kubernetes version resulting in a new semver breaking
`k8s-openapi` … we aim to ship these semver breaking upgrades for new Kubernetes versions as a
major kube version" ([stability](https://kube.rs/stability/)). Deprecations must survive
**3 major releases** before removal, and breaking PRs must carry migration guidance.

**Curriculum consequence:** "1.0 shipped" does *not* mean "tutorials stay valid." A blog post
written against kube 0.87 (2023) predates schemars 1.x, hyper 1.x, and four majors of API
polish. **Pin a kube major in the curriculum and expect to re-verify code once a year.**
Minimum supported Kubernetes version for kube 4.0.0 is **1.32**, latest target **1.36**
([kubernetes-version](https://kube.rs/kubernetes-version/)).

**Does `kube::runtime::Controller` really cover everything?** Verified against
`kube-runtime/src/` and docs.rs 4.2.0:

| Capability | In `kube-runtime`? | Where |
|---|---|---|
| Watchers | **Yes** | `watcher` module (`watcher::Config`, error recovery) |
| Reflectors / in-memory stores | **Yes** | `reflector` module, `Controller::store()` |
| Informer equivalent | **Yes, but re-imagined** — streams + `WatchStreamExt`, not client-go's `SharedIndexInformer`/`DeltaFIFO` | `utils/watch_ext.rs`, `utils/reflect.rs` |
| Finalizers | **Yes** | `finalizer` module ("Finalizer helper for Controller reconcilers"); `ResourceExt::finalizers()` |
| Owner references | **Yes** | `Resource::owner_ref()` / `Resource::controller_owner_ref()` generate `OwnerReference`; `Controller::owns()` watches children by owner-ref |
| Retry / backoff | **Yes** | `utils/stream_backoff.rs`, `utils/backoff_reset_timer.rs`, `Controller::trigger_backoff()` (default "follows client-go conventions"); per-error requeue via the `error_policy` callback returning `Action` |
| Event recorder | **Yes** | `events` module (`Recorder`) |
| Graceful shutdown | **Yes** | `shutdown_on_signal()`, `graceful_shutdown_on()` |
| Related-object mapping | **Yes** | `Controller::watches(api, cfg, mapper)` |
| Wait-for-condition | **Yes** | `wait` module |
| **Leader election** | **NO** | Not present. `kube-runtime/src/` contains only `controller/`, `events.rs`, `finalizer.rs`, `reflector/`, `scheduler.rs`, `utils/`, `wait.rs`, `watcher.rs` |

So **hypothesis 3 is confirmed except for leader election**, which is explicitly out of scope:
"At the moment, leader election support is not supported by `kube` itself, and requires 3rd party
crates (see [kube#485](https://github.com/kube-rs/kube/issues/485))"
([availability](https://kube.rs/controllers/availability/)). The docs' own recommendation is to
run **a single replica** and accept eventual consistency, which is fine for a lab and is
arguably the more instructive default anyway (it forces you to reason about the eventual-consistency
model rather than hide behind a lease).

Note also `kube::runtime::scheduler` is **not** a Kubernetes scheduler — it is a
"delays and deduplicates Stream items" utility (the requeue debouncer). Do not let that name
confuse the scheduler phase of the curriculum.

**Production users — hypothesis 4 confirmed and extended.** Stackable is real, but it is far
from the only one. From [kube.rs/adopters](https://kube.rs/adopters/), spot-verified:

- **Linkerd** — `linkerd2/policy-controller` is Rust on kube-rs. Verified directly: the Linkerd
  workspace `Cargo.toml` on `main` declares `kube = { version = "3.1", default-features = false }`
  ([linkerd2/Cargo.toml](https://github.com/linkerd/linkerd2/blob/main/Cargo.toml)), repo last
  pushed 2026-08-17, 11.4k stars. This is the strongest single precedent: a CNCF **Graduated**
  project shipping a kube-rs controller in the data path of production service meshes.
- **Stackable** — a whole family of operators (Kafka, ZooKeeper, HDFS, …)
  ([stackabletech](https://github.com/stackabletech)). Confirmed.
- **Kubewarden** (CNCF policy engine), **Akri** (CNCF edge device interface),
  **bottlerocket-update-operator** (AWS), **Vector** (Datadog), **mirrord** (MetalBear),
  **tembo-operator**, **SimKube**, **Cluster API Addon Provider Fleet** (Rancher),
  **gateway-api** crate (Gateway API bindings), **blixt** (Kong L4 LB).
- Companies self-listed: AWS, Buoyant, Datadog, Stackable, Bitnami, Materialize, TrueLayer,
  Kong, MetalBear, Tembo, ZURU, nais, Aptakube.

**Bus factor — the honest caveat.** Commit counts from the GitHub contributors API: **clux**
(Eirik Albrigtsen) ~1,614; nightkr ~348; kazk ~243; then a long tail well under 50, across ~171
total contributors. That is ~4.6× the #2 contributor. Secondary maintainers are genuinely
active, but this is a one-primary-maintainer project.

**Ecosystem crate worth knowing:** `kubert` (Linkerd's kube-rs runtime helper) supplies the
boilerplate kube-rs deliberately omits — admin server with `/ready` and `/live`, graceful
SIGTERM shutdown, Prometheus metrics, a **requeue channel**, an **HTTPS server with certificate
reloading** (explicitly "for admission controllers and API extensions"), and a **`lease`
module** for leader election ([README](https://github.com/linkerd/linkerd-kubert),
[src/](https://github.com/linkerd/linkerd-kubert/tree/main/kubert/src)). For the admission-webhook
lab this is the shortest honest path to working TLS. Caveat: docs.rs failed to build kubert
0.25.0, so read the source rather than the rendered docs. **[UNVERIFIED]**: current kubert
version in the wild — Linkerd pins `kubert 0.27.0` by git tag rather than crates.io, which
suggests crates.io may lag.

---

## 3. Aya (Rust eBPF)

**Version reality — do not assume 1.0.** Verified on crates.io: `aya` **0.14.0** (2026-06-24),
`aya-ebpf` **0.2.1** (2026-06-30), `aya-log` **0.3.0** (2026-06-24), `bpf-linker` **0.11.0**
(2026-08-12). Aya has **~3.27M all-time downloads** and is clearly alive, but it is **still
pre-1.0 after five years**, and 0.13.2 was published *and yanked* within a day (2025-11-17/18).
Release gaps are long: 0.13.1 (2024-11) → 0.14.0 (2026-06). `bpf-linker`, by contrast, releases
frequently.

**Nightly Rust is still required for the kernel-side crate.** The Aya book's setup still says
`rustup toolchain install nightly --component rust-src` alongside stable
([development](https://aya-rs.dev/book/start/development/)), and the "Become a Tier 2 Rust
Target" issue in `bpf-linker` (opened 2021) **remains open**
([bpf-linker#6](https://github.com/aya-rs/bpf-linker/issues/6)). So `bpfel-unknown-none` has not
been stabilised. **[UNVERIFIED]**: the official Rust platform-support page for the BPF target
404'd during this research, so I could not double-source the Tier-3 status from rust-lang directly
— but the book + open issue are strong evidence.

**`bpf-linker` is still a separate, LLVM-pinned install**, and the maintainers explicitly warn
off `cargo install`: building from source is "not recommended … due to dependency on specific
LLVM version, system libraries and overall complexity of getting the setup right." The
recommended path is now **`cargo binstall bpf-linker`** or a prebuilt release tarball
([README](https://github.com/aya-rs/bpf-linker/blob/main/README.md)). The book deliberately
refuses to hardcode the LLVM version because it moves.
**[UNVERIFIED]**: a search snippet claimed the current pin is LLVM 21; I could not confirm the
number from the repo. Treat the LLVM version as "look it up on the day."

**Governance — hypothesis 6 partially REFUTED.** Aya's own README shows **no** CNCF, Linux
Foundation, or eBPF Foundation affiliation ([aya-rs/aya](https://github.com/aya-rs/aya)). The
"Aya joined a foundation" intuition appears to be a conflation with **bpfman** — an eBPF program
manager *built on Aya* — which **was** accepted into CNCF at **Sandbox** on **2024-06-19**
([cncf.io/projects/bpfman](https://www.cncf.io/projects/bpfman/)). bpfman's maintainer list is
heavily **Red Hat** ([MAINTAINERS.md](https://github.com/bpfman/bpfman/blob/main/MAINTAINERS.md)),
and Dave Tucker (Red Hat) maintains both bpfman and Aya. So the institutional backing is real,
it just lives one layer downstream.

**Verified Aya users:** bpfman (CNCF Sandbox, Red Hat), **Anza** (Agave Solana validator, XDP —
[FOSDEM 2026 talk](https://fosdem.org/2026/events/attachments/T7LDUJ-aya/slides/267117/aya-2026_dixkcsr.pdf)),
**Exein/Pulsar** ([repo](https://github.com/exein-io/pulsar)), Deepfence, Bombini, and
Kubernetes-adjacent **blixt** ([awesome-aya](https://github.com/aya-rs/awesome-aya)).
**Cloudflare, Datadog and Oxide were checked and NOT confirmed** — do not cite them.

**Debian 13 trixie compatibility — verified directly, and it's good news.** Trixie released
2025-08-09 shipping the **6.12 LTS** kernel
([release announcement](https://www.debian.org/News/2025/20250809)); the `linux-image-amd64`
metapackage currently resolves to 6.12.101-1
([packages.debian.org](https://packages.debian.org/trixie/linux-image-amd64)). I read the actual
Debian kernel config for 6.12.41-1 and confirmed:

```
CONFIG_DEBUG_INFO_BTF=y            # BTF/CO-RE available — the historical distro blocker is NOT present
CONFIG_MODULE_ALLOW_BTF_MISMATCH=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_XDP_SOCKETS=y
CONFIG_BPF_UNPRIV_DEFAULT_OFF=y    # unprivileged bpf() off by default -> run as root / CAP_BPF
```

Sources: [amd64/config](https://salsa.debian.org/kernel-team/linux/-/raw/debian/6.12.41-1/debian/config/amd64/config),
[config](https://salsa.debian.org/kernel-team/linux/-/raw/debian/6.12.41-1/debian/config/config).
BTF has been Debian's default since kernel 5.10.5-1
([Debian #973870](https://bugs.debian.org/973870)).

**Practical upshot for the lab:** Debian 13 is a *good* Aya host. A CO-RE XDP packet counter or a
toy tc/cgroup-skb datapath is entirely achievable. Budget for privileged pods / root, and budget
a **separate setup session** for nightly + `bpf-linker` + LLVM before the first eBPF lab — that
setup is a lab in its own right and will eat an hour or three the first time.

**Aya learning material:** there *is* an official book with a real "Hello XDP" walkthrough plus
program-type reference chapters (probes, fentry/fexit, tracepoints, socket programs, classifiers,
cgroups, cgroup-skb, XDP, LSM) ([book](https://aya-rs.dev/book/),
[SUMMARY.md](https://github.com/aya-rs/book/blob/main/src/SUMMARY.md)). It states outright that it
"caters towards people with either some eBPF or some Rust background" and points Rust newcomers
at *The Rust Book* — it will not teach Rust. Steve Latif's community series fills the gap with a
worked per-CPU packet counter using `PerCpuArray`
([part 4](https://dev.to/stevelatif/aya-rust-tutorial-part-four-xdp-hello-world-4c85),
[part 5](https://dev.to/stevelatif/aya-rust-tutorial-part-5-using-maps-1boe)).

---

## 4. Admission webhook TLS/cert plumbing

The Rust side is genuinely easy — `kube::core::admission` gives you `AdmissionReview`,
`AdmissionRequest`, `AdmissionResponse`, and `examples/admission_controller.rs` plus
`admission_setup.sh`, `admission_controller.yaml.tpl` and `cert_check.rs` in the repo are a
complete working starting point ([examples/](https://github.com/kube-rs/kube/tree/main/examples)).

The *hard* part is the same in every language: the API server will only call an HTTPS endpoint
whose serving cert it trusts, which means either

1. `caBundle` in the `ValidatingWebhookConfiguration`/`MutatingWebhookConfiguration` populated
   from a self-signed CA (what `admission_setup.sh` does — best for teaching, because you see
   every moving part), or
2. cert-manager + `cert-manager.io/inject-ca-from` annotation (what production does), or
3. `kubert`'s HTTPS server with certificate reloading (what Linkerd does)
   ([kubert README](https://github.com/linkerd/linkerd-kubert)).

Given the map's "depth over speed" preference, option 1 first is the right call: hand-rolling the
CA and the `caBundle` teaches why webhook failures manifest as `x509: certificate signed by
unknown authority` on the *API server*, not the webhook. Note the isolated NAT'd `10.10.10.0/24`
bridge means the webhook must be reachable **in-cluster by Service DNS**, which is fine — the API
server dials it from inside. Also note that `failurePolicy: Fail` on a broken webhook can wedge the
cluster; that is a great deliberate chaos drill and a terrible accident.

There is also a strictly-easier modern alternative worth teaching *alongside* webhooks:
**CRD CEL validation** (`x-kubernetes-validations`, GA since 1.29) and **ValidatingAdmissionPolicy**.
kube-rs's own admission guide recommends CEL over webhooks "because it is much less error prone"
([admission guide](https://kube.rs/controllers/admission/)). The curriculum should have the learner
do *both* and understand why the industry is migrating.

---

## 5. Learning material availability — the genuine risk

**What exists, and it's more than expected:**

- The **controllers guide** at kube.rs is a real multi-chapter book, not a stub. Chapters:
  `intro`, `object`, `reconciler`, `application`, `relations`, `gc`, `schemas` (concepts);
  `testing`, `admission`, `streams`, `generics`, `internals` (advanced); `observability`,
  `optimization`, `manifests`, `security`, `scaling`, `availability`, `webserver` (operational)
  ([docs/controllers/](https://github.com/kube-rs/website/tree/main/docs/controllers)). Several
  chapters carry real substance (the availability chapter reasons carefully about why controllers
  can run one replica; the optimization chapter has memory-profiling graphs).
- **~57 examples** in `kube-rs/kube/examples/` covering client basics, watchers (pod/node/dynamic/
  event/multi/error-bounded), reflectors (pod/node/secret/crd), **seven CRD-derive variants**
  including `crd_derive_cel.rs` and `crd_derive_multi.rs`, `crd_apply.rs`, `admission_controller.rs`,
  dynamic API, portforward, exec/attach/cp, `secret_syncer.rs`, `shared_stream_controllers.rs`,
  and `kubectl.rs` (a mini-kubectl) ([examples/](https://github.com/kube-rs/kube/tree/main/examples)).
- **`kube-rs/controller-rs`** — the official reference controller with finalizers, status updates,
  Kubernetes Events, Prometheus metrics and optional OpenTelemetry. **Actively maintained**:
  commits through 2026-06-17, release 0.16.1 ([repo](https://github.com/kube-rs/controller-rs)).
  This is the single most valuable artefact for the build track.
- A KubeCon EU 2024 talk, "Kubernetes Controllers in Rust: Fast, Safe, Sane" (Matei David,
  Buoyant) ([sched](https://kccnceu2024.sched.com/event/1YeOR/kubernetes-controllers-in-rust-fast-safe-sane-matei-david-buoyant)).

**What does not exist, and this is the risk:**

- **No book.** There is no Rust equivalent of *Programming Kubernetes* or *Kubernetes Operators*.
  Every published operator book is Go. (Absence-based finding — no publisher statement, so a niche
  self-published title could have been missed. **[UNVERIFIED]** as a strict negative.)
- **The guide is a patterns reference, not a tutorial.** Getting Started is thin and explicitly
  punts: "See the examples directory for how to use any of these crates"
  ([getting-started](https://kube.rs/getting-started/)). The website's own build-out tracking
  issue has been **open since February 2022** with sections still incomplete
  ([website#5](https://github.com/kube-rs/website/issues/5)).
- **Nothing explains the Rust.** The reconciler page presents
  `async fn reconcile(o: Arc<K>, ctx: Arc<T>) -> Result<Action, Error>` without a word about what
  `Arc` is or why async tasks need shared ownership ([reconciler](https://kube.rs/controllers/reconciler/)).
  The generics page casually shows
  `where K: Resource<Scope = NamespaceResourceScope, DynamicType = ()> + Clone + DeserializeOwned + Debug`
  ([generics](https://kube.rs/controllers/generics/)). This is not badly written — it is written
  *for someone who already knows Rust*.
- **Third-party tutorials are dated and assume competence.** MetalBear (2023-03), Kubesimplify
  (2024-07), Shuttle (2024-10), Frankel (2021-07). Given a semver-major every ~3 months, all of
  them are stale in detail. Frankel's is the most honest datum in the whole corpus: an experienced
  developer writing "my understanding of pinning is zero, so assume that it's needed and works"
  ([blog.frankel.ch](https://blog.frankel.ch/start-rust/6/)). Kubesimplify documents the exact
  borrow-checker workaround pattern — cloning the client into a context struct — that a learner
  will hit within an hour ([kubesimplify](https://blog.kubesimplify.com/kubernetes-management-with-rust-a-dive-into-generic-client-go-controller-abstractions-and-crd-macros-with-kubers)).
- **Community support is real but not fast.** kube-rs has no dedicated Discord — it uses a channel
  inside the **Tokio** community server ([kube.rs](https://kube.rs/)). GitHub Discussions
  responsiveness is maintainer-dependent: some threads answered same-day by clux or nightkr,
  others sitting "Unanswered" for months ([discussions](https://github.com/kube-rs/kube/discussions)).

**Rust concepts kube-rs forces on you, unavoidably and mostly unexplained:** `async`/`await` and
the tokio runtime; `Arc` for shared ownership across tasks; `Stream`/`futures` (`Controller::run`
returns a stream you must consume); generic trait bounds over resource types; `thiserror`/`anyhow`
error modelling; and enough `Pin` awareness to not panic when the compiler mentions it.

**Verdict on this risk:** the material is adequate *for a Rust programmer* and thin *for a Rust
learner*. The mitigation is not "pick Go" — it's to sequence a real Rust primer **before** the
build track opens, specifically covering ownership/`Arc`, `async`/tokio, `Result`+`?`+`thiserror`,
traits and generic bounds, and iterators/streams. The map already flags "Rust primer scope" as
unspecified; this research says **it is necessary, not optional**, and should be sized at real
weeks, not a weekend. Without it, the learner will spend the operator phase fighting Rust and
learning nothing about Kubernetes — the exact failure mode "depth over speed" is meant to prevent.

---

## 6. Where Rust actively costs you depth

This is the section to argue with, because these are the real trade-offs.

1. **You will not learn client-go's informer machinery by building in Rust.** kube-rs
   deliberately re-imagines it: streams + `WatchStreamExt` + `reflector` instead of
   `SharedIndexInformer`, `DeltaFIFO`, `Indexer` and the rate-limiting `workqueue`. Those Go types
   are what you will actually read in `k/k` and in every real operator, and they encode design
   decisions (resync periods, delta compression, per-key rate limiting) that the Rust stream model
   expresses differently or not at all. **Mitigation:** treat `client-go/tools/cache` and
   `client-go/util/workqueue` as *required reading* in the controller phase even though you build
   in Rust, and explicitly diff the two designs. That diff is itself excellent internals material.

2. **The scheduler is the biggest loss.** A standalone Rust scheduler teaches watch → decide →
   POST `Binding`, which is genuinely the core insight. It teaches you **nothing** about the
   scheduling framework's actual machinery: the scheduling queue (activeQ/backoffQ/unschedulableQ),
   the node snapshot, PreFilter/Filter/PostFilter/PreScore/Score/Reserve/Permit/PreBind/Bind
   sequencing, preemption and nominated nodes, or percentage-of-nodes-to-score. Because framework
   plugins are Go-only (§1 row 8), **the only way to get that depth is reading `pkg/scheduler`
   in Go** — and, if you want to build it, writing one out-of-tree Go plugin against
   `kubernetes-sigs/scheduler-plugins`. **Recommendation:** do the Rust standalone scheduler for
   the mechanism, the Rust extender for the webhook contract, and then *read* `pkg/scheduler` and
   optionally write **one** small Go filter plugin. Breaking the "build in Rust" rule exactly once,
   here, buys disproportionate depth.

3. **The aggregated API server is simply off the table.** Building one is the single best way to
   learn API machinery — storage layers, strategies, the admission chain, OpenAPI and discovery,
   versioning and conversion, `TokenReview`/`SubjectAccessReview` delegation. There is no Rust
   path (§1 row 15). **Mitigation:** read `k8s.io/apiserver` and `sample-apiserver`, and get the
   equivalent lessons from CRDs + conversion webhooks + admission webhooks in Rust, which cover
   versioning/conversion and admission but not storage or discovery.

4. **No kubebuilder/controller-runtime literacy.** Every operator job posting and every CNCF
   operator you will read assumes `controller-gen`, `envtest`, `Reconcile(ctx, req)`, and the
   kubebuilder project layout. Building only in Rust means never touching any of it. That is
   partly the *point* — hand-wiring a reconcile loop demystifies more than scaffolding one — but
   it is a real gap. **Mitigation:** one deliberately small kubebuilder operator, late, purely for
   literacy, after the Rust one exists. You will appreciate what it generates instead of being
   mystified by it.

5. **CSI and device plugins put you on an unpaved road.** CSI has a Rust precedent (Mayastor) but
   no shared bindings crate; device plugins have **no** Rust precedent at all. You will spend real
   time on `tonic-build` and proto vendoring rather than on storage or device semantics. If the
   goal is "understand CSI's Identity/Controller/Node split and the sidecar contract," the fastest
   honest route may be reading a Go driver and writing only the **Node** service in Rust.

6. **`schemars` hides structural-schema rules.** The derive generates a valid schema for you, which
   means you never confront `x-kubernetes-preserve-unknown-fields`, pruning, or why untagged enums
   and free-form maps are painful — until they bite. **Mitigation:** always `kubectl get crd -o yaml`
   the generated CRD and read it line by line. Also note the transitive `JsonSchema` requirement and
   the "conformance rewriter for structural schemas" caveat ([schemas](https://kube.rs/controllers/schemas/)).

7. **Lab-constraint risk, flagged as judgment rather than sourced fact.** `factory` has 6 cores at
   1.7 GHz base and ~9.9 GB available, and default guests are 2 cores / 1 GB / 5 GB. A cold
   `cargo build` of a kube-rs project pulls in tokio, hyper, rustls, serde, schemars and
   `k8s-openapi` — `k8s-openapi` in particular is a very large generated crate. Compiling that
   inside a 1 GB VM is likely to be slow at best and OOM at worst. **Recommendation:** build Rust
   artefacts on the Mac or on `hopper` with a warm cargo cache, ship **container images or static
   binaries** into the cluster, and never make "wait for rustc" part of a lab's critical path.
   Size any VM that must compile Rust at 4 GB+ — which, against a 9.9 GB ceiling, is itself an
   argument for cross-building off-cluster. I have **not** benchmarked this; treat it as a design
   caution to validate early, ideally in the very first Rust lab, before the curriculum commits.

---

## 7. Recommended language split (proposal, not a decision)

| Build in **Rust** | Build in **Go** (deliberate exceptions) | **Read** only, don't build |
|---|---|---|
| CRDs + operator/reconciler (the spine of the build track) | One out-of-tree kube-scheduler **framework plugin** (`scheduler-plugins`) | `k8s.io/apiserver` / aggregated API server |
| Validating + mutating admission webhooks | One tiny **kubebuilder** operator, late, for ecosystem literacy | `client-go/tools/cache` + `util/workqueue` (contrast with kube-rs streams) |
| CRD conversion webhook (multi-version) | | `pkg/scheduler` internals |
| Standalone custom scheduler (`schedulerName` + `Binding`) | | Existing Go CSI driver, as the reference |
| Scheduler **extender** webhook | | kubelet internals |
| CNI plugin (netns/veth work is the real lesson) | | |
| eBPF programs with Aya (XDP counter → toy datapath) | | |
| kubectl plugin (cheap early win, builds Rust confidence) | | |
| CSI **Node** service (optionally full driver) | | |

---

## 8. Open questions / things to re-verify before Phase 1

- Exact LLVM version `bpf-linker` 0.11 pins, and whether `cargo binstall` works cleanly on
  Debian 13 trixie. **[UNVERIFIED]**
- Whether `bpfel-unknown-none` has moved off nightly by the time the eBPF phase starts — recheck
  [bpf-linker#6](https://github.com/aya-rs/bpf-linker/issues/6).
- Real `cargo build` wall-clock and peak RSS for a `kube` + `k8s-openapi` project on `factory`-class
  hardware. Unmeasured; blocks the VM-sizing decision for any Rust lab.
- Whether `kube` 5.0 (expected ~2026 Q4 for Kubernetes 1.37, by their 3-month major policy) breaks
  anything the curriculum depends on. Pin a major and note the expected churn.
- `kubert` crates.io currency vs Linkerd's git pin, and whether `kubert::lease` is the right
  leader-election recommendation vs `kube-lease-manager`. **[UNVERIFIED]**
- Whether DatenLord is still actively maintained (could not obtain last-commit date). **[UNVERIFIED]**
