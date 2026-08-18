# Phase 0 — Linux & container primitives

> **3–4 weeks.** No cert, no build-track artifact, no cluster.
> The range is planning information. **The gate at the bottom of this file decides when the phase is finished** — not the calendar. A phase that runs long and passes its gate has succeeded.

| | |
|---|---|
| **Prerequisites** | None. This is week one. A solid programmer who can read Go and has barely written it, and a complete Kubernetes beginner — that is exactly who this phase is written for. |
| **Unlocks** | Everything. Concretely: [P6](06-kubelet-node.md)'s eviction and OOM forensics, [P7](07-networking.md)'s CNI and datapath work, and [P8](08-storage.md)'s `mountPropagation: Bidirectional` are all unreadable without the primitives here — and every [Chaos Mesh](../strands/chaos.md#catalogue) fault class from P6 onward is a wrapper over a Linux mechanism you injure by hand in this phase. |
| **Source area** | [Area 0 — Foundational](../strands/source-reading.md#area-0-foundational), the prose half. **Plus the one source no other phase reads: the kernel's own interfaces** — `man 7 namespaces`, `man 7 cgroups`, and the `/proc` and `/sys/fs/cgroup` pseudo-filesystems. This is the only phase whose primary source is not Go. |
| **Language** | Go ([#9](https://github.com/k3ii/k8s-academy/issues/9)) — but only a **trivial static binary** for the capstone. The Go primer proper is days of work at the tail of [P1](01-operate-shallow.md), because [P2](02-etcd.md) is the first phase that opens Go source in anger. Here you need `package main`, a `println`, and `CGO_ENABLED=0 go build`. |
| **Labs** | [`labs/00/`](../labs/00/README.md) — twenty-two exercises, in order, all on one guest |
| **Strands** | [source reading](../strands/source-reading.md#area-0-foundational) · [talks](../strands/talks.md#networking) · [chaos](../strands/chaos.md#principle) |

---

<a id="objectives"></a>
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

<a id="modules"></a>
## 2. Modules

The Linux modules are hands-on against the kernel; the reading module runs alongside them, not after. There is **no k/k Go source in this phase** — the "read the source" habit is trained here against `man` pages and pseudo-filesystems, which is the right first target for someone who can read Go but has never read a kernel interface.

<a id="m0-1"></a>
### Module 0.1 — Namespaces, one at a time (~4 days)

The whole of "a container" is namespaces + cgroups + a root filesystem. Take the namespaces first and *singly* — the mistake is to reach for a tool that creates all seven at once and learn none of them.

**Read** — `man 7 namespaces`, then `man 2 unshare` and `man 2 setns`. The question to answer from the source, not a blog:

| Read | Answer from it |
|---|---|
| `man 7 namespaces` | Seven namespace types are listed. Which one is **not** disabled by dropping a capability but by a separate `sysctl`/build option, and which one did **not** exist before user namespaces made it safe? Which namespace does a process join by writing to `/proc/<pid>/ns/*`? |
| `man 7 user_namespaces` | Why is the **user** namespace the one that makes all the others available to non-root? Find the sentence about UID/GID mapping that explains it. |

**Labs** — [One flag, one thing hidden](../labs/00/01-uts-namespace.md) · [`ps` lies until you remount `/proc`](../labs/00/02-pid-namespace-and-proc.md) · [A namespace is a file you can point at](../labs/00/03-namespaces-are-inodes.md) · [Kill PID 1 and take the namespace with it](../labs/00/04-kill-pid-1.md)

---

<a id="m0-2"></a>
### Module 0.2 — Cgroups v2: the resource walls (~4 days)

Namespaces control what a process can *see*; cgroups control what it can *consume*. This module is the foundation of [P6](06-kubelet-node.md)'s entire eviction story.

**Read** — `man 7 cgroups` (the v2 section), then the kernel's own `Documentation/admin-guide/cgroup-v2.rst` for the controller you are about to use.

> **Question to answer from the source:** in cgroup v2, what is the "no internal processes" rule, and what does it force about where you may place a process in the tree? Find where `cgroup.controllers` differs from `cgroup.subtree_control`.

**Labs** — [Membership is a write to a file](../labs/00/05-move-a-process-into-a-cgroup.md) · [0.C1 — OOMKilled while the host barely notices](../labs/00/06-oom-inside-a-wall.md) · [CPU limits throttle; they never kill](../labs/00/07-cpu-max-throttles.md) · [0.C3 — fork-bomb a wall you built](../labs/00/08-exhaust-the-pid-limit.md)

---

<a id="m0-3"></a>
### Module 0.3 — Network namespaces and veth (~5 days)

The densest module, and the one the [Container Networking From Scratch](../strands/talks.md#networking) talk was made for. Watch it first, then reproduce it — the talk builds exactly this on one machine with no Kubernetes.

**Watch** — *Container Networking From Scratch* (Jacobs), full entry under [networking](../strands/talks.md#networking) in the talk index. It ages perfectly; Linux primitives do not move.

**Labs** — [Three things must be true before a ping crosses](../labs/00/09-link-address-route.md) · [A bridge is what replaces N² cables](../labs/00/10-a-bridge-for-three.md) · [The namespace reaches the internet through one NAT rule](../labs/00/11-masquerade-out.md) · [0.C2 — sever a link, then merely delay it](../labs/00/12-cut-a-link-then-slow-it.md)

---

<a id="m0-4"></a>
### Module 0.4 — Root filesystems, layers, and mount propagation (~4 days)

A container's third pillar. This module ends on mount propagation, which is subtle, load-bearing, and the direct link to [P8](08-storage.md).

**Read** — `man 2 pivot_root`, `man 7 mount_namespaces` (the propagation-type section), and the kernel's `Documentation/filesystems/overlayfs.rst` (the "lower", "upper", "work" description).

> **Question to answer from the source:** `pivot_root` and `chroot` both change what `/` means. Which one changes it for the whole *mount namespace* and leaves no reachable path to the old root, and why does that difference matter for escape resistance?

**Labs** — [Predict which layer a write lands in](../labs/00/13-overlayfs-by-hand.md) · [The old root has to become unreachable](../labs/00/14-pivot-root-vs-chroot.md) · [Predict whether a mount crosses the boundary](../labs/00/15-mount-propagation.md) · [0.C4 — the writable layer fills](../labs/00/16-fill-the-upper-layer.md)

---

<a id="m0-5"></a>
### Module 0.5 — Capabilities, seccomp, and what "privileged" means (~3 days)

The security primitives. Short, but it defuses the single most dangerous phrase in a manifest.

**Read** — `man 7 capabilities` (skim the capability list, read the model), and `man 2 seccomp` (the `SECCOMP_SET_MODE_FILTER` section, concept only).

> **Question to answer from the source:** what is the difference between the permitted, effective and bounding capability sets? When a container drops `ALL` and adds back `NET_BIND_SERVICE`, which set is being manipulated?

**Labs** — [Drop one capability, lose one syscall](../labs/00/17-drop-a-capability.md) · [A filter that kills on a syscall](../labs/00/18-seccomp-one-syscall.md) · [Find one operation only the privileged version can do](../labs/00/19-the-privileged-delta.md)

---

<a id="m0-6"></a>
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

<a id="capstone"></a>
## 3. Capstone

**Build and run a container with no container runtime.**

No Docker, no `runc`, no `podman`, no `nerdctl` — six primitives from modules 0.1–0.5,
composed by hand into one process isolated on every axis. A static Go binary as the
workload; its own mount, PID, network, UTS and IPC namespaces; a veth into a bridge with a
real, `ping`-able address; a `pivot_root` into an overlayfs root with the old root
unmounted; a cgroup with a `memory.max`; capabilities dropped to a hand-picked set. Every
one of those you have already run in isolation. The capstone is composing them with
nothing that hides any of it.

**The assessed part is the verification, not the script.** It is checked from *outside*:
`nsenter` on each axis, a ping across the bridge, an OOMKill driven from the host through
the cgroup, and then the flag mapping that makes every later `docker`/`kubectl` flag
legible rather than magic.

**Labs** — [A container with no container runtime](../labs/00/20-container-from-scratch.md) · [Every container flag, mapped to its primitive](../labs/00/21-docker-flags-to-primitives.md)

**This is the target named from week one.** [P11's synthesis capstone](11-synthesis.md) — `kubectl run nginx` traced all the way down to a running container — ends *here*, at the syscalls you made by hand. Closing that loop is the point of the whole curriculum; opening it is the point of this phase.

---

<a id="chaos"></a>
## 4. Chaos drills

**Hand-driven, every one.** No chaos tool is installed until [P6](06-kubelet-node.md); [the standing principle](../strands/chaos.md#principle) is that the mechanism is only the lesson when you inflict it yourself. Each mechanism below reappears later as a [Chaos Mesh CRD](../strands/chaos.md#catalogue) — the point of doing it by hand now is that the CR will then read as a wrapper, not as magic.

| # | Drill | What you must be able to say afterwards |
|---|---|---|
| 0.C1 | [**OOM inside a wall**](../labs/00/06-oom-inside-a-wall.md) | Which `memory.events` counter moved, and why the host barely noticed — the request-vs-limit sentence |
| 0.C2 | [**Cut a link; then slow it**](../labs/00/12-cut-a-link-then-slow-it.md) | The exact failure a severed link produces versus a delayed one, and where `netem` lives (a qdisc in the netns) |
| 0.C3 | [**Exhaust the PID namespace**](../labs/00/08-exhaust-the-pid-limit.md) | What fails, with which errno, and why the blast radius stops at the namespace boundary |
| 0.C4 | [**Fill the root overlay**](../labs/00/16-fill-the-upper-layer.md) | What a process sees when its writable layer is full — the primitive under disk-pressure eviction in P6 |

**Every drill here is also a module exercise**, which is not true of any later phase: P0's
faults *are* its primitives, so the drill and the lesson are the same file rather than a
separate injection into a running cluster.

**0.C1 is the one to spend real time on.** It is the mechanism behind every eviction, OOMKill and "why is my pod `Running` but dead" conversation for the next ten months.

---

<a id="talks"></a>
## 5. Talks

Slotted where they reinforce the hands-on work. Full entry, with exact runtime, under [networking](../strands/talks.md#networking) in the talk index.

- **Container Networking From Scratch** (Jacobs) — watch at the *start* of module 0.3, then reproduce it. It is a build-it-yourself lab in talk form and the single most on-target talk for this phase.

That is deliberately the only assigned talk. P0 is a hands-and-`man`-pages phase; the conference corpus earns its place from P2 onward.

---

<a id="ecosystem"></a>
## 6. Ecosystem

One item, and it is the productised form of your own capstone.

**`runc` and the OCI Runtime Specification** — **read, do not run.**

- **Hands-on:** none new. You already built what `runc` is.
- **Internals:** the spec's `config.json` is your capstone, written down as a schema, and
  `runc` is a program that reads it and makes the syscalls you made by hand. Finding each
  of your six steps in it — and then finding four or five things `runc` does that your
  script does not — is [the exercise](../labs/00/22-find-your-container-in-config-json.md).
- **Maturity:** the OCI runtime and image specs are the industry standard; `runc` is their reference implementation and what containerd (hence Kubernetes' default path) ultimately calls. This is not a maturity-tier judgement call — it is the floor everything else stands on.

---

<a id="checklist"></a>
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

<a id="gate"></a>
## 8. Gate

You may advance to [P1](01-operate-shallow.md) when:

1. **The from-scratch container runs and survives outside verification.** `nsenter` confirms isolation on every axis, it has a `ping`-able address, and it can be OOMKilled from the host via its cgroup. This is objective, and it is the phase.
2. **The `docker run`-flag mapping is complete and correct.** The standard is that for any container flag a reader names, you can point at the primitive it sets. "I understand containers" is unfalsifiable; "`--memory` sets `memory.max` on the process's cgroup" is either true or it is not.
3. **No chaos drill remains mysterious.** Specifically 0.C1: if you cannot say which `memory.events` counter moved and why the host did not notice, **stay in this phase** — a red drill is the one condition permitted to extend a phase without renegotiating the schedule. Every P6 eviction conversation depends on this being reflexive.

There is no cert and no build-track gate here — this phase has neither. What it has instead is the foundation that makes the next ten months legible: when P2 says "the kubelet undoes a `PodKill` on a static pod," or P7 says "the CNI just wired a veth into a bridge," or P8 says "the mount has to propagate back to the host," none of it will be new mechanism. It will be this phase, named.
