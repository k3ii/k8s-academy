# Chaos

This document answers three questions. Which fault do you inject? By which Linux primitive?
And with which tool? It also names the faults that no tool can express. You do those drills
by hand, or you do not do them at all.

It derives from [`../research/chaos-tooling.md`](../research/chaos-tooling.md), research date
2026-08-17. That file carries the full comparison of Chaos Mesh against Litmus, the footprint
arithmetic and the project-health assessment. **Chaos Mesh is primary, at 582Mi minimised.
Litmus gets one comparative session, on the `litmus-core` chart. ChaosCenter is never
installed.** That verdict is settled. This document is the part that a phase file links into.

<a id="principle"></a>
## The standing principle

> **Every drill is performed by hand first, and only then scripted.**

The tool has two jobs: regression and repeatability. It proves that a fix holds, and it
re-runs a scenario cheaply after a change. **First contact with a failure mode is not one of
its jobs.** Consider a `NetworkChaos` CR that produces a partition. It teaches nothing about
partitions to a person who has never watched `tc qdisc` do it. Inject the fault by hand, and
the mechanism is the lesson. Inject it by CR, and the mechanism hides behind a controller.

This is also why the chaos strand carries no dedicated phase. It spreads across eight months.
It *is* the preparation for the Troubleshooting domain of the CKA, and that domain is the
largest single domain in any of the three exams, at 30%. The two requirements reinforce each
other, and they do not compete for a slot.

## Which phase drills how

| Phases | How |
|---|---|
| **P0–P5** | **Hand-driven only.** You use `tc netem`, `iptables`, cgroup writes, `kill -9`, `dd` and `qm stop`. No chaos tool is installed. |
| **P6 onward** | Chaos Mesh arrives. By then it reads as *a wrapper over the primitives from P0*, and not as magic. That ordering is the whole reason why it is not installed earlier. |
| **One session, P6+** | Litmus `litmus-core`, for the [probe model](#litmus). Chaos Mesh under-teaches that concept. |
| **Every phase** | At least one drill. The lab stanza of [#11](https://github.com/k3ii/k8s-academy/issues/11) has a mandatory **Break it** field. That field is how "chaos is a strand, not a module" actually lands. |

A **red chaos drill blocks advancement**, and it may extend a phase. It is a gate condition,
and a cert result is not.

---

<a id="catalogue"></a>
## Fault catalogue

This table says what to reach for, and what each fault actually does to the kernel. `CM`
means a Chaos Mesh CRD. `L` means a Litmus OSS fault. **A dash is not a gap in this table. It
is a statement that the tool cannot express the fault**, and that is often the more useful
fact.

| Fault | Chaos Mesh | Litmus (OSS) | Mechanism to teach |
|---|---|---|---|
| **Pod deleted** | `PodChaos: pod-kill` | `pod-delete` | A plain API `DELETE`, with `gracePeriod: 0`. Nothing kernel-level happens. The controller reacts. |
| **Container killed** | `PodChaos: container-kill` | `container-kill` | A gRPC call to the runtime's `StopContainer`. The pod object survives, and the restart count moves. |
| **Workload gone, pod still there** | `PodChaos: pod-failure` | — | **It rewrites the container image to `pause`.** You get sustained unavailability with no deletion. That is the failure mode that looks healthiest in `kubectl get pods`. Litmus has no analogue. |
| **Latency / loss / corruption / duplication** | `NetworkChaos: delay, loss, corrupt, duplicate` (with jitter and correlation on `delay`) | `pod-network-latency`, `-loss`, `-corruption`, `-duplication` | A `netem` qdisc inside the netns of the target. You can see it with `tc -s qdisc show`. |
| **Bandwidth cap** | `NetworkChaos: bandwidth` | `pod-network-rate-limit` | A `tbf` qdisc. |
| **Network partition** | `NetworkChaos: partition`, `direction: to/from/both` | ⚠️ `pod-network-partition` | **CM uses `iptables` plus `ipset` inside the netns, so it is CNI-independent.** Litmus instead **creates a Kubernetes `NetworkPolicy`**. It therefore needs a policy-enforcing CNI, and it silently does nothing without one. That is the wrong layer for teaching partitions. It is a good contrast to draw *against* the iptables version. |
| **DNS failure** | `DNSChaos: error \| random` (it needs `chaos-dns-server`; **A/AAAA only, and wildcards are suffix-only**) | `pod-dns-error`, `pod-dns-spoof` | CM runs **CoreDNS with the `k8s_dns_chaos` plugin**, and it steers the pod's resolution to that server. The whole path from `resolv.conf` through `ndots` to the search domains becomes inspectable. Spoofing is Litmus-only. |
| **CPU / memory / IO contention** | `StressChaos`, `IOChaos`, `BlockChaos` | `pod-cpu-hog`, `pod-memory-hog`, `pod-io-stress`, `pod-fio-stress`, `disk-fill`, `node-*-hog` | `stress-ng` joins the target's **existing cgroup**. It therefore hits the real `memory.max`, and it produces a **genuine OOMKill**, because the pod's limits are not raised. This is exactly the pressure that this lab wants to observe. |
| **Filesystem lies** | `IOChaos: latency, fault, attrOverride, mistake` | — | **`toda`, a FUSE filesystem injected into the mount namespace**, driven over JSON-RPC. It can add latency, return `EIO`, lie in `stat()`, or silently corrupt bytes. It needs `MKNOD` for `/dev/fuse`. |
| **Slow disk under etcd** | `BlockChaos` | — | A device-mapper delay or freeze on a block device. **This is the honest way to give etcd a slow `fsync` without touching etcd.** See [what neither tool can do](#cannot-express). |
| **Clock skew** | `TimeChaos` (`timeOffset`, `clockIds`, `containerNames`) | ❌ **none** | `ptrace` plus **vDSO patching**, described below. No time fault exists in the OSS `chaos-charts`. `time-chaos` is in the commercial catalogue of Harness only. |
| **Kernel / syscall failure** | `KernelChaos` (`failKernRequest`, `failtype` 0=slab, 1=page, 2=bio, `callchain` predicates) | ❌ **none** | eBPF **kprobe override**, on the kernel's own fault-injection points. It needs `bpfki.create=true`, Linux 4.18 or later, and `CONFIG_BPF_KPROBE_OVERRIDE=y`. [Verify that first](#verify-first). |
| **HTTP-layer faults** | `HTTPChaos: abort, delay, replace, patch` | `pod-http-latency`, `-reset-peer`, `-status-code`, `-modify-body`, `-modify-header` | Both are viable. They are useful in P9, against the mesh. |
| **Node down / restart / drain** | ⚠️ **no native node kind** | ✅ `node-poweroff`, `node-restart`, `node-drain`, `node-taint`, `kubelet-service-kill` | See [below](#cannot-express). On this lab the answer is `qm stop` on Proxmox. The SSH-key mechanism of Litmus is a hazard, and it is worth reading rather than running. |
| **Bare-host / VM faults** | `PhysicalMachineChaos` plus `chaosd` | ⚠️ VMware and cloud only | This is the only path in either tool that reaches the *host* processes of a control-plane node. **Cadence risk:** `chaosd` went from v1.4.0 in February 2023 to v1.4.1 in April 2026. Do not build a required drill on it without testing it. |
| **Steady-state hypothesis** | ⚠️ `StatusCheck`, and it is thin | ✅ **best in class**: 4 probe types × 5 modes | This is the one reason why Litmus gets a session. See [Litmus](#litmus). |
| **etcd corruption / restore** | ❌ | ❌ | [Manual](#manual-drills). |
| **Control-plane quorum loss** | ⚠️ partial, and only via `chaosd` | ❌ | [Manual](#manual-drills). |

---

<a id="cannot-express"></a>
## What neither tool can do

Three gaps matter enough to state on their own. A phase file that assumes a CR exists for
these will send the learner looking for one.

**1. Node failure has no Chaos Mesh kind.** There is no `NodeChaos`. You have three options.
You can run `PhysicalMachineChaos` plus `chaosd` on the host. You can run `StressChaos` heavy
enough to force eviction. Or you can run **`qm stop` on the Proxmox host**, which is the
right answer on this lab.

Litmus does have real node faults, and they are genuinely its strongest area. But
`node-restart` and `node-poweroff` require a **Secret named `id-rsa` that holds an SSH
private key for the node**. That puts node-root credentials inside a Kubernetes Secret, and
anything with `get secrets` in that namespace can read it. That directly contradicts the
key-handling rule of the lab. **Read the mechanism, discuss why it is a bad trade, and then
use `qm stop`.**

`kubelet-service-kill` deserves the same treatment. The command of the helper pod is
literally `sleep 10 && systemctl stop kubelet && sleep <duration> && systemctl start
kubelet`, and it runs **on the kubelet that it just stopped**. If the helper is lost
mid-experiment, then the node stays broken. That is excellent teaching material about
self-referential blast radius. It is also a real footgun on a small lab.

**2. No etcd-aware fault exists in either project.** This was verified by enumerating all 36
entries under `chaos-charts/faults/kubernetes/` and all 19 Chaos Mesh CRDs. The nearest
adjacents are two. `BlockChaos` gives a device-mapper delay or freeze on the block device of
etcd, which produces `fsync` latency, and that is legitimately useful. `chaosd process` sends
SIGKILL to etcd. Corruption and restore are [manual](#manual-drills).

**3. Control-plane quorum loss cannot be scripted honestly.** In-cluster CRDs *can* select
control-plane pods. But the kubelet immediately undoes a `PodKill` on a static pod, and
**that is a lesson about static pods, and not about quorum loss.** The legitimate scripted
approach is a `NetworkChaos partition` on etcd peer port 2380, between members. That gives
you a good repeatable observation of what a minority member does. Actually losing quorum
means stopping VMs.

---

<a id="manual-drills"></a>
## Drills that stay manual

These drills stay manual for one reason. It is not that tooling is unavailable. It is that
the tooling would hide the thing being learned.

1. **etcd snapshot save and restore.** Run `etcdctl snapshot save`. Restore to a fresh
   `--data-dir`, with a new `--initial-cluster-token`. Fix the static pod manifest, and watch
   the cluster come back. The learning is the *procedure and its ordering*. It is also the
   sinking realisation about what a stale snapshot means for everything created since.
2. **etcd data corruption.** Use `dd` on a page of `member/snap/db`. Then meet `etcdctl
   check`, a revision and consistency-index mismatch, and
   `--experimental-initial-corrupt-check`. Do this by hand. The point is the bbolt page
   layout, and what "corrupt" means to a Raft log. A CR would hide both.
3. **Control-plane quorum loss and recovery.** Stop 2 of the 3 control-plane VMs. Observe
   the read-only and unavailable behaviour. Then recover with `--force-new-cluster`, and
   rebuild the member list.
4. **Version upgrade and migration.** Run `kubeadm upgrade plan` and `apply`. Work through
   the kubelet and kubectl skew rules, an API deprecation, and a k0s upgrade. No chaos tool
   models any of it, because the failure modes are procedural rather than injected.
5. **Botched rollout and rollback.** Use a bad image, an impossible readiness probe, and a
   request that the node cannot satisfy. Then use `kubectl rollout status` and `undo`,
   `revisionHistoryLimit`, and `maxUnavailable` with `maxSurge`. **The fault must be the
   learner's own YAML.** Injecting it externally removes exactly the skill being built, which
   is recognising your own mistake from the behaviour of the controller.
6. **Certificate expiry.** Run `kubeadm certs check-expiration`, then rotate the front-proxy
   and kubelet client certificates. This is explicitly **not** a `TimeChaos` drill, for two
   reasons. TimeChaos affects PID 1 and its children in one container only. And moving the
   node clock to force expiry will wreck etcd. Fake the expiry properly, or skip the drill.
7. **Node join, and cordon then drain then uncordon.** Do it by hand first, so that the
   learner watches `kubectl drain` fight PDBs and DaemonSets. *Then* script it with the
   Litmus `node-drain` fault, for repeatability.

<a id="borrowed-drills"></a>
### Two drills this strand inherited from other decisions

- **Corrupt the `caBundle` on a working admission webhook**, and then diagnose it from the
  API server logs alone. With `failurePolicy: Fail` that is an outage, and the outage is the
  honest version: a broken admission webhook can wedge a cluster, and this is the place where
  wedging one costs nothing. From
  [`build-mechanics.md`](build-mechanics.md#webhook-tls).
- **Boot the build guest on a different kernel than the nodes**, and watch the eBPF artifact
  fail. You get either a verifier rejection or, much worse, a silently wrong field offset.
  From [`build-mechanics.md`](build-mechanics.md#kernel-lockstep).

---

<a id="mechanisms"></a>
## The internals hook — one Linux primitive per fault class

This list is the reason why Chaos Mesh won. It is also a Linux-primitives syllabus in its own
right. The architecture runs in one direction. `chaos-controller-manager` reconciles the CRDs
and runs the admission webhooks. It talks over gRPC, with **mTLS by default**, on port 31767,
to `chaos-daemon`. That daemon is a privileged DaemonSet, one per node. The daemon then
reaches the kernel namespaces of the target container.

**One mechanism unlocks everything.** The daemon asks the **CRI** for the PID of the target
container. It then enters the namespaces of that container from the host, with `nsexec -l -p
/proc/<pid>/ns/pid -m /proc/<pid>/ns/mnt`. That is the `setns(2)` family. The fault then
happens *inside* the namespace of the target. That is why it is contained to that container,
and why it is invisible to the neighbours of that container on the same node.

| Fault | Primitive |
|---|---|
| `NetworkChaos` | Traffic control, programmed **in-process via netlink** with `vishvananda/netlink` rather than by shelling out. It uses a `netem` qdisc for delay, loss, corruption and duplication, `tbf` for bandwidth, and `iptables` plus `ipset` for a partition. The teaching value is the qdisc hierarchy, the `prio` bands and the u32 filters. All of it is visible in `tc -s qdisc show`. |
| `StressChaos` | `stress-ng`, **paused and then resumed**. The process therefore attaches to the cgroup of the target *before* it starts allocating. Pod limits are never modified, so the OOMKill is real. |
| `IOChaos` | **`toda`**, a FUSE filesystem. It is injected into the mount namespace of the target, and driven over JSON-RPC 2.0. Every read and write now traverses a userspace filesystem that can lie. |
| `TimeChaos` | **The most instructive one.** It calls `ptrace(PTRACE_ATTACH)` to stop the target. It finds the **vDSO** mapping in `/proc/<pid>/maps`. It uses `process_vm_writev(2)` to write a `fake_clock_gettime`, plus its offset parameters, into a new mapping. Then it **rewrites the `clock_gettime` entry in the vDSO to jump to the fake**, and detaches. It patches the vDSO instead of using `LD_PRELOAD` **because Go binaries parse the vDSO directly and never go through libc**. That choice is also why it affects PID 1 and its children only, and why a process that `kubectl exec` starts later is untouched. |
| `DNSChaos` | CoreDNS, running the `k8s_dns_chaos` plugin. It returns `SERVFAIL` or a bogus address for matching names. |
| `KernelChaos` | eBPF with **kprobe override**, attached to the kernel's own fault-injection points. You can filter by `callchain`, so that only allocations reached through a specific kernel call path fail. It is the deepest hook available in either tool. |
| `BlockChaos` | A device-mapper delay or freeze on a block device. |
| `PodChaos` | Three different layers of "the pod died": an API `DELETE`, a runtime `StopContainer`, and the image rewritten to `pause`. **That difference is itself the lesson.** |

Litmus reaches the same kernel primitives by a different route. It uses `nsenter(1)`, and it
shells out to `tc(8)`. It resolves cgroups by parsing `/proc/<pid>/cgroup`, and its v1 and v2
branching in `stress-helper.go` is worth reading. Cleanup is `tc qdisc delete dev <if> root`.
So **if the helper pod dies first, then the qdisc is orphaned.** A resident daemon does not
have that failure mode.

---

<a id="install"></a>
## Installing Chaos Mesh, minimised

**Budget 582Mi.** The default install is 1350Mi, across three controller replicas, a
dashboard and a DNS server. The dashboard is both the largest avoidable cost and the entire
CVE surface.

```sh
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace \
  --set controllerManager.replicaCount=1 \
  --set dashboard.create=false \
  --set dnsServer.create=true \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock
```

- **`chaosDaemon.runtime` is a footgun, and not a preference.** The chart still defaults to
  `docker` and `/var/run/docker.sock`. On Debian 13 with containerd, **every runtime-touching
  fault fails silently-ish** without the override.
- **`dashboard.create=false` is also the security call.** Chaos Mesh shipped four CVEs on
  2025-09-15, under the name "Chaotic Deputy". `CVE-2025-59358` scores 7.5: an
  unauthenticated GraphQL debug server allows a cluster-wide DoS. `CVE-2025-59359`,
  `CVE-2025-59360` and `CVE-2025-59361` each score **9.8**: OS command injection allows full
  cluster takeover. All four are in the `CtrlServer` of the **chaos-dashboard**, and all four
  were fixed in v2.7.3. Turning the dashboard off costs nothing, and it removes the surface.
  **This is not only a hardening default. It is a loop.** `CVE-2025-59359` anchors the
  security-incident capstone of P10 ([#15](https://github.com/k3ii/k8s-academy/issues/15)).
  There, the learner deliberately re-enables the dashboard on a pinned pre-2.7.3 install,
  exploits it, catches it with a Falco rule that they wrote, and **remediates by returning to
  exactly the config on this line.** Incident response then arrives at the hardening that is
  prescribed here, four phases earlier. So the P6 reader who wonders why the dashboard is off
  gets the answer as a P10 exercise, rather than as a footnote.
- **Set `resources.limits` explicitly on every component.** The chart leaves limits unset on
  the controller manager, the dashboard and the DNS server. This node runs deliberately near
  its ceiling, and there the chart's requests are a floor rather than a ceiling.
- **`chaos-daemon` cannot be disabled**, because it *is* the injector. It runs with
  `privileged: true` and `hostPID: true`, and it host-mounts `/sys` at `/host-sys`, plus
  `/lib/modules` and the runtime socket. If you drop privileged, then the capability set is
  `SYS_PTRACE, NET_ADMIN, NET_RAW, MKNOD, SYS_CHROOT, SYS_ADMIN, KILL, IPC_LOCK`. Read *why
  each one is needed* against the [mechanism table](#mechanisms). That reading is a better
  privilege lesson than any policy exercise.
- **No external dependencies.** There is no database, because the embedded SQLite of the
  dashboard goes off with the dashboard. There is no Prometheus, and no cert-manager: webhook
  TLS is self-signed inline by the Helm `genCA` and `genSignedCert` functions, for 1825 days.
- Drop `dnsServer.create=true` and the install is 512Mi. But the DNS drills are required.
- **`install.sh` is deprecated as of 2.8.2**, so use Helm. The CRD API reference is off-site,
  at `chaos-mesh.dev/reference/master/`, and the docs sidebar does not link it.
- **This block is re-run at the start of every phase that needs it.** It is not run once for
  the curriculum. Each phase provisions a fresh topology, so the install goes with the
  cluster when the cluster is destroyed. It is an exercise exactly once, in
  [P6](../phases/06-kubelet-node.md), where the [capability-to-mechanism
  reading](#mechanisms) is done. Everywhere after that, it is one line of setup.

<a id="verify-first"></a>
### Verify before promising KernelChaos

```sh
grep CONFIG_BPF_KPROBE_OVERRIDE /boot/config-$(uname -r)
```

Run that on the Debian 13 guest, before any `KernelChaos` drill is written into a phase file.
Treat KernelChaos as a **stretch goal, and not as a required drill.** Note also what the
upstream docs say themselves: *"disabled by default. Do not use in production."* It also
needs `bpfki.create=true`, and that is a second DaemonSet.

<a id="litmus"></a>
## The one Litmus session

Use `litmus-helm/charts/litmus-core`. Its chart version and appVersion are both **3.31.0**,
so it is actively versioned in lockstep with the main release. It is not a legacy leftover.
It costs **about 128Mi in total**: one `chaos-operator` Deployment with requests equal to
limits at 100m and 128Mi, the three CRDs (`chaosengine`, `chaosexperiment` and
`chaosresult`), and `chaos-exporter`, which is off by default. Pair it with the
`kubernetes-chaos` chart, which carries ChaosExperiment CRs and RBAC only and has no
Deployment of its own. Then drive everything with `kubectl apply` of `ChaosEngine` CRs. Allow
roughly 30 minutes to install it and tear it down.

**Never install ChaosCenter.** It costs 2.5GB to 3.8GB, which is 25% to 38% of the whole
budget, and it buys a web UI. MongoDB is also still mandatory in 3.x, with hostile defaults:
a `replicaset` architecture, `replicaCount: 3`, an 8Gi PVC per replica, `resources: {}`, and
images pulled from **`bitnamilegacy/mongodb`** pinned to a 2022 chart. `litmusctl` is *not*
the light path. It is a CLI alternative to the web UI, and it still registers against a
running ChaosCenter GraphQL backend.

The session covers exactly three things.

1. **The probe model. This is the reason why the session exists.** There are four probe
   types: `httpProbe`, `cmdProbe`, `k8sProbe` and `promProbe`. Each one runs in one of five
   modes: `SOT` (before), `EOT` (after), `Edge` (both), `Continuous` (polled throughout) or
   `OnChaos` (strictly during injection). Probe outcomes fold into the `ChaosResult` verdict.
   So **a Litmus experiment fails when the hypothesis is violated**, and not merely when the
   injection errors. That is the correct shape for a chaos experiment. The learner must own
   the steady-state hypothesis independently of any tooling. `StatusCheck` in Chaos Mesh is
   the thinner equivalent, so carry the concept back to it.
2. **`pod-network-partition` as a mechanism contrast.** It is NetworkPolicy against
   iptables, and it shows why the layer matters.
3. **`kubelet-service-kill` as a blast-radius lesson.** Read the command. Do not run it on a
   single-node lab.

**Set `resources:` by hand on every transient pod.** `RunnerInfo.Resources` and
`ExperimentComponents.Resources` are both `json:"resources,omitempty"`, with no defaults. The
shipped `ChaosExperiment` templates carry no `resources:` block either. So every runner,
experiment and helper pod is **BestEffort**, unless you set
`spec.components.runner.resources` and `spec.experiments[].spec.components.resources` in the
`ChaosEngine`. On a node near its ceiling, those pods then silently compete with the very
resource-pressure drills that you are observing.

The documentation for the CRD-only path lives on
**`litmuschaos.github.io/litmus/experiments/`**, and not on `docs.litmuschaos.io`. No primary
doc says in one sentence that standalone `chaos-operator` is supported in 3.x. The conclusion
rests on three things: the versioned `litmus-core` chart, the `ChaosEngine` CRD still
shipping, and the *Construct Chaos Scenario YAML without ChaosCenter* user guide.
