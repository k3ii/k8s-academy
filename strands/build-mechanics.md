# Build mechanics

Eleven Go artifacts across five phases, one workflow decided once: two stages per
artifact, one guest that compiles them, one registry, one identity convention, one
sizing rule, and a named gate per artifact.

Settled in [#12](https://github.com/k3ii/k8s-academy/issues/12). The measurements in
[Measured, not estimated](#measurements) are reproducible from
[`../research/build-footprints/`](../research/build-footprints/).

The learner's code lives in `build/NN-artifact/` as real Go modules in this repo, with
notes in `journal/NN-name.md` — so P4's hand-wired-versus-`kubebuilder` comparison is
literally a `git diff`.

<a id="two-stages"></a>
## Two stages, and which artifacts get both

**Every artifact that can run outside the cluster is developed that way first, then
re-shipped inside it.** Stage 1 is an edit/run loop measured in seconds. Stage 2 adds
ServiceAccount, ClusterRole, leader election, image plumbing and resource sizing as a
deliberate second exercise rather than a tax paid on every keystroke.

**The API server cannot tell the difference, which is the point: stage 1 is not a
simulation.**

<a id="artifact-table"></a>
| Artifact | Phase | Stage 1 — outside | Stage 2 — inside |
|---|---|---|---|
| Scheduler from scratch | P5 | `go run ./cmd/... --kubeconfig` | ✔ leader election, `schedulerName` |
| Scheduler framework plugin | P5 | second scheduler, `KubeSchedulerConfiguration` | ✔ |
| Operator, hand-wired `client-go` | P4 | `go run`, informers against the real API | ✔ |
| Operator, `kubebuilder` | P4 | `make run` | ✔ |
| Webhook ×3 | P3 | **`clientConfig.url`** pointing at `forge` | ✔ **`clientConfig.service`** |
| `kubectl` plugin | P3 | it is a client binary | — never has a stage 2 |
| CNI plugin | P7 | none — on-node only | ✔ |
| eBPF program | P7 | none — on-node only | ✔ |
| CSI driver | P8 | `csi-sanity` over a UNIX socket | ✔ with the sidecars |

Two rows are worth more than their width.

**The webhooks get a real stage 1 only because [`forge`](#forge) is on the lab
bridge.** `ValidatingWebhookConfiguration.clientConfig` is a union: `service` for
in-cluster, or **`url`** for anything the API server can dial. Stage 1 sets
`url: https://forge.lab:8443`, so the API server calls a `go run` process on the build
guest and the whole admission path is live while the code is still being edited. Stage
2 switches to `service` and discovers what that swap actually costs — Service,
Endpoints, in-cluster DNS, a cert with the right SANs. **The two halves of
`clientConfig` are the same lesson from both sides**, and it is only available because
`forge` sits on `10.10.10.0/24` rather than behind the bastion.

**CSI's stage 1 is the harness.** `csi-sanity` drives the driver over `/tmp/csi.sock`
with no Kubernetes present at all, which is also how P8 gates it. The gate and the fast
loop are the same tool; the sidecars arrive at stage 2.

**The `kubectl` plugin is the odd one out and the phase file should say so** rather
than let the learner notice. P3 builds four artifacts and one of them never practises
deployment mechanics at all, because it is a client binary. That is correct, not an
omission.

<a id="forge"></a>
## `forge` — the build guest

**A dedicated Debian 13 guest, `forge`, at 1536MB / 2c / 25G, at `10.10.10.125`,
never part of any cluster and never torn down** — and therefore
[never a node in a topology](lab-topologies.md#build-guest), only co-resident with one.

| Holds | Why there |
|---|---|
| Go toolchain, `GOMODCACHE`, `GOCACHE` | Survives every teardown. The k/k module graph is not something to re-download per phase. |
| clang, libbpf headers, target BTF | The eBPF artifact's C half needs them, and they must match the nodes' kernel — [kernel lockstep](#kernel-lockstep). |
| `docker` + `buildx`, and the [registry](#registry) container | It is the machine that pushes. Docker stays off a PVE host. |
| The stage-1 process itself | `go run`, and the `url:`-mode webhook the API server dials. |

**Why not the control plane of whatever topology is up**, which was the more literal
reading of "build where it runs": the cache dies at every teardown, and build RAM
competes with the cluster being studied. `forge` is the same OS, same kernel and same
architecture as the nodes, so fidelity survives; only co-tenancy is given up, and
co-tenancy was the part that cost something.

**Why 1536MB rather than 2048MB.** The
[spendable figure is ~9.5GB](lab-topologies.md#ceiling), and `ha` at 7.5GB had already
spent the margin. Totals are quoted from [the topology
table](lab-topologies.md#topologies), which owns them; the arithmetic is what is being
argued here:

| Topology | + `forge` 1536MB | Margin in 9.5GB |
|---|---|---|
| [`ha`](lab-topologies.md#ha) 7.5GB | 9.0GB | 0.5GB |
| [`workhorse`](lab-topologies.md#workhorse) 7.0GB | 8.5GB | 1.0GB |
| [`platform`](lab-topologies.md#platform) 6.0GB · [`nested`](lab-topologies.md#nested) 6.0GB | 7.5GB | 2.0GB |
| [`pair`](lab-topologies.md#pair) 5.0GB | 6.5GB | 3.0GB |
| [`solo`](lab-topologies.md#solo) 4.0GB | 5.5GB | 4.0GB |
| [`etcd-only`](lab-topologies.md#etcd-only) 3.0GB · [`k0s-light`](lab-topologies.md#k0s-light) 2.0GB | 4.5GB · 3.5GB | 5.0GB+ |

At 2048MB, `ha` plus `forge` commits all 9.5GB with nothing spare — and with
`balloon 0` there is no reclaim, so staying under budget rather than trusting the
6.1GB of swap is binding. 1536MB keeps "always up" **literally** true for every
topology in the table, which is what makes the persistent cache worth having.

> **`forge` is 1536MB by default and 2560MB for the two builds that link a Kubernetes
> binary with its debug information kept: [P3's apiserver](#p3-raise) and [P5's
> schedulers](#p5-split).** Up at the start of each and back down in its teardown — a
> `qm set` and a reboot four times in the curriculum, not twice. `GOMODCACHE` and
> `GOCACHE` are on disk and do not notice.

Because 1536MB is **not** enough to link `cmd/kube-scheduler` with DWARF kept — see
[the measurements](#measurements) — and `cmd/kube-apiserver` is the larger binary, so
**1535 MiB is a floor for it rather than an estimate of it.** That last step is
inferred: the apiserver link has never been sampled, and the honest form of the claim
is *at least as large*, which is all the sizing decision needs.

Every artifact in [the table above](#artifact-table) fits with room to spare — the
operator and webhook shape, five of the eleven, peaks at 564 MiB, and the phases that
build them (P3, P4, P7, P8) run beside `pair`, leaving 3.0GB. **What does not fit is
not an artifact at all**: it is the two phases that compile a Kubernetes component in
order to read it from the inside.

<a id="p3-raise"></a>
### P3 raises it once, with nothing else up

P3 compiles `cmd/kube-apiserver` with `-gcflags=all="-N -l"` so that it can be stepped
through under a debugger, which is the same DWARF-heavy link as P5's schedulers and does
not fit 1536MB either. The resemblance ends there: **P3's first three modules need no
topology at all**, so the raise is taken while the ceiling is otherwise empty, and the
guest stays at 2560MB for the rest of the phase.

| P3 modules | Topology | `forge` | Total | Margin |
|---|---|---|---|---|
| Hand-start and instrument an apiserver | **none** | **2560MB** | 2.5GB | 7.0GB |
| From the first provision to the capstone | [`pair`](lab-topologies.md#pair) 5.0GB | **2560MB** | 7.5GB | 2.0GB |

The first row is the argument for deferring that provision rather than a consequence of
it: the build that wants the largest `forge` in the curriculum is also the one build
that can have the machine to itself. The capstone's teardown puts the guest back to
1536MB, so the raise does not follow P3 into P4, whose two operators are the 564 MiB
shape and have never needed it.

<a id="p5-split"></a>
### P5 splits its lab

P5 is assigned [`workhorse`](lab-topologies.md#workhorse) (7.0GB) because *"scoring across two nodes teaches almost
nothing"* — but `workhorse` plus a 2560MB `forge` is the entire budget with zero
margin. This cannot be dodged by compiling before the cluster is provisioned, because
**stage 1 *is* `go run`, which links on every iteration**: the peak is needed
repeatedly, with the cluster up.

The resolution comes from inside that justification rather than against it. The third
node exists for *scoring*; the two build artifacts do not need it.

| P5 modules | Topology | `forge` | Total | Margin |
|---|---|---|---|---|
| Build the two schedulers | `pair` 5.0GB | **2560MB** | 7.5GB | 2.0GB |
| Scoring, preemption, topology spread | `workhorse` 7.0GB | 1536MB | 8.5GB | 1.0GB |

The image built in the first half is pushed to the registry on `forge` and simply run
in the second, so **nothing is compiled while `workhorse` is up**. The phase now
separates *building a scheduler* from *watching one make decisions at scale*, which
were always two different exercises sharing a topology out of convenience.

**Disk is tighter than RAM here.** `workhorse` at 65G plus `forge` at 25G is 90G of
95G, so **cache eviction is part of teardown discipline, not optional hygiene**:
`go clean -modcache` and `docker system prune` belong in the teardown runbook alongside
`tofu destroy`. The `workhorse` phases are where forgetting costs a failed provision.

<a id="kernel-lockstep"></a>
## `forge` must track the nodes' kernel

**The one way a dedicated build guest could quietly reintroduce the failure it was
meant to avoid.** CO-RE resolves against `/sys/kernel/btf/vmlinux`. If `forge` drifts
to a different Debian 13 kernel than the lab guests, the eBPF artifact compiles
against BTF for a kernel it will never attach to — which is precisely why
"cross-compile everything on the Mac" was rejected, re-entering through the back door.

The convention: `forge` is provisioned from the same template as the nodes, its kernel
is pinned in lockstep, and **`uname -r` on `forge` and on a lab node is compared before
the eBPF module starts.**

```sh
ssh forge  uname -r
ssh node-1 uname -r    # these must match, and a mismatch is a stop-and-fix
```

A mismatch is a stop-and-fix, not a warning. The failure it prevents is either a
verifier rejection or a **silently wrong field offset**, and the second one is much
worse than the first. The [chaos strand](chaos.md#borrowed-drills) takes the deliberate
mismatch as a drill.

<a id="registry"></a>
## Images reach the nodes through one registry, outside the cluster

`registry:3.0.0` as a container on `forge`, so it costs the cluster nothing and works
identically on one, two or three nodes.

```
build   docker buildx build --platform linux/amd64 \
          -t forge.lab:5000/toy-scheduler:v3 --push .
nodes   containerd insecure-registry entry, Ansible-managed
```

The alternative — `docker save`, `scp` through the bastion, `ctr -n k8s.io images
import` on each node — is zero-infrastructure but is per-node manual work, and it
degrades exactly where the build track needs it most: a DaemonSet artifact (the CNI
plugin, the CSI node plugin, the eBPF loader) on `pair` or `workhorse` means doing it
on every node, every iteration.

**But the node-side trust plumbing is not skipped.** Configuring containerd to pull
from an insecure registry is a legible piece of trust configuration and it stays
visible in Ansible rather than hidden. And **the `ctr import` path is done by hand
exactly once**, so that when an image fails to arrive, the content-addressed store is
somewhere the learner has already been.

<a id="base-image"></a>
## `scratch`, with one distroless artifact for contrast

```dockerfile
FROM scratch
COPY toy-scheduler /toy-scheduler
ENTRYPOINT ["/toy-scheduler"]
```

~12MB. No shell, no CA bundle, no `/etc/nsswitch.conf`. `kubectl exec` fails with
`exec: "sh": not found`, and the way in is:

```sh
kubectl debug -it <pod> --image=busybox --target=toy-scheduler
```

— an ephemeral container sharing the process namespace, which is **a mechanism worth
needing rather than reading about.**

One artifact ships `gcr.io/distroless/static:nonroot` instead, so the difference
between "empty" and "deliberately minimal but debuggable" is felt: +2MB for a CA
bundle, tzdata and a nonroot UID, still no shell. **The artifact that gets distroless
should be one that actually needs the CA bundle** — an outbound TLS call to something
outside the cluster makes `x509: certificate signed by unknown authority` the *reason*
for the change rather than an illustration of it. Which artifact that is, is a
phase-file decision.

<a id="identity"></a>
## Identity, per artifact

Namespace `academy-build`. **One ServiceAccount and one hand-written least-privilege
ClusterRole per artifact** — not a shared build-track identity, because the
least-privilege exercise is CKS material the curriculum wants anyway, and an
over-broad grant is only visible if the grants are separate.

```sh
kubectl auth can-i list pods \
  --as=system:serviceaccount:academy-build:toy-scheduler
```

That command is the check, and it is falsifiable: run it for a verb the artifact should
*not* have and the expected answer is `no`.

<a id="sizing"></a>
## Sizing, per artifact

`resources: {}` is a live hazard on this node — it disqualified Argo CD and forced a
non-optional `DeploymentRuntimeConfig` override on Crossplane's function pods. Eleven
of these pods are the learner's own, so the same standard applies to the curriculum's
own output:

- **A memory request, always** — taken from `kubectl top pod` during stage 1 rather
  than guessed.
- **A memory limit is a decision that gets written down**, per artifact, with the
  reason. The sharpest finding behind this rule was not that limits are good but that
  a 16× request-to-limit ratio is a lie about the working set. So *"limit equals
  request"* and *"no limit, and here is why"* are both acceptable answers. **"No limit
  because the chart didn't have one" is not.**
- **No artifact ships `resources: {}`.**

<a id="webhook-tls"></a>
## Webhook TLS: `openssl` first, `cert-manager` second

**Webhook 1 is hand-certed end to end** — generate a CA, sign a serving cert with the
right SANs, base64 the CA into `caBundle` by hand. Then **break it on purpose**: change
one SAN, watch admission fail, read the API server log, and recognise `x509:
certificate signed by unknown authority` from the inside.

**Webhook 2 uses `cert-manager`** — a `Certificate` plus the `ca-injector` annotation
that writes `caBundle` for you — which now reads as automation of a shape already
understood rather than an annotation that works for unexamined reasons. Webhook 3 takes
whichever fits its phase.

The drill this hands to the [chaos strand](chaos.md#borrowed-drills): corrupt the
`caBundle` on a working webhook and diagnose it from the API server logs alone. With
`failurePolicy: Fail` that is an outage, which is the honest version — a broken
admission webhook can wedge a cluster, and this is where wedging one costs nothing.

<a id="gates"></a>
## What "done" means, per artifact

**Name the real harness where one exists rather than inventing a uniform bar.** Six of
eleven have one; the remaining five fall to the falsifiable-claim tier — a `file:line`
claim a hostile reader could check and find wrong.

| Artifact | Gate | Kind |
|---|---|---|
| CSI driver | `csi-sanity --csi.endpoint=/tmp/csi.sock` | objective harness |
| Scheduler framework plugin | upstream framework test helpers | objective harness |
| Operator, hand-wired | **`envtest`** — a real apiserver and etcd, locally | objective harness |
| Operator, `kubebuilder` | **`envtest`** | objective harness |
| eBPF program | the verifier accepts it, or it does not | objective, and free |
| CNI plugin | `cnitool` `ADD`/`DEL` against a netns | objective harness |
| Scheduler from scratch | falsifiable written claim | tier 2 |
| Webhook ×3 | falsifiable written claim | tier 2 |
| `kubectl` plugin | falsifiable written claim | tier 2 |

**`envtest` is the addition worth flagging.** A hand-wired `client-go` controller had
no objective gate at all. `sigs.k8s.io/controller-runtime/pkg/envtest` runs genuine
`kube-apiserver` and `etcd` binaries out-of-cluster, so the reconciler is tested
against real API semantics — optimistic concurrency, watch delivery, defaulting,
validation — rather than a fake client that agrees with whatever the code does. It also
means **both operators are gated by the same harness**, which is what makes the
hand-wired-versus-`kubebuilder` `git diff` a comparison rather than an anecdote.

A learner-written test suite was considered and rejected **as the gate**: a suite you
wrote can be as weak as you like, so it is good practice and bad evidence.

<a id="measurements"></a>
## Measured, not estimated: what a build actually costs

Sampling **aggregate** RSS across the whole toolchain process tree — the driver,
`compile`, `link`, `asm` — because what OOMs a small guest is the sum. Parallelism
pinned to `forge`'s 2 cores, `CGO_ENABLED=0 GOOS=linux GOARCH=amd64`, Go 1.26.5.

| Build | Cache | Peak aggregate RSS | Wall |
|---|---|---|---|
| controller-runtime manager + webhook — *stands in for both operators and all three webhooks* | cold | **564 MiB** | 43s |
| `k8s.io/kubernetes/cmd/kube-scheduler` — *stands in for both P5 artifacts* | cold | 1076 MiB (**undercounted** — see below) | 64s |
| `kube-scheduler`, **link step only**, DWARF kept | warm | **1535 MiB** | 5s |
| `kube-scheduler`, link only, `-ldflags="-s -w"` | warm | 1177 MiB | 3s |

**Three things this measurement taught that an estimate would have got wrong.**

**1. The link is the peak, not the compile fan-out.** The first cold run reported
1076 MiB and **that number is wrong** — sampling at 1Hz across a 64-second build missed
a spike lasting a few seconds. Re-sampling at 5Hz against a warm cache, where nothing
*but* the link runs, gives 1535 MiB. The methodological point is worth keeping:
**`/usr/bin/time -l` reports the largest single child's RSS, and a Go build forks dozens
of `compile` processes** — so the aggregate has to be sampled across the process tree.

**2. `-p` is not a lever.** The link is a single process. Reducing build parallelism
reduces the *compile* phase's aggregate, which was never the constraint. Anyone sizing
a build guest by throttling `-p` is tuning the wrong number.

**3. Neither is `GOGC`.** The linker's *live* set is the constraint, not garbage it is
failing to collect:

| `GOGC` | Link peak, DWARF kept |
|---|---|
| 100 (default) | 1510 / 1535 MiB across two runs |
| 50 | **1352 MiB** |
| 25 | 1426 MiB — *worse* than 50 |

Roughly 10% at best, then it goes backwards, and identical configurations vary by
~25 MiB run to run. So `GOGC=50` is worth setting and is not worth relying on.

**Caveats, stated rather than buried.** Measured on darwin/arm64 cross-linking to
linux/amd64; a native linux/amd64 link could differ, though not by the ~400 MiB that
would change any conclusion. And the P5 plugin builds against
`kubernetes-sigs/scheduler-plugins` rather than `k/k` directly — but that project's
output *is* a `kube-scheduler` binary with extra plugins linked in, over the same
staging-repo module graph, so `cmd/kube-scheduler` is the right proxy and if anything a
slight underestimate.

<a id="open"></a>
## Open, and where it bites

- **Re-measure the native link peak on `forge` itself**, before P5 begins — it is the
  number the 2560MB resize rests on, and a five-minute check on first boot. Run
  [`link-peak.sh`](../research/build-footprints/link-peak.sh) on the guest. **If a
  native link exceeds ~2.2GB, 2560MB is not enough and `-s -w` becomes mandatory.**
- **The `ha`-plus-`forge` margin is 0.5GB**, which is thin. If `ha` needs its full
  7.5GB in practice, `forge` stops for that topology and the cache survives the pause —
  a fallback, not the plan.
- **The eleven artifacts have a directory layout and no module convention.** This doc
  puts the learner's code in `build/NN-artifact/`, and the thirteen `labs/` directories
  kept to it — fourteen such paths are cited, from `build/00-scratch` to
  `build/08-csi-driver`, with no session inventing a second shape. What no ruling covers
  is what goes *inside*: the module path each `go.mod` declares, whether `cmd/` is
  mandatory for a single-binary artifact, and the invocation the acceptance harness is
  run by. Thirty-nine exercises carry a `**Build**` key and only two state a module path
  at all, both of them `probe` for a throwaway. It bites at the second artifact, not the
  first: P4's two operators are built to be diffed against each other, and P5's plugin
  is meant to be carried onto the scheduler binary from earlier in the same phase. A
  convention chosen after eleven `go.mod` files exist is eleven edits; chosen before the
  first, it is one paragraph. Left open on purpose when
  [map #29](https://github.com/k3ii/k8s-academy/issues/29) closed: the exercise *shape*
  is settled by two prototypes, and the scaffold has no evidence behind it yet, because
  no artifact in this curriculum has been built.
