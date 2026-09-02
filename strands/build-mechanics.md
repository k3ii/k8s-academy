# Build mechanics

The curriculum builds eleven Go artifacts across five phases. It decides the workflow once,
and the decision has six parts: two stages per artifact, one guest that compiles them, one
registry, one identity convention, one sizing rule, and a named gate per artifact.

This was settled in [#12](https://github.com/k3ii/k8s-academy/issues/12). The measurements in
[Measured, not estimated](#measurements) are reproducible from
[`../research/build-footprints/`](../research/build-footprints/).

The learner's code lives in `build/NN-artifact/`, as real Go modules in this repo. The notes
live in `journal/NN-name.md`. P4 therefore compares a hand-wired operator against a
`kubebuilder` operator with a literal `git diff`.

<a id="two-stages"></a>
## Two stages, and which artifacts get both

**Every artifact that can run outside the cluster is developed that way first. Then it is
re-shipped inside the cluster.** Stage 1 is an edit-and-run loop that is measured in seconds.
Stage 2 adds the ServiceAccount, the ClusterRole, leader election, image plumbing and
resource sizing. Stage 2 is a deliberate second exercise, and not a tax that you pay on every
keystroke.

**The API server cannot tell the difference between the two stages. That is the point: stage
1 is not a simulation.**

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

**The webhooks get a real stage 1 for one reason: [`forge`](#forge) is on the lab bridge.**
`ValidatingWebhookConfiguration.clientConfig` is a union. It takes `service` for an
in-cluster target, or **`url`** for anything that the API server can dial. Stage 1 sets `url:
https://forge.lab:8443`. The API server then calls a `go run` process on the build guest, so
the whole admission path is live while you are still editing the code. Stage 2 switches to
`service`, and it discovers what that swap actually costs: a Service, Endpoints, in-cluster
DNS, and a cert with the right SANs. **The two halves of `clientConfig` are the same lesson
from both sides.** That lesson is only available because `forge` sits on `10.10.10.0/24`,
rather than behind the bastion.

**The stage 1 of CSI is the harness.** `csi-sanity` drives the driver over `/tmp/csi.sock`,
with no Kubernetes present at all. That is also how P8 gates it. So the gate and the fast
loop are the same tool. The sidecars arrive at stage 2.

**The `kubectl` plugin is the odd one out, and the phase file should say so** instead of
letting the learner notice it. P3 builds four artifacts, and one of them never practises
deployment mechanics at all, because it is a client binary. That is correct, and it is not an
omission.

<a id="forge"></a>
## `forge` — the build guest

**`forge` is a dedicated Debian 13 guest, at 1536MB, 2 cores and 25G, on `10.10.10.125`. It
is never part of any cluster, and it is never torn down.** It is therefore
[never a node in a topology](lab-topologies.md#build-guest). It is only ever co-resident with
one.

| Holds | Why there |
|---|---|
| The Go toolchain, `GOMODCACHE` and `GOCACHE` | They survive every teardown. The module graph of k/k is not something to re-download per phase. |
| clang, the libbpf headers, and the target BTF | The C half of the eBPF artifact needs them. They must also match the kernel of the nodes. See [kernel lockstep](#kernel-lockstep). |
| `docker` with `buildx`, and the [registry](#registry) container | This is the machine that pushes. Docker stays off a PVE host. |
| The stage-1 process itself | That means `go run`, and the `url:`-mode webhook that the API server dials. |

**Why not the control plane of whatever topology is up?** That was the more literal reading
of "build where it runs". It fails for two reasons. The cache dies at every teardown. And
build RAM competes with the cluster that you are studying. `forge` has the same OS, the same
kernel and the same architecture as the nodes, so fidelity survives. You give up co-tenancy
only, and co-tenancy was the part that cost something.

**Why 1536MB rather than 2048MB.** The [spendable figure is about 9.5GB](lab-topologies.md#ceiling),
and `ha` at 7.5GB had already spent the margin. The totals below are quoted from
[the topology table](lab-topologies.md#topologies), which owns them. The arithmetic is what
is being argued here:

| Topology | + `forge` 1536MB | Margin in 9.5GB |
|---|---|---|
| [`ha`](lab-topologies.md#ha) 7.5GB | 9.0GB | 0.5GB |
| [`workhorse`](lab-topologies.md#workhorse) 7.0GB | 8.5GB | 1.0GB |
| [`platform`](lab-topologies.md#platform) 6.0GB · [`nested`](lab-topologies.md#nested) 6.0GB | 7.5GB | 2.0GB |
| [`pair`](lab-topologies.md#pair) 5.0GB | 6.5GB | 3.0GB |
| [`solo`](lab-topologies.md#solo) 4.0GB | 5.5GB | 4.0GB |
| [`etcd-only`](lab-topologies.md#etcd-only) 3.0GB · [`k0s-light`](lab-topologies.md#k0s-light) 2.0GB | 4.5GB · 3.5GB | 5.0GB+ |

At 2048MB, `ha` plus `forge` commits all 9.5GB, with nothing spare. And with `balloon 0`
there is no reclaim, so staying under budget is binding. Do not trust the 6.1GB of swap.
1536MB keeps "always up" **literally** true for every topology in the table, and that is what
makes the persistent cache worth having.

> **`forge` is 1536MB by default. It is 2560MB for the two builds that link a Kubernetes
> binary and keep its debug information: [the apiserver in P3](#p3-raise) and [the schedulers
> in P5](#p5-split).** It goes up at the start of each phase, and back down in that phase's
> teardown. That is a `qm set` and a reboot four times in the curriculum, and not twice.
> `GOMODCACHE` and `GOCACHE` are on disk, and they do not notice.

The raise is needed because 1536MB is **not** enough to link `cmd/kube-scheduler` with DWARF
kept. See [the measurements](#measurements). And `cmd/kube-apiserver` is the larger binary,
so **1535 MiB is a floor for it, rather than an estimate of it.** That last step is inferred.
The apiserver link has never been sampled, so the honest form of the claim is *at least as
large*, and that is all that the sizing decision needs.

Every artifact in [the table above](#artifact-table) fits with room to spare. The operator
and webhook shape covers five of the eleven artifacts, and it peaks at 564 MiB. The phases
that build them are P3, P4, P7 and P8, and they run beside `pair`, which leaves 3.0GB.
**What does not fit is not an artifact at all.** It is the two phases that compile a
Kubernetes component in order to read it from the inside.

<a id="p3-raise"></a>
### P3 raises it once, with nothing else up

P3 compiles `cmd/kube-apiserver` with `-gcflags=all="-N -l"`, so that you can step through it
under a debugger. That is the same DWARF-heavy link as the schedulers of P5, and it does not
fit 1536MB either. The resemblance ends there. **The first three modules of P3 need no
topology at all.** So the raise is taken while the ceiling is otherwise empty, and the guest
then stays at 2560MB for the rest of the phase.

| P3 modules | Topology | `forge` | Total | Margin |
|---|---|---|---|---|
| Hand-start and instrument an apiserver | **none** | **2560MB** | 2.5GB | 7.0GB |
| From the first provision to the capstone | [`pair`](lab-topologies.md#pair) 5.0GB | **2560MB** | 7.5GB | 2.0GB |

Read the first row as the argument for deferring that provision, and not as a consequence of
it. The build that wants the largest `forge` in the curriculum is also the one build that can
have the machine to itself. The teardown of the capstone puts the guest back to 1536MB, so
the raise does not follow P3 into P4. The two operators of P4 are the 564 MiB shape, and they
have never needed it.

<a id="p5-split"></a>
### P5 splits its lab

P5 is assigned [`workhorse`](lab-topologies.md#workhorse) at 7.0GB, because *"scoring across
two nodes teaches almost nothing"*. But `workhorse` plus a 2560MB `forge` is the entire
budget, with zero margin. You cannot dodge that by compiling before the cluster is
provisioned, because **stage 1 *is* `go run`, and `go run` links on every iteration.** The
peak is needed repeatedly, with the cluster up.

The resolution comes from inside that justification, rather than against it. The third node
exists for *scoring*. The two build artifacts do not need it.

| P5 modules | Topology | `forge` | Total | Margin |
|---|---|---|---|---|
| Build the two schedulers | `pair` 5.0GB | **2560MB** | 7.5GB | 2.0GB |
| Scoring, preemption, topology spread | `workhorse` 7.0GB | 1536MB | 8.5GB | 1.0GB |

The image that you build in the first half is pushed to the registry on `forge`. The second
half simply runs it. So **nothing is compiled while `workhorse` is up.** The phase now
separates *building a scheduler* from *watching one make decisions at scale*. Those were
always two different exercises, and they shared a topology out of convenience.

**Disk is tighter than RAM here.** `workhorse` at 65G plus `forge` at 25G is 90G out of 95G.
So **cache eviction is part of teardown discipline, and not optional hygiene.** Put `go clean
-modcache` and `docker system prune` in the teardown runbook, next to `tofu destroy`. The
`workhorse` phases are where forgetting that costs you a failed provision.

<a id="kernel-lockstep"></a>
## `forge` must track the nodes' kernel

**This is the one way in which a dedicated build guest could quietly reintroduce the failure
that it was meant to avoid.** CO-RE resolves against `/sys/kernel/btf/vmlinux`. Suppose that
`forge` drifts to a different Debian 13 kernel than the lab guests. The eBPF artifact then
compiles against BTF for a kernel that it will never attach to. That is precisely why
"cross-compile everything on the Mac" was rejected, and here it re-enters through the back
door.

So here is the convention. `forge` is provisioned from the same template as the nodes. Its
kernel is pinned in lockstep. And **you compare `uname -r` on `forge` and on a lab node
before the eBPF module starts.**

```sh
ssh forge  uname -r
ssh node-1 uname -r    # these must match, and a mismatch is a stop-and-fix
```

A mismatch is a stop-and-fix, and not a warning. The failure that it prevents is either a
verifier rejection or a **silently wrong field offset**, and the second one is much worse
than the first. The [chaos strand](chaos.md#borrowed-drills) takes the deliberate mismatch as
a drill.

<a id="registry"></a>
## Images reach the nodes through one registry, outside the cluster

Run `registry:3.0.0` as a container on `forge`. It then costs the cluster nothing, and it
works identically on one, two or three nodes.

```
build   docker buildx build --platform linux/amd64 \
          -t forge.lab:5000/toy-scheduler:v3 --push .
nodes   containerd insecure-registry entry, Ansible-managed
```

The alternative is `docker save`, then `scp` through the bastion, then `ctr -n k8s.io images
import` on each node. That path needs zero infrastructure, but it is per-node manual work.
And it degrades exactly where the build track needs it most. A DaemonSet artifact — the CNI
plugin, the CSI node plugin, or the eBPF loader — on `pair` or `workhorse` means doing that
work on every node, on every iteration.

**But the node-side trust plumbing is not skipped.** Configuring containerd to pull from an
insecure registry is a legible piece of trust configuration, and it stays visible in Ansible
rather than hidden. And **the `ctr import` path is done by hand exactly once.** Then, when an
image fails to arrive, the content-addressed store is somewhere that the learner has already
been.

<a id="base-image"></a>
## `scratch`, with one distroless artifact for contrast

```dockerfile
FROM scratch
COPY toy-scheduler /toy-scheduler
ENTRYPOINT ["/toy-scheduler"]
```

That image is about 12MB. It has no shell, no CA bundle and no `/etc/nsswitch.conf`.
`kubectl exec` fails with `exec: "sh": not found`. The way in is this:

```sh
kubectl debug -it <pod> --image=busybox --target=toy-scheduler
```

That is an ephemeral container, and it shares the process namespace. It is **a mechanism
worth needing, rather than a mechanism to read about.**

One artifact ships `gcr.io/distroless/static:nonroot` instead. You then feel the difference
between "empty" and "deliberately minimal but debuggable". It costs 2MB more, and it buys a
CA bundle, tzdata and a nonroot UID. It still has no shell. **The artifact that gets
distroless should be one that actually needs the CA bundle.** Give it an outbound TLS call to
something outside the cluster. Then `x509: certificate signed by unknown authority` is the
*reason* for the change, rather than an illustration of it. Which artifact that is, is a
phase-file decision.

<a id="identity"></a>
## Identity, per artifact

The namespace is `academy-build`. **Each artifact gets one ServiceAccount and one
hand-written least-privilege ClusterRole.** There is no shared build-track identity, for two
reasons. The least-privilege exercise is CKS material that the curriculum wants anyway. And
an over-broad grant is only visible if the grants are separate.

```sh
kubectl auth can-i list pods \
  --as=system:serviceaccount:academy-build:toy-scheduler
```

That command is the check, and it is falsifiable. Run it for a verb that the artifact should
*not* have, and the expected answer is `no`.

<a id="sizing"></a>
## Sizing, per artifact

`resources: {}` is a live hazard on this node. It disqualified Argo CD, and it forced a
non-optional `DeploymentRuntimeConfig` override on the function pods of Crossplane. Eleven of
these pods are the learner's own, so the same standard applies to the curriculum's own
output:

- **Always set a memory request.** Take it from `kubectl top pod` during stage 1. Do not
  guess it.
- **A memory limit is a decision, and you write the decision down**, per artifact, with the
  reason. The sharpest finding behind this rule was not that limits are good. It was that a
  16× request-to-limit ratio is a lie about the working set. So two answers are acceptable:
  *"limit equals request"*, and *"no limit, and here is why"*. **"No limit because the chart
  didn't have one" is not acceptable.**
- **No artifact ships `resources: {}`.**

<a id="webhook-tls"></a>
## Webhook TLS: `openssl` first, `cert-manager` second

**Webhook 1 is hand-certed end to end.** Generate a CA. Sign a serving cert with the right
SANs. Then base64 the CA into `caBundle` by hand. Then **break it on purpose**: change one
SAN, watch admission fail, read the API server log, and recognise `x509: certificate signed
by unknown authority` from the inside.

**Webhook 2 uses `cert-manager`.** That means a `Certificate`, plus the `ca-injector`
annotation that writes `caBundle` for you. It now reads as automation of a shape that you
already understand, rather than as an annotation that works for unexamined reasons. Webhook 3
takes whichever method fits its phase.

This section hands one drill to the [chaos strand](chaos.md#borrowed-drills). Corrupt the
`caBundle` on a working webhook, and diagnose it from the API server logs alone. With
`failurePolicy: Fail` that is an outage, and the outage is the honest version. A broken
admission webhook can wedge a cluster, and this is the place where wedging one costs nothing.

<a id="gates"></a>
## What "done" means, per artifact

**Where a real harness exists, name it. Do not invent a uniform bar.** Six of the eleven
artifacts have such a harness. The remaining five fall to the falsifiable-claim tier, which
means a `file:line` claim that a hostile reader could check and find wrong.

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

**`envtest` is the addition worth flagging.** A hand-wired `client-go` controller had no
objective gate at all. `sigs.k8s.io/controller-runtime/pkg/envtest` runs genuine
`kube-apiserver` and `etcd` binaries out-of-cluster. The reconciler is therefore tested
against real API semantics: optimistic concurrency, watch delivery, defaulting and
validation. It is not tested against a fake client that agrees with whatever the code does.
It also means that **both operators are gated by the same harness**, and that is what makes
the hand-wired-versus-`kubebuilder` `git diff` a comparison rather than an anecdote.

A learner-written test suite was considered, and it was rejected **as the gate**. A suite that
you wrote can be as weak as you like. So it is good practice, and it is bad evidence.

<a id="measurements"></a>
## Measured, not estimated: what a build actually costs

The sampling measures **aggregate** RSS across the whole toolchain process tree: the driver,
`compile`, `link` and `asm`. The reason is that what OOMs a small guest is the sum.
Parallelism was pinned to the 2 cores of `forge`, with `CGO_ENABLED=0 GOOS=linux
GOARCH=amd64`, on Go 1.26.5.

| Build | Cache | Peak aggregate RSS | Wall |
|---|---|---|---|
| controller-runtime manager + webhook — *stands in for both operators and all three webhooks* | cold | **564 MiB** | 43s |
| `k8s.io/kubernetes/cmd/kube-scheduler` — *stands in for both P5 artifacts* | cold | 1076 MiB (**undercounted** — see below) | 64s |
| `kube-scheduler`, **link step only**, DWARF kept | warm | **1535 MiB** | 5s |
| `kube-scheduler`, link only, `-ldflags="-s -w"` | warm | 1177 MiB | 3s |

**This measurement taught three things that an estimate would have got wrong.**

**1. The link is the peak. The compile fan-out is not.** The first cold run reported 1076
MiB, and **that number is wrong**. Sampling at 1Hz across a 64-second build missed a spike
that lasted a few seconds. Re-sampling at 5Hz against a warm cache, where nothing *but* the
link runs, gives 1535 MiB. The methodological point is worth keeping. **`/usr/bin/time -l`
reports the RSS of the largest single child, and a Go build forks dozens of `compile`
processes.** So you must sample the aggregate across the process tree.

**2. `-p` is not a lever.** The link is a single process. Reducing build parallelism reduces
the aggregate of the *compile* phase, and that phase was never the constraint. Anyone who
sizes a build guest by throttling `-p` is tuning the wrong number.

**3. `GOGC` is not a lever either.** The constraint is the *live* set of the linker, and not
garbage that the linker is failing to collect:

| `GOGC` | Link peak, DWARF kept |
|---|---|
| 100 (default) | 1510 / 1535 MiB across two runs |
| 50 | **1352 MiB** |
| 25 | 1426 MiB — *worse* than 50 |

That is roughly 10% at best, and then it goes backwards. Identical configurations also vary
by about 25 MiB from run to run. So `GOGC=50` is worth setting, and it is not worth relying
on.

**Two caveats, stated rather than buried.** First, this was measured on darwin/arm64,
cross-linking to linux/amd64. A native linux/amd64 link could differ, although not by the
400 MiB or so that would change any conclusion. Second, the P5 plugin builds against
`kubernetes-sigs/scheduler-plugins`, rather than against `k/k` directly. But the output of
that project *is* a `kube-scheduler` binary with extra plugins linked in, over the same
staging-repo module graph. So `cmd/kube-scheduler` is the right proxy, and if anything it is
a slight underestimate.

<a id="open"></a>
## Open, and where it bites

- **Re-measure the native link peak on `forge` itself, before P5 begins.** It is the number
  that the 2560MB resize rests on, and it is a five-minute check on first boot. Run
  [`link-peak.sh`](../research/build-footprints/link-peak.sh) on the guest. **If a native
  link exceeds about 2.2GB, then 2560MB is not enough, and `-s -w` becomes mandatory.**
- **The margin for `ha` plus `forge` is 0.5GB**, which is thin. If `ha` needs its full 7.5GB
  in practice, then `forge` stops for that topology, and the cache survives the pause. That
  is a fallback, and not the plan.
- **The eleven artifacts have a directory layout, and no module convention.** This doc puts
  the learner's code in `build/NN-artifact/`, and the thirteen `labs/` directories kept to
  it. Fourteen such paths are cited, from `build/00-scratch` to `build/08-csi-driver`, and no
  session invented a second shape. What no ruling covers is what goes *inside*. Three things
  are unspecified: the module path that each `go.mod` declares, whether `cmd/` is mandatory
  for a single-binary artifact, and the invocation that the acceptance harness is run by.
  Thirty-nine exercises carry a `**Build**` key, and only two state a module path at all.
  Both of those two say `probe`, for a throwaway. This bites at the second artifact, and not
  at the first. The two operators of P4 are built to be diffed against each other, and the
  plugin of P5 is meant to be carried onto the scheduler binary from earlier in the same
  phase. A convention that is chosen after eleven `go.mod` files exist costs eleven edits.
  Chosen before the first one, it costs one paragraph. It was left open on purpose when
  [map #29](https://github.com/k3ii/k8s-academy/issues/29) closed. The exercise *shape* is
  settled by two prototypes. The scaffold has no evidence behind it yet, because no artifact
  in this curriculum has been built.
