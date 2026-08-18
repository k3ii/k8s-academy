# Chaos

Which fault to inject, by which Linux primitive, with which tool — and which faults
no tool can express, so the drill is done by hand or not at all.

Derived from [`../research/chaos-tooling.md`](../research/chaos-tooling.md), research
date 2026-08-17, which carries the full Chaos Mesh vs Litmus comparison, the
footprint arithmetic and the project-health assessment. **Chaos Mesh is primary at
582Mi minimised; Litmus gets one comparative session on the `litmus-core` chart and
ChaosCenter is never installed.** That verdict is settled — this document is the part
a phase file links into.

<a id="principle"></a>
## The standing principle

> **Every drill is performed by hand first, and only then scripted.**

The tool's job is regression and repeatability — proving a fix holds, re-running a
scenario cheaply after a change — **not first contact with a failure mode**. A
`NetworkChaos` CR that produces a partition teaches nothing about partitions to
someone who has never watched `tc qdisc` do it. Injected by hand, the mechanism is
the lesson; injected by CR, the mechanism is hidden behind a controller.

This is also why the chaos strand carries no dedicated phase. It is spread across
eight months, and it *is* the preparation for CKA's Troubleshooting domain — the
largest single domain in any of the three exams at 30%. The two requirements
reinforce each other rather than competing for a slot.

## Which phase drills how

| Phases | How |
|---|---|
| **P0–P5** | **Hand-driven only.** `tc netem`, `iptables`, cgroup writes, `kill -9`, `dd`, `qm stop`. No chaos tool is installed. |
| **P6 onward** | Chaos Mesh arrives, and it reads as *a wrapper over the primitives from P0* rather than as magic. This ordering is the whole reason it is not installed earlier. |
| **One session, P6+** | Litmus `litmus-core`, for the [probe model](#litmus) — a concept Chaos Mesh under-teaches. |
| **Every phase** | At least one drill, because [#11](https://github.com/k3ii/k8s-academy/issues/11)'s lab stanza has a mandatory **Break it** field. That field is how "chaos is a strand, not a module" actually lands. |

A **red chaos drill blocks advancement** and may extend a phase. That is a gate
condition, unlike a cert result.

---

<a id="catalogue"></a>
## Fault catalogue

What to reach for, and what it actually does to the kernel. `CM` = Chaos Mesh CRD,
`L` = Litmus OSS fault. **A dash is not a gap in this table — it is a statement that
the tool cannot express the fault**, which is often the more useful fact.

| Fault | Chaos Mesh | Litmus (OSS) | Mechanism to teach |
|---|---|---|---|
| **Pod deleted** | `PodChaos: pod-kill` | `pod-delete` | A plain API `DELETE` with `gracePeriod: 0`. Nothing kernel-level happens; the controller reacts. |
| **Container killed** | `PodChaos: container-kill` | `container-kill` | gRPC to the runtime's `StopContainer`. The pod object survives; the restart count moves. |
| **Workload gone, pod still there** | `PodChaos: pod-failure` | — | **Rewrites the container image to `pause`.** Sustained unavailability with no deletion — the failure mode that looks healthiest in `kubectl get pods`. No Litmus analogue. |
| **Latency / loss / corruption / duplication** | `NetworkChaos: delay, loss, corrupt, duplicate` (jitter and correlation on `delay`) | `pod-network-latency`, `-loss`, `-corruption`, `-duplication` | A `netem` qdisc inside the target's netns. Visible with `tc -s qdisc show`. |
| **Bandwidth cap** | `NetworkChaos: bandwidth` | `pod-network-rate-limit` | A `tbf` qdisc. |
| **Network partition** | `NetworkChaos: partition`, `direction: to/from/both` | ⚠️ `pod-network-partition` | **CM: `iptables` + `ipset` inside the netns — CNI-independent.** Litmus instead **creates a Kubernetes `NetworkPolicy`**, so it needs a policy-enforcing CNI and silently does nothing without one. Wrong layer for teaching partitions; a good contrast to draw *against* the iptables version. |
| **DNS failure** | `DNSChaos: error \| random` (needs `chaos-dns-server`; **A/AAAA only, wildcards suffix-only**) | `pod-dns-error`, `pod-dns-spoof` | CM runs **CoreDNS with the `k8s_dns_chaos` plugin** and steers the pod's resolution to it. Makes the whole `resolv.conf` → `ndots` → search-domain path inspectable. Spoofing is Litmus-only. |
| **CPU / memory / IO contention** | `StressChaos`, `IOChaos`, `BlockChaos` | `pod-cpu-hog`, `pod-memory-hog`, `pod-io-stress`, `pod-fio-stress`, `disk-fill`, `node-*-hog` | `stress-ng` joined into the target's **existing cgroup**, so it hits the real `memory.max` and produces a **genuine OOMKill** — the pod's limits are not raised. Exactly the pressure this lab wants to observe. |
| **Filesystem lies** | `IOChaos: latency, fault, attrOverride, mistake` | — | **`toda`, a FUSE filesystem injected into the mount namespace**, driven over JSON-RPC. Can add latency, return `EIO`, lie in `stat()`, or silently corrupt bytes. Needs `MKNOD` for `/dev/fuse`. |
| **Slow disk under etcd** | `BlockChaos` | — | device-mapper delay/freeze on a block device. **The honest way to give etcd slow `fsync` without touching etcd** — see [what neither tool can do](#cannot-express). |
| **Clock skew** | `TimeChaos` (`timeOffset`, `clockIds`, `containerNames`) | ❌ **none** | `ptrace` + **vDSO patching** (below). No time fault exists in OSS `chaos-charts` — `time-chaos` is in Harness's commercial catalogue only. |
| **Kernel / syscall failure** | `KernelChaos` (`failKernRequest`, `failtype` 0=slab, 1=page, 2=bio, `callchain` predicates) | ❌ **none** | eBPF **kprobe override** on the kernel's own fault-injection points. Needs `bpfki.create=true`, Linux ≥4.18, `CONFIG_BPF_KPROBE_OVERRIDE=y` — [verify first](#verify-first). |
| **HTTP-layer faults** | `HTTPChaos: abort, delay, replace, patch` | `pod-http-latency`, `-reset-peer`, `-status-code`, `-modify-body`, `-modify-header` | Both viable. Useful in P9 against the mesh. |
| **Node down / restart / drain** | ⚠️ **no native node kind** | ✅ `node-poweroff`, `node-restart`, `node-drain`, `node-taint`, `kubelet-service-kill` | See [below](#cannot-express) — on this lab the answer is `qm stop` on Proxmox, and Litmus's SSH-key mechanism is a hazard worth reading rather than running. |
| **Bare-host / VM faults** | `PhysicalMachineChaos` + `chaosd` | ⚠️ VMware / cloud only | The only path in either tool that reaches a control-plane node's *host* processes. **Cadence risk:** `chaosd` went v1.4.0 (Feb 2023) → v1.4.1 (Apr 2026). Do not build a required drill on it without testing. |
| **Steady-state hypothesis** | ⚠️ `StatusCheck` — thin | ✅ **best in class**: 4 probe types × 5 modes | The one reason Litmus gets a session. See [Litmus](#litmus). |
| **etcd corruption / restore** | ❌ | ❌ | [Manual](#manual-drills). |
| **Control-plane quorum loss** | ⚠️ partial, only via `chaosd` | ❌ | [Manual](#manual-drills). |

---

<a id="cannot-express"></a>
## What neither tool can do

Three gaps matter enough to state on their own, because a phase file that assumes a
CR exists for these will send the learner looking for one.

**1. Node failure has no Chaos Mesh kind.** There is no `NodeChaos`. The options are
`PhysicalMachineChaos` + `chaosd` on the host, `StressChaos` heavy enough to force
eviction, or — on this lab, and this is the right answer — **`qm stop` on the Proxmox
host**. Litmus does have real node faults and they are genuinely its strongest area,
but `node-restart`/`node-poweroff` require a **Secret named `id-rsa` holding a node
SSH private key**, which puts node-root credentials inside a Kubernetes Secret
readable by anything with `get secrets` in that namespace. That directly contradicts
the lab's key-handling rule. **Read the mechanism, discuss why it is a bad trade, and
use `qm stop`.**

`kubelet-service-kill` deserves the same treatment: the helper pod's command is
literally `sleep 10 && systemctl stop kubelet && sleep <duration> && systemctl start
kubelet`, running **on the kubelet it just stopped**. If the helper is lost
mid-experiment the node stays broken. Excellent teaching material about
self-referential blast radius; a real footgun on a small lab.

**2. No etcd-aware fault exists in either project.** Verified by enumerating all 36
`chaos-charts/faults/kubernetes/` entries and all 19 Chaos Mesh CRDs. The nearest
adjacents are `BlockChaos` (device-mapper delay/freeze on etcd's block device →
`fsync` latency, which is legitimately useful) and `chaosd process` (SIGKILL etcd).
Corruption and restore are [manual](#manual-drills).

**3. Control-plane quorum loss cannot be scripted honestly.** In-cluster CRDs *can*
select control-plane pods, but `PodKill` on a static pod is immediately undone by the
kubelet — **that is a lesson about static pods, not about quorum loss.** The
legitimate scripted approach is `NetworkChaos partition` on etcd peer port 2380
between members, which is a good repeatable "what does a minority member do"
observation. Actually losing quorum means stopping VMs.

---

<a id="manual-drills"></a>
## Drills that stay manual

Not because tooling is unavailable, but because the tooling would hide the thing being
learned.

1. **etcd snapshot save and restore.** `etcdctl snapshot save`, restore to a fresh
   `--data-dir` with a new `--initial-cluster-token`, fix the static pod manifest,
   watch it come back. The learning is the *procedure and its ordering* — and the
   sinking realisation about what a stale snapshot means for everything created since.
2. **etcd data corruption.** `dd` a page of `member/snap/db`, then meet `etcdctl
   check`, revision/consistency-index mismatch, and `--experimental-initial-corrupt-check`.
   By hand: the point is bbolt page layout and what "corrupt" means to a Raft log,
   which a CR would hide.
3. **Control-plane quorum loss and recovery.** Stop 2 of 3 control-plane VMs, observe
   the read-only/unavailable behaviour, recover with `--force-new-cluster` and rebuild
   the member list.
4. **Version upgrade and migration.** `kubeadm upgrade plan`/`apply`, kubelet/kubectl
   skew rules, API deprecation, and a k0s upgrade. No chaos tool models any of it —
   the failure modes are procedural, not injected.
5. **Botched rollout and rollback.** A bad image, an impossible readiness probe, a
   request the node cannot satisfy — then `kubectl rollout status`/`undo`,
   `revisionHistoryLimit`, `maxUnavailable`/`maxSurge`. **The fault must be the
   learner's own YAML.** Injecting it externally removes exactly the skill being
   built: recognising your own mistake from the controller's behaviour.
6. **Certificate expiry.** `kubeadm certs check-expiration`, front-proxy and kubelet
   client cert rotation. Explicitly **not** a `TimeChaos` drill: TimeChaos affects
   only PID 1 and its children in one container, and moving the node clock to force
   expiry will wreck etcd. Fake the expiry properly, or skip it.
7. **Node join, and cordon → drain → uncordon.** By hand first, so the learner watches
   `kubectl drain` fight PDBs and DaemonSets. *Then* script it with Litmus
   `node-drain` for repeatability.

<a id="borrowed-drills"></a>
### Two drills this strand inherited from other decisions

- **Corrupt the `caBundle` on a working admission webhook** and diagnose it from the
  API server logs alone. With `failurePolicy: Fail` that is an outage — which is the
  honest version, since a broken admission webhook can wedge a cluster, and this is
  the place where wedging one costs nothing. From
  [`build-mechanics.md`](build-mechanics.md#webhook-tls).
- **Boot the build guest on a different kernel than the nodes** and watch the eBPF
  artifact fail — either a verifier rejection or, much worse, a silently wrong field
  offset. From [`build-mechanics.md`](build-mechanics.md#kernel-lockstep).

---

<a id="mechanisms"></a>
## The internals hook — one Linux primitive per fault class

This list is the reason Chaos Mesh won, and it is a Linux-primitives syllabus in its
own right. Architecture: `chaos-controller-manager` (reconciles CRDs, runs the
admission webhooks) → gRPC, **mTLS by default**, port 31767 → `chaos-daemon`
(privileged DaemonSet, one per node) → the target container's kernel namespaces.

**The single mechanism that unlocks everything:** the daemon asks the **CRI** for the
target container's PID, then enters that container's namespaces from the host —
`nsexec -l -p /proc/<pid>/ns/pid -m /proc/<pid>/ns/mnt`, i.e. the `setns(2)` family.
The fault then happens *inside* the target's namespace, which is why it is contained
to that container and invisible to its neighbours on the same node.

| Fault | Primitive |
|---|---|
| `NetworkChaos` | Traffic control programmed **in-process via netlink** (`vishvananda/netlink`), not by shelling out: `netem` qdisc for delay/loss/corrupt/duplicate, `tbf` for bandwidth, `iptables` + `ipset` for partition. Teaching value: qdisc hierarchy, `prio` bands and u32 filters, all visible in `tc -s qdisc show`. |
| `StressChaos` | `stress-ng` **pause-then-resume**, so the process is attached to the target's cgroup *before* it starts allocating. Pod limits are never modified, so the OOMKill is real. |
| `IOChaos` | **`toda`**, a FUSE filesystem, injected into the target's mount namespace and driven over JSON-RPC 2.0. Every read/write now traverses a userspace filesystem that can lie. |
| `TimeChaos` | **The most instructive one.** `ptrace(PTRACE_ATTACH)` to stop the target; find the **vDSO** mapping in `/proc/<pid>/maps`; `process_vm_writev(2)` a `fake_clock_gettime` plus its offset parameters into a new mapping; **rewrite the `clock_gettime` entry in the vDSO to jump to the fake**; detach. It patches the vDSO rather than using `LD_PRELOAD` **because Go binaries parse the vDSO directly and never go through libc** — which is also why it only affects PID 1 and its children, and why a process started later by `kubectl exec` is untouched. |
| `DNSChaos` | CoreDNS running the `k8s_dns_chaos` plugin, returning `SERVFAIL` or a bogus address for matching names. |
| `KernelChaos` | eBPF with **kprobe override** attached to the kernel's own fault-injection points, optionally filtered by `callchain` so only allocations reached through a specific kernel call path fail. The deepest hook available in either tool. |
| `BlockChaos` | device-mapper delay/freeze on a block device. |
| `PodChaos` | Three different layers of "the pod died" — API `DELETE`, runtime `StopContainer`, image rewritten to `pause` — **which is itself the lesson**. |

Litmus reaches the same kernel primitives by a different route — `nsenter(1)` plus
shelling out to `tc(8)`, and cgroup resolution by parsing `/proc/<pid>/cgroup` (its
v1/v2 branching in `stress-helper.go` is worth reading). Cleanup is `tc qdisc delete
dev <if> root`, so **if the helper pod dies first, the qdisc is orphaned** — a
failure mode a resident daemon does not have.

---

<a id="install"></a>
## Installing Chaos Mesh, minimised

**Budget 582Mi.** The default install is 1350Mi across three controller replicas, a
dashboard and a DNS server; the dashboard is both the largest avoidable cost and the
entire CVE surface.

```sh
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace \
  --set controllerManager.replicaCount=1 \
  --set dashboard.create=false \
  --set dnsServer.create=true \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock
```

- **`chaosDaemon.runtime` is a footgun, not a preference.** The chart still defaults to
  `docker` and `/var/run/docker.sock`. On Debian 13 + containerd, **every
  runtime-touching fault fails silently-ish** without the override.
- **`dashboard.create=false` is also the security call.** Chaos Mesh shipped four CVEs
  on 2025-09-15 — "Chaotic Deputy": `CVE-2025-59358` (7.5, unauthenticated GraphQL
  debug server → cluster-wide DoS) and `CVE-2025-59359/59360/59361` (**9.8**, OS
  command injection → full cluster takeover), all in the **chaos-dashboard**
  `CtrlServer`, fixed in v2.7.3. Turning it off costs nothing and removes the surface.
  **This is not only a hardening default — it is a loop.** `CVE-2025-59359` anchors
  P10's security-incident capstone ([#15](https://github.com/k3ii/k8s-academy/issues/15)):
  the learner deliberately re-enables the dashboard on a pinned pre-2.7.3 install,
  exploits it, catches it with a Falco rule they wrote, and **remediates by returning
  to exactly the config on this line.** Incident response arrives at the hardening
  prescribed here four phases earlier — so the P6 reader who wonders why the dashboard
  is off gets the answer as a P10 exercise rather than a footnote.
- **Set `resources.limits` explicitly on every component.** The chart leaves limits
  unset on the controller manager, dashboard and DNS server. On a node deliberately
  run near its ceiling, the chart's requests are a floor and not a ceiling.
- **`chaos-daemon` cannot be disabled** — it *is* the injector. It runs
  `privileged: true`, `hostPID: true`, with host mounts of `/sys` → `/host-sys`,
  `/lib/modules` and the runtime socket. If privileged is dropped, the capability set
  is `SYS_PTRACE, NET_ADMIN, NET_RAW, MKNOD, SYS_CHROOT, SYS_ADMIN, KILL, IPC_LOCK` —
  and reading *why each one is needed* against the [mechanism table](#mechanisms) is a
  better privilege lesson than any policy exercise.
- **No external dependencies.** No database (the dashboard's embedded SQLite is off
  with the dashboard), no Prometheus, no cert-manager — webhook TLS is self-signed
  inline by Helm `genCA`/`genSignedCert`, 1825-day.
- Drop `dnsServer.create=true` and it is 512Mi, but DNS drills are required.
- **`install.sh` is deprecated as of 2.8.2** — use Helm. The CRD API reference is
  off-site at `chaos-mesh.dev/reference/master/` and is not linked from the docs
  sidebar.
- **This block is re-run at the start of every phase that needs it**, not once for the
  curriculum: each phase provisions a fresh topology, so the install goes with the
  cluster when it is destroyed. It is an exercise exactly once — in
  [P6](../phases/06-kubelet-node.md), where the [capability-to-mechanism
  reading](#mechanisms) is done — and one line of setup everywhere after.

<a id="verify-first"></a>
### Verify before promising KernelChaos

```sh
grep CONFIG_BPF_KPROBE_OVERRIDE /boot/config-$(uname -r)
```

On the Debian 13 guest, before any `KernelChaos` drill is written into a phase file.
Treat KernelChaos as a **stretch goal, not a required drill** — and note the upstream
docs' own words: *"disabled by default. Do not use in production."* It also needs
`bpfki.create=true`, which is a second DaemonSet.

<a id="litmus"></a>
## The one Litmus session

`litmus-helm/charts/litmus-core`, chart and appVersion **3.31.0** — actively versioned
in lockstep with the main release, not a legacy leftover. **~128Mi total**: one
`chaos-operator` Deployment with requests == limits at 100m / 128Mi, the three CRDs
(`chaosengine`, `chaosexperiment`, `chaosresult`), and `chaos-exporter` off by
default. Pair it with the `kubernetes-chaos` chart (ChaosExperiment CRs and RBAC only,
no Deployment of its own) and drive everything with `kubectl apply` of `ChaosEngine`
CRs. Roughly 30 minutes to install and tear down.

**Never install ChaosCenter.** It is 2.5–3.8GB — 25–38% of the whole budget — for a
web UI, and MongoDB is still mandatory in 3.x with hostile defaults: `replicaset`
architecture, `replicaCount: 3`, an 8Gi PVC per replica, `resources: {}`, and images
pulled from **`bitnamilegacy/mongodb`** pinned to a 2022 chart. `litmusctl` is *not*
the light path — it is a CLI alternative to the web UI and still registers against a
running ChaosCenter GraphQL backend.

The session covers exactly three things:

1. **The probe model — the reason this session exists.** `httpProbe` / `cmdProbe` /
   `k8sProbe` / `promProbe`, each in mode `SOT` (before), `EOT` (after), `Edge`
   (both), `Continuous` (polled throughout) or `OnChaos` (strictly during injection).
   Probe outcomes fold into the `ChaosResult` verdict, so **a Litmus experiment fails
   when the hypothesis is violated**, not merely when the injection errors. That is
   the correct shape for a chaos experiment, and the steady-state hypothesis is a
   concept the learner must own independently of tooling — Chaos Mesh's `StatusCheck`
   is the thinner equivalent, so carry the concept back to it.
2. **`pod-network-partition` as a mechanism contrast** — NetworkPolicy versus
   iptables, and why the layer matters.
3. **`kubelet-service-kill` as a blast-radius lesson** — read the command, do not run
   it on a single-node lab.

**Set `resources:` by hand on every transient pod.** `RunnerInfo.Resources` and
`ExperimentComponents.Resources` are `json:"resources,omitempty"` with no defaults and
the shipped `ChaosExperiment` templates carry no `resources:` block, so every runner,
experiment and helper pod is **BestEffort** unless
`spec.components.runner.resources` and `spec.experiments[].spec.components.resources`
are set in the `ChaosEngine`. On a node near its ceiling that silently competes with
the very resource-pressure drills being observed.

The CRD-only path's documentation lives on **`litmuschaos.github.io/litmus/experiments/`**,
not `docs.litmuschaos.io`. No primary doc says in one sentence that standalone
`chaos-operator` is supported in 3.x; the conclusion rests on the versioned
`litmus-core` chart, the `ChaosEngine` CRD still shipping, and the *Construct Chaos
Scenario YAML without ChaosCenter* user guide.
