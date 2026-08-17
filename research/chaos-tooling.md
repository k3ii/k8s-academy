# Chaos Tooling: Chaos Mesh vs Litmus on a Cramped Lab

Resolves [k3ii/k8s-academy#7](https://github.com/k3ii/k8s-academy/issues/7). Research date: **2026-08-17**. All figures read from primary sources (Helm `values.yaml`, project docs, GitHub API, `litmus-go` source) at that date.

---

## Verdict

**Chaos Mesh is the primary scripted-chaos tool. Litmus gets one comparative session — using the `litmus-core` chart only, never ChaosCenter.**

Reasoning, in order of weight:

1. **Fault coverage against the required list is decisively Chaos Mesh's.** Litmus's open-source catalogue has **no clock-skew fault and no kernel/syscall fault at all** — both are on the requirements list, and both exist in Chaos Mesh (`TimeChaos`, `KernelChaos`). Litmus's `time-chaos` lives only in Harness's commercial catalogue, not in `litmuschaos/chaos-charts`. Verified by enumerating `chaos-charts/faults/kubernetes/` (36 entries — see matrix).
2. **The internals hook is far richer in Chaos Mesh, and mechanism is the curriculum's whole point.** Chaos Mesh maps one Linux primitive per fault class — `setns` + netlink `tc netem`, cgroup attach, `ptrace` + vDSO patching, FUSE, a CoreDNS plugin, BPF kprobe override, device-mapper. That list *is* a Linux-primitives syllabus. Litmus uses a narrower set (mostly `nsenter` + shelling out to `tc`), and one of its faults is implemented at the wrong layer for teaching (partition via NetworkPolicy — see below).
3. **Footprint favours Chaos Mesh once you compare like for like.** Litmus's *lighter* mode (`litmus-core`, ~128Mi) genuinely beats Chaos Mesh minimised (~582Mi) at rest. But Litmus's *default* mode (ChaosCenter + MongoDB replicaset) costs a realistic **2.5–3.8GB = 25–38% of the 9.9GB budget** for a web UI, and its transient experiment pods are **BestEffort by default** — unbounded on a node that is deliberately being run to the edge. Chaos Mesh's minimised footprint is a flat, predictable 582Mi with **no database of any kind**. On a lab whose curriculum includes OOMKill and eviction drills, "predictable overhead" beats "128Mi plus an unbounded tail".
4. **Litmus is not weaker as a project** — this is not a health-based decision. Litmus ships *monthly* (3.31.0, 2026-07-15); Chaos Mesh ships quarterly (2.8.3, 2026-06-10). Both are CNCF Incubating. Litmus loses on capability and mechanism, not on maintenance.

**Where Litmus earns its one session:** the **probe model** (`httpProbe`/`cmdProbe`/`k8sProbe`/`promProbe` × `SOT`/`EOT`/`Edge`/`Continuous`/`OnChaos`) is a genuinely better encoding of the steady-state hypothesis than Chaos Mesh's `StatusCheck`, and steady-state hypothesis is a chaos-engineering *concept* the learner must own independently of tooling. Litmus also has better **node-level** faults (`node-poweroff`, `node-restart`, `node-drain`, `node-taint`, `kubelet-service-kill`) than Chaos Mesh has natively. One session, `litmus-core` only.

---

## Project health

| | Chaos Mesh | Litmus |
|---|---|---|
| CNCF tier | **Incubating** since 2022-02-16 (sandbox 2020-07-14) | **Incubating** since 2022-01-11 (sandbox 2020-06-25) |
| Graduated? | No — ~4.5 yrs in incubation | No |
| Latest release | **v2.8.3, 2026-06-10** | **3.31.0, 2026-07-15** |
| Cadence | ~2–3 months (2.8.2 Mar 2026, 2.8.1 Dec 2025, 2.8.0 Sep 2025) | **Monthly, unbroken** through 2025–2026 |
| Commits, last 6 mo | 81 (`chaos-mesh/chaos-mesh`) | 83 (`litmuschaos/litmus`) |
| Repo activity | pushed 2026-08-17; 543 open issues, ~89 PRs, 7.8k stars | pushed 2026-07-31; 414 open issues, 74 PRs, 5.6k stars |
| Maintainer concentration | 3 of 5 maintainers at PingCAP (bus factor) | Maintainers are now *the Harness Chaos Engineering team* — single-vendor governance |
| Docs | Versioned, in sync with 2.8.3. **CRD API reference is off-site** at `chaos-mesh.dev/reference/master/`, not linked from the sidebar | Versioned but **fragmented**: `docs.litmuschaos.io` (at 3.30.0, one release behind) covers ChaosCenter; the per-fault CRD reference lives on a *different* site, `litmuschaos.github.io/litmus/experiments/` |
| K8s support | 2.8.x tested against **1.30–1.35**. `install.sh` deprecated as of 2.8.2 — use Helm | chart `kubeVersion: ">=1.16.0-0"` |

**Security, and a bonus finding.** Chaos Mesh shipped four CVEs disclosed 2025-09-15 — **"Chaotic Deputy"**: `CVE-2025-59358` (CVSS 7.5, unauthenticated GraphQL debug server → cluster-wide DoS) and `CVE-2025-59359/59360/59361` (CVSS **9.8**, OS command injection → full cluster takeover), all in the **chaos-dashboard** `CtrlServer`, fixed in v2.7.3 (2025-08-21). Two consequences:

- **Operational:** install with `dashboard.create=false`. This is also the right call for footprint, so it costs nothing.
- **Curriculum:** this is a strong candidate for the *CVE-driven security-incident lab* still listed as unspecified fog on #1. It is an in-cluster, network-isolated, RCE-to-cluster-takeover chain in a CNCF project the learner will already have installed, needing no internet egress — a clean fit for the NAT'd `vmbr0` containment story. Worth raising as its own ticket.

Litmus's comparable signal is routine: CVEs patched in-release (e.g. `CVE-2026-33186` in 3.29.0). Its own smell is different — the ChaosCenter chart pulls **`bitnamilegacy/mongodb`** images from Bitnami's frozen legacy catalogue, pinned to chart `mongodb 12.1.11` (a 2022 chart). That is an unmaintained image in the default install path.

---

## Resource footprint

### Chaos Mesh (Helm chart, `helm/chaos-mesh/values.yaml`, master @ 2.8.3)

| Component | Kind | Default replicas | CPU req | Mem req | Limits |
|---|---|---|---|---|---|
| `chaos-controller-manager` | Deployment | **3** | 25m | 256Mi | **unset** |
| `chaos-daemon` | DaemonSet (1/node) | 1 per node | 100m | 256Mi | via `resourceProfile: light` |
| `chaos-dashboard` | Deployment | 1, `create: true` | 25m | 256Mi | **unset** |
| `chaos-dns-server` | Deployment | 1, `create: true` (default-on since 2.6) | 100m | 70Mi | **unset** |
| `chaos-kernel` (bpfki) | DaemonSet | `create: false` | — | — | opt-in, needed for KernelChaos |
| Prometheus / chaosDlv | — | `false` | — | — | opt-in |

- **Default install, single node: 300m CPU / 1350Mi (~1.32GiB) requests.**
- **Minimised for this lab** (`controllerManager.replicaCount=1`, `dashboard.create=false`, keep DNS server because DNS drills are required): **225m / 582Mi**. Drop the DNS server too and it is **125m / 512Mi**.
- `chaos-daemon` cannot be disabled — it *is* the injector.
- **External dependencies: none.** No database (dashboard defaults to embedded SQLite, `persistentVolume.enabled: false`), no Prometheus, no cert-manager (webhook TLS is self-signed inline by Helm `genCA`/`genSignedCert`, 1825-day).
- **Limits are unset by default.** On a 9.9GB node, set them explicitly — the requests above are a floor, not a ceiling.
- `chaos-daemon` privileges: `privileged: true`, `hostPID: true`, host mounts of `/sys` → `/host-sys`, `/lib/modules`, and the runtime socket. Capability set if you drop privileged: `SYS_PTRACE, NET_ADMIN, NET_RAW, MKNOD, SYS_CHROOT, SYS_ADMIN, KILL, IPC_LOCK`.
- **Install footgun:** the chart still defaults to `chaosDaemon.runtime: docker` / `socketPath: /var/run/docker.sock`. On Debian 13 + containerd you **must** override to `runtime: containerd` / `socketPath: /run/containerd/containerd.sock` or every runtime-touching fault fails. (Debian 13 itself is not in any official compatibility statement — the daemon is distro-agnostic in principle, but treat this as unverified.)

### Litmus — full ChaosCenter (`litmus-helm/charts/litmus`, chart 3.30.0)

| Component | CPU req | Mem req | CPU lim | Mem lim |
|---|---|---|---|---|
| `litmusportal-frontend` | 125m | 150Mi | 550m | 512Mi |
| `litmusportal-server` (GraphQL) | 225m | 250Mi | 550m | 712Mi |
| `litmusportal-auth-server` | 225m | 250Mi | 550m | 712Mi |
| `waitForMongodb` init | 25m | 150Mi | 250m | 512Mi |
| **MongoDB** (Bitnami dep, `enabled: true`) | **unset** | **unset** | **unset** | **unset** |
| chaos-infra agent: `subscriber`, `event-tracker`, `workflow-controller`, `chaos-operator-ce`, `chaos-exporter` | 25m each | 300M each | none published | none published |

**Yes, MongoDB is still mandatory in 3.x**, and the defaults are hostile to this lab: `architecture: replicaset`, **`replicaCount: 3`**, `persistence.enabled: true` inheriting Bitnami's **8Gi PVC per replica (24Gi)**, and `resources: {}` — no requests, no limits, three unconstrained `mongod` processes each with a WiredTiger cache sized from available memory. It can be reduced (`architecture: standalone`, `replicaCount: 1`) or pointed at an external instance, but not eliminated.

Declared requests total **~700m / ~2.03GiB**; add MongoDB's real, undeclared usage and the honest number is **~2.5–3.8GB, i.e. 25–38% of the 9.9GB budget**, before the cluster, the workloads under test, or a single experiment. Litmus's own FAQ claims "1 GiB memory and 1 core" for ChaosCenter; that matches the declared requests and ignores MongoDB. **Disqualifying for this lab.**

### Litmus — the lighter CRD-only mode: **yes, it exists and is current**

`litmus-helm/charts/litmus-core`, **chart + appVersion 3.31.0, released 2026-07-20** — actively versioned in lockstep with the main release, not a legacy leftover. It installs:

- `chaos-operator` Deployment, `replicaCount: 1`, **requests == limits at 100m CPU / 128Mi**
- CRDs: `chaosengine`, `chaosexperiment`, `chaosresult`
- `chaos-exporter`: `enabled: false` by default

**~128Mi total. No MongoDB, no ChaosCenter, no GraphQL, no auth server, no Argo.** Pair it with the `kubernetes-chaos` chart (ChaosExperiment CRs + RBAC only — no Deployment of its own) and drive everything with `kubectl apply` of `ChaosEngine` CRs. `litmusctl` is *not* the light path — it is a CLI alternative to the ChaosCenter web UI and still registers against a running ChaosCenter GraphQL backend.

Caveat, stated honestly: no primary doc says in one sentence "chaos-operator standalone is supported in 3.x". The conclusion rests on three converging primary sources — the versioned `litmus-core` chart at 3.31.0, the `ChaosEngine` CRD still shipping in `chaos-operator` (pushed 2026-07-15), and the *Construct Chaos Scenario YAML without ChaosCenter* user guide in current docs. The documentation for this path lives on the older `litmuschaos.github.io/litmus/experiments/` site, not `docs.litmuschaos.io`.

### Litmus per-node and transient overhead

- **No DaemonSet.** Everything is a Deployment, or a transient pod created per run: `ChaosEngine` → **chaos-runner** pod → **experiment** pod → **helper** pod (node-pinned, privileged).
- Helper pods need `privileged: true`, `hostPID: true`, and the container-runtime socket mounted.
- **`RunnerInfo.Resources` and `ExperimentComponents.Resources` are `json:"resources,omitempty"` with no defaults**, and the shipped `ChaosExperiment` templates carry no `resources:` block. Every transient pod is therefore **BestEffort** unless you set `spec.components.runner.resources` and `spec.experiments[].spec.components.resources` in every `ChaosEngine` by hand. On a node deliberately near its ceiling, that is a real hazard — and it silently competes with the very resource-pressure drills the curriculum wants to observe.

### Head-to-head on the 9.9GB budget

| Install | Resident overhead | Verdict |
|---|---|---|
| Chaos Mesh minimised (1 controller, no dashboard, DNS on) | **582Mi**, bounded, no DB | **Viable** — 5.9% of budget |
| Chaos Mesh default | 1350Mi | Viable but wasteful; dashboard is also the CVE surface |
| **Litmus `litmus-core` CRD-only** | **128Mi** + unbounded transient pods | **Viable** — lightest at rest, needs manual `resources:` discipline |
| Litmus full ChaosCenter | 2.5–3.8GB | **Not viable** |

---

## Fault coverage matrix

Scenarios from #7. `chaos-charts/faults/kubernetes/` enumerated directly (36 faults); Chaos Mesh CRD list taken from `webhook.CRDS` in `values.yaml`.

| Required scenario | Chaos Mesh | Litmus (OSS) |
|---|---|---|
| **Node failure / shutdown** | ⚠️ **No native node kind.** Options: `PhysicalMachineChaos` + `chaosd` `process`/`network-partition` on the host; `StressChaos` to force eviction; or `qm stop` on Proxmox. Not scripted in-cluster. | ✅ **Best coverage.** `node-poweroff`, `node-restart`, `node-drain`, `node-taint`, `kubelet-service-kill`, `docker-service-kill` |
| **Network partition** | ✅ `NetworkChaos` action `partition`, `direction: to/from/both` — **`iptables` + `ipset` inside the target netns. CNI-independent.** | ⚠️ `pod-network-partition` **creates a Kubernetes `NetworkPolicy`** — needs a policy-enforcing CNI (Calico/Cilium). With plain flannel it silently does nothing. Wrong layer for teaching partitions |
| **Latency / packet loss / corruption / duplication / bandwidth** | ✅ `NetworkChaos` `delay` (with jitter/correlation), `loss`, `corrupt`, `duplicate`, `bandwidth` | ✅ `pod-network-latency`, `-loss`, `-corruption`, `-duplication`, `-rate-limit` |
| **DNS failure** | ✅ `DNSChaos` `error` \| `random`. Needs `chaos-dns-server`. **A/AAAA only; wildcards suffix-only** | ✅ `pod-dns-error`, plus `pod-dns-spoof` (spoofing is a Litmus-only capability) |
| **etcd corruption + backup/restore** | ❌ **No.** No etcd-aware fault in any CRD. Nearest adjacents: `BlockChaos` (device-mapper delay/freeze on etcd's block device → fsync latency), `chaosd process` (SIGKILL etcd), `disk-fill` | ❌ **No.** No etcd fault in `chaos-charts` at all. Nearest: `disk-fill` |
| **Control-plane quorum loss** | ⚠️ **Partially, and only honestly via `chaosd`.** In-cluster CRDs *can* select control-plane pods, but `PodKill` on a static pod is immediately undone by the kubelet — that is a lesson about static pods, not quorum loss. The legitimate scripted approach is `NetworkChaos partition` on etcd peer port 2380 between members on a multi-CP cluster. Actually losing quorum = stopping VMs | ❌ **No.** `node-drain`/`node-taint` do not evict static pods. `node-poweroff` is an SSH reboot wrapper with no quorum awareness |
| **Noisy neighbour: CPU / memory / IO contention** | ✅ `StressChaos` (`stress-ng` joined into the target's cgroup — **does not raise the pod's limits, so real OOMKill and CFS throttling result**), `IOChaos` (latency/fault/attrOverride/mistake), `BlockChaos` | ✅ Broadest node-level set: `pod-cpu-hog`, `pod-memory-hog` (+ `-exec` variants), `pod-io-stress`, `pod-fio-stress`, `disk-fill`, `node-cpu-hog`, `node-memory-hog`, `node-io-stress` |
| **Pod kill / container kill / pod failure** | ✅ `PodChaos`: `pod-kill` (API delete, `gracePeriod: 0`), `container-kill` (CRI `StopContainer`), `pod-failure` (**rewrites the image to `pause` → sustained unavailability without deletion**) | ✅ `pod-delete` (API delete, `FORCE` option), `container-kill` (via runtime socket), `pod-autoscaler`. No analogue of `pod-failure`'s pause-image trick |
| **Clock skew** | ✅ `TimeChaos` (`timeOffset`, `clockIds`, `containerNames`). Also `chaosd clock` on hosts | ❌ **No.** No time/clock fault in OSS `chaos-charts`. `time-chaos` exists only in Harness's commercial catalogue |
| **Kernel / syscall faults** | ✅ `KernelChaos` — `failKernRequest` with `failtype` 0=slab alloc, 1=page alloc, 2=bio, plus `callchain` predicates. Requires `bpfki.create=true`, Linux ≥4.18, `CONFIG_BPF_KPROBE_OVERRIDE=y`. Docs: *"disabled by default. Do not use in production"* | ❌ **No.** Nothing kernel- or syscall-level |
| *(bonus)* HTTP-layer faults | ✅ `HTTPChaos` abort/delay/replace/patch | ✅ `pod-http-latency`, `-reset-peer`, `-status-code`, `-modify-body`, `-modify-header` |
| *(bonus)* JVM faults | ✅ `JVMChaos` (byteman agent) | ⚠️ Spring Boot Chaos Monkey only |
| *(bonus)* Bare-host / VM faults | ✅ `PhysicalMachineChaos` + `chaosd`: `process`, `clock`, `disk-fill`, `disk-read/write-payload`, `network-*`, `stress-cpu/mem`, `jvm-*` | ⚠️ `vm-poweroff` (VMware), cloud-provider faults only |
| *(bonus)* Steady-state hypothesis / verification | ⚠️ `StatusCheck` CRD — thin | ✅ **Best in class:** 4 probe types × 5 modes, folded into the `ChaosResult` verdict |

**Verify before promising KernelChaos in a lab spec:** run `grep CONFIG_BPF_KPROBE_OVERRIDE /boot/config-$(uname -r)` on the Debian 13 guest. Treat KernelChaos as a stretch goal, not a required drill.

---

## The internals hook

### Chaos Mesh — a resident privileged daemon that enters the target's namespaces

Architecture: `chaos-controller-manager` (reconciles CRDs, runs the admission webhooks) → gRPC, **mTLS by default**, port 31767 → `chaos-daemon` (privileged DaemonSet, one per node) → the target container's kernel namespaces.

The single mechanism that unlocks everything: the daemon asks the **CRI** for the target container's PID, then enters that container's namespaces from the host — `nsexec -l -p /proc/<pid>/ns/pid -m /proc/<pid>/ns/mnt`, i.e. the `setns(2)` family. The fault then happens *inside* the target's namespace, which is why it is contained to that container and invisible to its neighbours on the same node. Per fault class:

- **NetworkChaos** — after entering the netns, it programs traffic control **via the `vishvananda/netlink` library, in-process** (not by shelling out): a `netem` qdisc for `delay`/`loss`/`corrupt`/`duplicate`, `tbf` for `bandwidth`, and `iptables` + `ipset` rules for `partition`. Teaching value: qdisc hierarchy, `prio` bands, and u32 filters are all visible with `tc -s qdisc show`.
- **StressChaos** — normalises the spec into `stress-ng` arguments and starts the process, using a **pause-then-resume** sequence so the process is attached to the *target's* cgroup before it starts allocating. It does **not** modify the pod's cgroup limits, so the memory pressure hits the real `memory.max` and produces a genuine OOMKill — exactly the pressure the lab wants to observe.
- **IOChaos** — injects **`toda`**, a FUSE filesystem written in Rust, into the container's **mount namespace**, and drives it over JSON-RPC 2.0. Every read/write from the app now traverses a userspace filesystem that can add latency, return `EIO`, lie in `stat()` (`attrOverride`), or silently corrupt bytes (`mistake`). This requires `MKNOD` to create `/dev/fuse`.
- **TimeChaos** — the most instructive one. `ptrace(PTRACE_ATTACH)` to stop the target; find the **vDSO** mapping via `/proc/<pid>/maps`; create a new mapping in the target's address space and `process_vm_writev(2)` a `fake_clock_gettime` implementation plus its offset parameters into it; then use ptrace to **rewrite the `clock_gettime` entry in the vDSO to jump to the fake**; detach. It patches the vDSO rather than using `LD_PRELOAD` precisely because Go binaries parse the vDSO directly and never go through libc. This is also why it **only affects PID 1 in the container and its children** — a process started later by `kubectl exec` is untouched.
- **DNSChaos** — `chaos-dns-server` is **CoreDNS running the `k8s_dns_chaos` plugin**; the target pod's resolution is steered to it, and the plugin returns `SERVFAIL` (`error`) or a bogus address (`random`) for matching names. Teaching value: the whole `resolv.conf` → `ndots` → search-domain → CoreDNS path becomes inspectable.
- **KernelChaos** — the `chaos-kernel` (bpfki) daemon attaches an eBPF program using **kprobe override** (`CONFIG_BPF_KPROBE_OVERRIDE`, Linux ≥4.18) to the kernel's own fault-injection points, forcing `slab` allocations, page allocations, or block-IO submissions to fail, optionally filtered by `callchain` so only allocations reached through a specific kernel call path fail. This is the deepest hook available in either tool.
- **BlockChaos** — device-mapper (delay/freeze) on a block device; the honest way to give etcd slow `fsync` without touching etcd.
- **PodChaos** — `pod-kill` is a plain API `DELETE` with `gracePeriod: 0`; `container-kill` is a gRPC call to the daemon which calls the runtime's `StopContainer`; `pod-failure` **rewrites the container image to `pause`**, so the pod object stays but the workload is gone. Three different layers of "the pod died", which is itself the lesson.
- **PhysicalMachineChaos** — a **`chaosd`** agent in service mode on the bare host; the CRD proxies actions (`process`, `clock`, `network-*`, `disk-*`, `stress-*`, `jvm-*`) to it. This is the only path in either tool that can legitimately reach a control-plane node's *host* and its processes. Note the cadence risk: `chaosd` went **v1.4.0 (Feb 2023) → v1.4.1 (Apr 2026)** — a three-year gap. It is the weakest-maintained piece of the Chaos Mesh story; do not build a required drill on it without testing first.

### Litmus — an operator that spawns transient privileged helper pods, plus a probe-driven verdict

Execution chain: `ChaosEngine` CR applied → **`chaos-operator`** reconciles it → creates a **`chaos-runner`** pod → the runner creates the **experiment (fault) job**, which for infra-level faults creates a node-pinned **helper pod** → results land in a **`ChaosResult`** CR. Nothing is resident on the nodes; privilege is acquired per run and released after.

Verified against `litmus-go` source:

- **Network faults** (`chaoslib/litmus/network-chaos/helper/netem.go`) — the helper pod shells out: `sudo nsenter --net=/proc/<pid>/ns/net tc qdisc replace dev <if> root <netem args>`, then builds a `prio` qdisc with `tc filter ... u32 match ip dport/sport/dst ...` to scope the fault to specific ports or destination IPs. Same kernel primitives as Chaos Mesh, reached by `nsenter(1)` + `tc(8)` instead of `setns` + netlink. Cleanup is `tc qdisc delete dev <if> root` — and if the helper dies first, the qdisc is orphaned.
- **Network partition** (`chaoslib/litmus/pod-network-partition/network-policy.go`) — **creates a Kubernetes `NetworkPolicy`** with ingress/egress deny rules matching the target pod's labels, then deletes it. This is enforcement-delegated-to-the-CNI, not a kernel-level partition: **it does nothing on a CNI that does not implement NetworkPolicy.** Pedagogically it teaches NetworkPolicy, not partitions — a genuinely useful contrast to draw against Chaos Mesh's iptables approach, but not a substitute for it.
- **Stress faults** (`chaoslib/litmus/stress-chaos/helper/stress-helper.go`) — parses `/proc/<pid>/cgroup`, resolves the target's cgroup path (handles **both cgroup v1 subsystems and cgroups v2**, via `containerd/cgroups`), then launches `stress-ng` **into the target's cgroup**. Same idea as Chaos Mesh; the v1/v2 branching in the source is itself worth reading.
- **`kubelet-service-kill`** — creates a **privileged helper pod pinned to the target node** (`NodeName: appNodeName`) whose command is literally `sleep 10 && systemctl stop kubelet && sleep <duration> && systemctl start kubelet`. Read that carefully: the pod that must restart the kubelet is *running on the kubelet it just stopped*. If the helper is lost mid-experiment, the kubelet is never restarted and the node stays broken. Excellent teaching material about self-referential blast radius — and a real footgun on a single-node lab.
- **`node-restart` / `node-poweroff`** — requires a Secret named **`id-rsa`** holding a node SSH private key; the helper copies it to an emptyDir, `chmod 400`, then runs `ssh -o StrictHostKeyChecking=no -i <key> <SSH_USER>@<NODE_IP> <REBOOT_COMMAND>`. Note the direct conflict with the lab's key-handling rule (`hopper` holds no private key): this puts a node-root SSH key **inside a Kubernetes Secret**, reachable by anything that can read Secrets in that namespace. Discuss it; prefer `qm stop`/`qm reset` on Proxmox for node-down drills.
- **`container-kill`** — helper pod mounts the container-runtime socket and kills the container through the runtime API directly.
- **Probes** — the part worth the session. `httpProbe` / `cmdProbe` / `k8sProbe` / `promProbe`, each in mode `SOT` (before), `EOT` (after), `Edge` (both), `Continuous` (throughout, polled), or `OnChaos` (strictly during injection). Probe outcomes are folded into the `ChaosResult` verdict alongside the built-in checks, so a Litmus experiment **fails when the hypothesis is violated**, not merely when the injection errors. That is the correct shape for a chaos experiment and the concept the learner should carry forward into Chaos Mesh, where `StatusCheck` is the thinner equivalent.

---

## Stays manual — confirmed

**The ticket's expectation is confirmed for both tools: etcd corruption/restore and control-plane quorum loss are outside what either tool can or should do.** Neither project ships a single etcd-aware fault (verified by enumerating all 36 `chaos-charts/faults/kubernetes/` entries and all 19 Chaos Mesh CRDs). On control-plane targeting, the refinement is: **Chaos Mesh can reach control-plane hosts and processes, Litmus effectively cannot** — but "can reach" is not "should script".

1. **etcd snapshot save and restore.** `etcdctl snapshot save`, then restore to a fresh `--data-dir` with a new `--initial-cluster-token`, then fix the static pod manifest and watch it come back. Not scripted by anything. The learning is the *procedure and its ordering* — and the sinking realisation about what a stale snapshot means for the objects created since.
2. **etcd data corruption.** `dd` a page of `member/snap/db`, then meet `etcdctl check`, revision/consistency-index mismatch and `--experimental-initial-corrupt-check`. Do it by hand: the point is bbolt page layout and what "corrupt" means to a Raft log, which a tool would hide behind a CR.
3. **Control-plane quorum loss and recovery.** Stop 2 of 3 control-plane VMs, observe read-only/unavailable behaviour, then recover with `--force-new-cluster` and rebuild the member list. A scripted `NetworkChaos partition` on port 2380 is a *supplement* — good for repeatable "what does a minority member do" observation — never a substitute for the recovery procedure.
4. **Version upgrade / migration.** `kubeadm upgrade plan`/`apply`, the kubelet/kubectl skew rules, API deprecation, and a k0s upgrade. No chaos tool models any of it; the failure modes are procedural, not injected.
5. **Botched rollout and rollback.** A bad image, an impossible readiness probe, a resource request the node cannot satisfy — then `kubectl rollout status`/`undo`, `revisionHistoryLimit`, `maxUnavailable`/`maxSurge`. **The fault must be the learner's own YAML.** Injecting it externally removes exactly the skill being built: recognising your own mistake from the controller's behaviour.
6. **Certificate expiry.** `kubeadm certs check-expiration`, front-proxy and kubelet client cert rotation. Explicitly *not* a TimeChaos drill: TimeChaos only affects PID 1 and its children in one container, and moving the node clock to force expiry will wreck etcd. Fake the expiry properly, or skip it.
7. **Node join / cordon → drain → uncordon lifecycle.** By hand first, so the learner sees `kubectl drain` fight PDBs and DaemonSets. *Then* script it with Litmus `node-drain` for repeatability.

**Standing principle for the chaos strand:** every drill is performed **by hand first**, and only then scripted. The chaos tool's job is regression and repeatability — proving a fix holds, and re-running a scenario cheaply after a change — not first contact with a failure mode.

---

## Recommendation for the curriculum

- **Primary: Chaos Mesh**, installed minimised — `controllerManager.replicaCount=1`, `dashboard.create=false` (footprint *and* the Chaotic Deputy CVEs), `dnsServer.create=true`, `chaosDaemon.runtime=containerd`, `chaosDaemon.socketPath=/run/containerd/containerd.sock`, and **explicit `resources.limits` on every component**. Budget **582Mi**.
- **Secondary: one Litmus session** on the `litmus-core` chart (**128Mi**, ~30 min to install and tear down), covering (a) the probe model as the steady-state-hypothesis lesson, (b) `pod-network-partition` as a NetworkPolicy-vs-iptables mechanism contrast, (c) `kubelet-service-kill` as a blast-radius lesson. **Never install ChaosCenter.** Note in the spec that the CRD-only docs live on `litmuschaos.github.io/litmus/experiments/`, not `docs.litmuschaos.io`.
- **Both are worth touching, but very unequally** — roughly 90/10. One tool does not quite suffice, because the probe model is a concept Chaos Mesh under-teaches.
- **Two follow-on tickets suggested:** (a) the Chaos Mesh "Chaotic Deputy" CVE chain as the anchor for the CVE-driven security-incident lab still listed as fog on #1; (b) verify `CONFIG_BPF_KPROBE_OVERRIDE` on the Debian 13 guest before any KernelChaos drill is written into a phase spec.

---

## Sources

- Chaos Mesh: [values.yaml](https://github.com/chaos-mesh/chaos-mesh/blob/master/helm/chaos-mesh/values.yaml) · [docs](https://chaos-mesh.org/docs/) · [CRD API reference](https://chaos-mesh.dev/reference/master/) · [supported releases](https://chaos-mesh.org/supported-releases/) · [releases](https://github.com/chaos-mesh/chaos-mesh/releases) · [MAINTAINERS.md](https://github.com/chaos-mesh/chaos-mesh/blob/master/MAINTAINERS.md) · [principle analysis blog](https://chaos-mesh.org/blog/implement-chaos-engineering-in-k8s/) · [clock-skew internals blog](https://chaos-mesh.org/blog/simulating-clock-skew-in-k8s-without-affecting-other-containers-on-node/) · [KernelChaos](https://chaos-mesh.org/docs/simulate-kernel-chaos-on-kubernetes/) · [DNSChaos](https://chaos-mesh.org/docs/simulate-dns-chaos-on-kubernetes/) · [TimeChaos](https://chaos-mesh.org/docs/simulate-time-chaos-on-kubernetes/) · [PhysicalMachineChaos](https://chaos-mesh.org/docs/simulate-physical-machine-chaos/) · [CNCF incubation](https://www.cncf.io/blog/2022/02/16/chaos-mesh-moves-to-the-cncf-incubator/) · [Chaotic Deputy CVEs (JFrog)](https://jfrog.com/blog/chaotic-deputy-critical-vulnerabilities-in-chaos-mesh-lead-to-kubernetes-cluster-takeover/)
- Litmus: [litmus-core chart](https://github.com/litmuschaos/litmus-helm/tree/master/charts/litmus-core) · [litmus (ChaosCenter) values.yaml](https://github.com/litmuschaos/litmus-helm/blob/master/charts/litmus/values.yaml) · [kubernetes-chaos chart](https://github.com/litmuschaos/litmus-helm/tree/master/charts/kubernetes-chaos) · [chaos-charts faults](https://github.com/litmuschaos/chaos-charts/tree/master/faults/kubernetes) · [litmus-go chaoslib](https://github.com/litmuschaos/litmus-go/tree/master/chaoslib/litmus) · [chaosengine_types.go](https://github.com/litmuschaos/chaos-operator/blob/master/api/litmuschaos/v1alpha1/chaosengine_types.go) · [docs](https://docs.litmuschaos.io/) · [construct experiment without ChaosCenter](https://docs.litmuschaos.io/docs/user-guides/construct-experiment) · [chaos infra install resources](https://docs.litmuschaos.io/docs/3.11.0/user-guides/chaos-infrastructure-installation) · [probes](https://litmuschaos.github.io/litmus/experiments/concepts/chaos-resources/probes/litmus-probes/) · [PSP/privileges](https://litmuschaos.github.io/litmus/experiments/concepts/security/psp/) · [CNCF incubation](https://www.cncf.io/blog/2022/01/11/litmuschaos-becomes-a-cncf-incubating-project/) · [CNCF Q1–Q2 2026 update](https://www.cncf.io/blog/2026/08/06/litmuschaos-q1-q2-2026-update-community-contributions-and-project-progress/)
