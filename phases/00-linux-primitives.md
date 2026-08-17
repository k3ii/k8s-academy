# Phase 0 — Linux & container primitives

> **3–4 weeks.** No cert, no build-track artifact, no cluster.
> The range is planning information. **The gate at the bottom of this file decides when the phase is finished** — not the calendar. A phase that runs long and passes its gate has succeeded.

| | |
|---|---|
| **Prerequisites** | None. This is week one. A solid programmer who can read Go and has barely written it, and a complete Kubernetes beginner — that is exactly who this phase is written for. |
| **Unlocks** | Everything. Concretely: [P6](06-kubelet-node.md)'s eviction and OOM forensics, [P7](07-networking.md)'s CNI and datapath work, and [P8](08-storage.md)'s `mountPropagation: Bidirectional` are all unreadable without the primitives here — and every [Chaos Mesh](../strands/chaos.md#catalogue) fault class from P6 onward is a wrapper over a Linux mechanism you injure by hand in this phase. |
| **Source area** | [Area 0 — Foundational](../strands/source-reading.md#area-0-foundational), the prose half. **Plus the one source no other phase reads: the kernel's own interfaces** — `man 7 namespaces`, `man 7 cgroups`, and the `/proc` and `/sys/fs/cgroup` pseudo-filesystems. This is the only phase whose primary source is not Go. |
| **Language** | Go ([#9](https://github.com/k3ii/k8s-academy/issues/9)) — but only a **trivial static binary** for the capstone. The Go primer proper is days of work at the tail of [P1](01-operate-shallow.md), because [P2](02-etcd.md) is the first phase that opens Go source in anger. Here you need `package main`, a `println`, and `CGO_ENABLED=0 go build`. |
| **Strands** | [source reading](../strands/source-reading.md#area-0-foundational) · [talks](../strands/talks.md#networking) · [chaos](../strands/chaos.md#principle) |

---

## 1. Objectives

Mechanism-level. Each is phrased so that failing it is detectable — "understand containers" is not on this list, and the word *understand* appears nowhere in it.

By the end of this phase you can:

1. **Name all seven namespace types**, and for a given `unshare` flag state which namespace it creates and one concrete thing the process can no longer see or affect because of it.
2. **Create a cgroup v2, set `memory.max`, and drive a workload inside it to an OOMKill** — then point at the exact counter in `memory.events` that proves it happened, and explain why the process died while the VM's own `free -m` barely moved.
3. **Wire two network namespaces into a ping** with a veth pair and a bridge, and name the three independent things — link, address, route — that each had to be true, having watched each one fail when omitted.
4. **Explain what `pivot_root` does that `chroot` does not**, in terms of the mount namespace, and state why a classic `chroot` escape does not survive a correct `pivot_root`.
5. **Assemble an overlayfs by hand** from lower/upper/work dirs, and predict which layer a given write lands in — the mechanism under every container image layer.
6. **Drop a capability from a process and show the syscall it can no longer make**, and say concretely what `privileged: true` grants that a default container does not have.
7. **Predict whether a mount made inside a namespace appears on the host** from its propagation mode (`private`/`rshared`/`rslave`) — the exact mechanism [P8](08-storage.md)'s CSI node DaemonSet depends on.
8. **State the difference between level-triggered and edge-driven reconciliation**, and why a controller re-reads from its cache instead of trusting the event that woke it — from the Area 0 reading, *before* you ever write a controller in [P4](04-controllers.md).

---

## 2. Modules

The Linux modules are hands-on against the kernel; the reading module runs alongside them, not after. There is **no k/k Go source in this phase** — the "read the source" habit is trained here against `man` pages and pseudo-filesystems, which is the right first target for someone who can read Go but has never read a kernel interface.

### Module 0.1 — Namespaces, one at a time (~4 days)

The whole of "a container" is namespaces + cgroups + a root filesystem. Take the namespaces first and *singly* — the mistake is to reach for a tool that creates all seven at once and learn none of them.

**Read** — `man 7 namespaces`, then `man 2 unshare` and `man 2 setns`. The question to answer from the source, not a blog:

| Read | Answer from it |
|---|---|
| `man 7 namespaces` | Seven namespace types are listed. Which one is **not** disabled by dropping a capability but by a separate `sysctl`/build option, and which one did **not** exist before user namespaces made it safe? Which namespace does a process join by writing to `/proc/<pid>/ns/*`? |
| `man 7 user_namespaces` | Why is the **user** namespace the one that makes all the others available to non-root? Find the sentence about UID/GID mapping that explains it. |

**Do**
1. `unshare --uts --fork bash`, change the hostname inside, and confirm from another shell that the host's hostname did not move.
2. `unshare --pid --fork --mount-proc bash`, run `ps aux`, and explain why you are PID 1 and cannot see the host's processes.
3. Enter another process's network namespace with `nsenter -t <pid> -n` and confirm you see *its* interfaces, not yours.
4. List `/proc/self/ns/` and read the inode numbers. Two processes in the same namespace share an inode; prove it.

**Break it** — as PID 1 inside a fresh PID namespace, `kill -9 1` yourself. What happens to the namespace and to every other process in it? Write down why PID 1 is special, because [P0's capstone](#8-capstone) and every real container inherit this.

**Write down** — the seven types with, for each, one thing a process in that namespace cannot see. This table is an input to the capstone.

### Module 0.2 — Cgroups v2: the resource walls (~4 days)

Namespaces control what a process can *see*; cgroups control what it can *consume*. This module is the foundation of [P6](06-kubelet-node.md)'s entire eviction story.

**Read** — `man 7 cgroups` (the v2 section), then the kernel's own `Documentation/admin-guide/cgroup-v2.rst` for the controller you are about to use.

> **Question to answer from the source:** in cgroup v2, what is the "no internal processes" rule, and what does it force about where you may place a process in the tree? Find where `cgroup.controllers` differs from `cgroup.subtree_control`.

**Do**
1. Under `/sys/fs/cgroup`, create a child cgroup, write a PID into `cgroup.procs`, and confirm the move via `/proc/<pid>/cgroup`.
2. Set `memory.max` to something small (e.g. `50M`). Run a memory hog inside. Watch it get OOMKilled.
3. Read `memory.events` **before and after** and name the counter that incremented. Read `memory.current` and `memory.peak`.
4. Set `cpu.max` to half a core and confirm the throttling in `cpu.stat` (`throttled_usecs`).
5. Set `pids.max` low and watch `fork()` fail with `EAGAIN`.

**Break it** — this is chaos drill [0.C1](#4-chaos-drills). OOM the cgroup, then explain, in writing, why the host's `free -m` barely changed while a process inside died. The answer is the whole point of a memory *limit* versus a memory *request*, and it is the sentence you will reuse in every P6 eviction conversation.

**Write down** — the exact `memory.events` line that proves the kill, and one paragraph distinguishing what the cgroup enforces (`.max`, a wall) from what it merely accounts (`.current`, a meter).

### Module 0.3 — Network namespaces and veth (~5 days)

The densest module, and the one the [Container Networking From Scratch](../strands/talks.md#networking) talk was made for. Watch it first, then reproduce it — the talk builds exactly this on one machine with no Kubernetes.

**Watch** — *Container Networking From Scratch* (Jacobs), full entry under [networking](../strands/talks.md#networking) in the talk index. It ages perfectly; Linux primitives do not move.

**Do**
1. Create two netns (`ip netns add a`, `add b`). Each is an island: no interfaces but `lo`, itself down.
2. Make a veth pair, move one end into each netns, bring both ends and `lo` up.
3. Address each end and `ping` across. Then remove *just the route* and watch it break; restore it. Remove *just the address*; watch it break differently.
4. Add a third netns and a **bridge** in the host namespace; connect all three through it. This is the container-network model in miniature: a bridge per node, a veth per pod.
5. Add a default route and a `MASQUERADE` iptables rule so a namespace can reach the outside world. This is `-j MASQUERADE` — the same NAT every CNI does.

**Break it** — chaos drill [0.C2](#4-chaos-drills): sever one veth end (`ip link del`) under a running `ping` and read the exact failure. Then, by hand, add a `netem` delay qdisc (`tc qdisc add ... netem delay 100ms`) and watch latency appear. You are performing, by hand, the mechanism the [chaos catalogue](../strands/chaos.md#catalogue) later drives from a `NetworkChaos` CR — which is precisely why the tool is not installed until P6.

**Write down** — the three-line recipe (link up, address, route) as a checklist, and one sentence on what the bridge replaces when you go from two namespaces to three.

### Module 0.4 — Root filesystems, layers, and mount propagation (~4 days)

A container's third pillar. This module ends on mount propagation, which is subtle, load-bearing, and the direct link to [P8](08-storage.md).

**Read** — `man 2 pivot_root`, `man 7 mount_namespaces` (the propagation-type section), and the kernel's `Documentation/filesystems/overlayfs.rst` (the "lower", "upper", "work" description).

> **Question to answer from the source:** `pivot_root` and `chroot` both change what `/` means. Which one changes it for the whole *mount namespace* and leaves no reachable path to the old root, and why does that difference matter for escape resistance?

**Do**
1. Build an overlayfs by hand: a read-only `lower`, a writable `upper`, a `work` dir, `mount -t overlay`. Write a file; find it in `upper`. Modify a file that exists only in `lower`; watch copy-up put the modified version in `upper` while `lower` is untouched. This *is* image layering.
2. In a fresh mount namespace, `pivot_root` into a directory tree with a `busybox` static binary, then `umount` the old root. Run the binary. You now have a process that cannot name any file outside its new root.
3. Demonstrate propagation: make a mount in a child namespace with propagation `private` and confirm the host does not see it; redo it `rshared`/`rslave` and watch it appear. 

**Break it** — mount something inside a namespace with the *wrong* propagation for what you intended, then explain — this is the lesson [P8's CSI DaemonSet](08-storage.md) pays for the hard way with `mountPropagation: Bidirectional`. A volume the driver mounts must propagate *back to the host* to be visible to other pods; get the mode wrong and the mount is invisible where it is needed.

**Write down** — an arrow diagram: `lower + upper + work → overlay → pivot_root → the process's /`. Name what each arrow does. This diagram is required input to the capstone.

### Module 0.5 — Capabilities, seccomp, and what "privileged" means (~3 days)

The security primitives. Short, but it defuses the single most dangerous phrase in a manifest.

**Read** — `man 7 capabilities` (skim the capability list, read the model), and `man 2 seccomp` (the `SECCOMP_SET_MODE_FILTER` section, concept only).

> **Question to answer from the source:** what is the difference between the permitted, effective and bounding capability sets? When a container drops `ALL` and adds back `NET_BIND_SERVICE`, which set is being manipulated?

**Do**
1. Run a process, drop `CAP_NET_RAW` (`capsh --drop=cap_net_raw --`), and confirm `ping` (raw sockets) now fails while TCP still works.
2. Inspect a normal process's capabilities in `/proc/<pid>/status` (`CapEff`), decode them with `capsh --decode=`.
3. Apply a tiny seccomp filter that blocks one syscall and watch a program that calls it die with the filter's action.

**Break it** — run your Module 0.4 container **once** with all capabilities and once with `ALL` dropped, and find a single operation that only the first can do. That delta is exactly what `securityContext.privileged: true` hands an attacker — write down the one-sentence version, because you will re-derive it as an *attacker* in [P10](10-security.md).

**Write down** — the capability you dropped, the syscall it gated, and a one-line definition of `privileged: true` in terms of capabilities + device access + namespaces retained.

### Module 0.6 — Foundational reading: why Kubernetes is shaped this way (runs alongside, ~ongoing)

The conceptual grounding, interleaved with the hands-on work above rather than saved for the end. The [Area 0](../strands/source-reading.md#area-0-foundational) prose is the cheapest leverage in the whole corpus and needs no cluster. **This phase reads the approachable, conceptual half (items 1–6); the operational half — API conventions, `local-up-cluster.sh` — is [P1](01-operate-shallow.md)'s, read once there is a cluster to point them at.**

Read in this order, each with a question to hold:

| Read | Answer from it |
|---|---|
| Borg paper — §2, §5, §8 ([Area 0](../strands/source-reading.md#area-0-foundational) item 1) | What did bin-packing many workloads onto shared machines *buy*, such that a scheduler is worth having at all? This is the economic argument the rest of the curriculum assumes. |
| `architecture.md` + `principles.md` (items 2–3) | Find the phrase "level-triggered, edge-driven." State what a controller does after a missed event, and why that makes the system self-healing rather than fragile. |
| `object-lifecycle.md` (item 5) | Creation → deletion → **finalizers** → GC in five pages. What is a finalizer, mechanically? You will meet the consequence in P4 and P8. |
| `controllers.md` (item 6) — **the highest value-per-byte doc in the corpus** | Why do you re-read from the cache instead of trusting the object in the event payload? Answering this is objective 8. |

**No lab.** This module is reading, and it is what turns every later "the controller reconciles" from an incantation into a mechanism.

---

## 3. Capstone

**Build and run a container with no container runtime.**

No Docker, no `runc`, no `podman`, no `nerdctl`. Just the primitives from modules 0.1–0.5, composed by hand into a single process that is isolated on every axis.

Requirements:
1. **A static Go binary** (`CGO_ENABLED=0 go build`) as the workload — trivial on purpose; the lesson is the isolation, not the program.
2. **Its own namespaces**: mount, PID, network, UTS, IPC — and, for the harder version, user. Created together (`unshare`/`clone` flags) but you must be able to say what each one is doing.
3. **A veth into a bridge** so the container has a real, `ping`-able address (module 0.3), with `MASQUERADE` for egress.
4. **A `pivot_root` into an overlayfs root** (module 0.4), old root unmounted, so the process cannot name a host path.
5. **A cgroup with a `memory.max`** (module 0.2), so the process can be OOMKilled independently of the host.
6. **Capabilities dropped to a hand-picked set** (module 0.5).

**Verify from outside**, and this is the assessed part:
- `nsenter -t <pid> -a` into it and confirm the isolation on each axis.
- `ip netns exec` / `ping` to prove the network.
- From the host, show the process in *its* cgroup and OOM it by breaching `memory.max`.
- **Then re-do it explaining, for each `docker run` flag you would otherwise use (`--memory`, `--cap-drop`, `--network`, `--read-only`), which primitive here it sets.** That mapping is the deliverable — it is what makes every later `docker`/`kubectl` flag legible rather than magic.

**This is the target named from week one.** [P11's synthesis capstone](11-synthesis.md) — `kubectl run nginx` traced all the way down to a running container — ends *here*, at the syscalls you made by hand. Closing that loop is the point of the whole curriculum; opening it is the point of this phase.

---

## 4. Chaos drills

**Hand-driven, every one.** No chaos tool is installed until [P6](06-kubelet-node.md); [the standing principle](../strands/chaos.md#principle) is that the mechanism is only the lesson when you inflict it yourself. Each mechanism below reappears later as a [Chaos Mesh CRD](../strands/chaos.md#catalogue) — the point of doing it by hand now is that the CR will then read as a wrapper, not as magic.

| # | Drill | By hand | What you must be able to say afterwards |
|---|---|---|---|
| 0.C1 | **OOM inside a wall** | `memory.max` low + a memory hog (module 0.2) | Which `memory.events` counter moved, and why the host barely noticed — the request-vs-limit sentence |
| 0.C2 | **Cut a link; then slow it** | `ip link del` a veth end, then `tc qdisc ... netem delay` (module 0.3) | The exact failure a severed link produces versus a delayed one, and where `netem` lives (a qdisc in the netns) |
| 0.C3 | **Exhaust the PID namespace** | `pids.max` low, then fork-bomb it | What fails, with which errno, and why the blast radius stops at the namespace boundary |
| 0.C4 | **Fill the root overlay** | `dd` into the `upper` dir until the backing fs is full | What a process sees when its writable layer is full — the primitive under disk-pressure eviction in P6 |

**0.C1 is the one to spend real time on.** It is the mechanism behind every eviction, OOMKill and "why is my pod `Running` but dead" conversation for the next ten months.

---

## 5. Talks

Slotted where they reinforce the hands-on work. Full entry, with exact runtime, under [networking](../strands/talks.md#networking) in the talk index.

- **Container Networking From Scratch** (Jacobs) — watch at the *start* of module 0.3, then reproduce it. It is a build-it-yourself lab in talk form and the single most on-target talk for this phase.

That is deliberately the only assigned talk. P0 is a hands-and-`man`-pages phase; the conference corpus earns its place from P2 onward.

---

## 6. Ecosystem

One item, and it is the productised form of your own capstone.

**`runc` and the OCI Runtime Specification** — **read, do not run.**

- **Hands-on:** none new. You already built what `runc` is.
- **Internals:** open the [OCI runtime spec](https://github.com/opencontainers/runtime-spec)'s `config.json` schema and find your capstone in it — `linux.namespaces`, `linux.resources.memory`, `process.capabilities`, `root.path`. Your hand-made container is exactly this document, executed. Then skim `runc`'s `libcontainer` for the same `setns`/`pivot_root`/cgroup-write calls you made, wrapped in Go. The comparison is the lesson: a "container runtime" is a program that reads that JSON and makes the syscalls you just made.
- **Maturity:** the OCI runtime and image specs are the industry standard; `runc` is their reference implementation and what containerd (hence Kubernetes' default path) ultimately calls. This is not a maturity-tier judgement call — it is the floor everything else stands on.

---

## 7. Checklist

Concrete demonstrable outputs. No item says *understand* or *know*; each is an artifact, a timed production, or a falsifiable claim.

**Produce from a clean VM, under time:**
- [ ] Two network namespaces pinging across a veth + bridge — **under 5 minutes**, from memory, no notes.
- [ ] A cgroup that OOMKills a process at a set `memory.max`, with the proving `memory.events` line read aloud — **under 3 minutes**.
- [ ] Enter a running container's five namespaces with `nsenter` and name what each isolates — **under 2 minutes**.

**Produce as a written artifact:**
- [ ] The completed capstone: the from-scratch container, plus the `docker run`-flag → primitive mapping table.
- [ ] The overlay → `pivot_root` → `/` arrow diagram from module 0.4, drawn from memory in under 5 minutes.
- [ ] The seven-namespaces table from module 0.1, each with one thing the namespace hides.

**Falsifiable claims — write the answer, then verify against `man`/source:**
- [ ] Which `memory.events` counter proves an OOMKill, and why the host's `free -m` did not move.
- [ ] Why a correct `pivot_root` resists an escape that `chroot` does not.
- [ ] Which mount propagation mode makes an in-namespace mount visible on the host, and why [P8's CSI DaemonSet](08-storage.md) needs it.
- [ ] What `privileged: true` grants, in terms of capabilities, device access, and namespaces retained.
- [ ] Why a controller re-reads from cache instead of trusting the event payload ([controllers.md](../strands/source-reading.md#area-0-foundational)).

---

## 8. Gate

You may advance to [P1](01-operate-shallow.md) when:

1. **The from-scratch container runs and survives outside verification.** `nsenter` confirms isolation on every axis, it has a `ping`-able address, and it can be OOMKilled from the host via its cgroup. This is objective, and it is the phase.
2. **The `docker run`-flag mapping is complete and correct.** The standard is that for any container flag a reader names, you can point at the primitive it sets. "I understand containers" is unfalsifiable; "`--memory` sets `memory.max` on the process's cgroup" is either true or it is not.
3. **No chaos drill remains mysterious.** Specifically 0.C1: if you cannot say which `memory.events` counter moved and why the host did not notice, **stay in this phase** — a red drill is the one condition permitted to extend a phase without renegotiating the schedule. Every P6 eviction conversation depends on this being reflexive.

There is no cert and no build-track gate here — this phase has neither. What it has instead is the foundation that makes the next ten months legible: when P2 says "the kubelet undoes a `PodKill` on a static pod," or P7 says "the CNI just wired a veth into a bridge," or P8 says "the mount has to propagate back to the host," none of it will be new mechanism. It will be this phase, named.
