# Labs — Phase 0, Linux & container primitives

Twenty-two exercises in the order they are meant to run. Each states one claim to test or
one artifact to produce, links its [topology](../../strands/lab-topologies.md) rather than
restating a footprint, and ends with a teardown line.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/00-linux-primitives.md`](../../phases/00-linux-primitives.md). These
files hold only what you type and what you should see.

**One guest runs all of them.** [`bare`](../../strands/lab-topologies.md#bare) comes up at
exercise 1 and is destroyed at exercise 22, which ends the phase. It is 2.0GB of a
[9.5GB budget](../../strands/lab-topologies.md#ceiling) — the cheapest thing in the
curriculum, and deliberately so, because P0 fork-bombs, disk-fills and OOMs it. **Every
exercise runs as root** on that guest; `sudo -i` once per session.

**Teardown here means cleaning the guest, not destroying it.** P8 tore down a cluster;
P0 leaves namespaces, cgroups, mounts, loop devices and `iptables` rules on a box that
stays up for three weeks. The teardown lines are the exercise — an orphaned `MASQUERADE`
rule or a stray `netem` qdisc will silently break something four exercises later, and
exercise 20's is written into the artifact itself.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [One flag, one thing hidden](01-uts-namespace.md) | The smallest possible namespace, so the first thing learned is that a flag isolates *one* axis. |
| 2 | [`ps` lies until you remount `/proc`](02-pid-namespace-and-proc.md) | The PID and mount namespaces are separate, and this is the first place that costs you. |
| 3 | [A namespace is a file you can point at](03-namespaces-are-inodes.md) | Turns "in the same namespace" from a phrase into an inode comparison. |
| 4 | [Kill PID 1 and take the namespace with it](04-kill-pid-1.md) | Why `docker stop` waits, and why a container's processes cannot outlive its init. |
| 5 | [Membership is a write to a file](05-move-a-process-into-a-cgroup.md) | The delegation direction, which makes every "why does `memory.max` not exist" question self-answering. |
| 6 | [0.C1 — OOMKilled while the host barely notices](06-oom-inside-a-wall.md) | **The sentence every eviction conversation for the next ten months rests on.** The gate names it. |
| 7 | [CPU limits throttle; they never kill](07-cpu-max-throttles.md) | The other failure shape: silent, gradual, and invisible to every probe. |
| 8 | [0.C3 — fork-bomb a wall you built](08-exhaust-the-pid-limit.md) | Containment rather than performance — and the reason P0 gets a guest it may destroy. |
| 9 | [Three things must be true before a ping crosses](09-link-address-route.md) | Three distinct errors, so a broken pod network is diagnosable from the symptom alone. |
| 10 | [A bridge is what replaces N² cables](10-a-bridge-for-three.md) | A bridge per node, a veth per pod — the pod-network model, in miniature and by hand. |
| 11 | [The namespace reaches the internet through one NAT rule](11-masquerade-out.md) | `-j MASQUERADE` is the whole of pod egress, and its failure looks nothing like a routing failure. |
| 12 | [0.C2 — sever a link, then merely delay it](12-cut-a-link-then-slow-it.md) | The delayed case is the dangerous one, and it is where `netem` stops being a chaos CRD. |
| 13 | [Predict which layer a write lands in](13-overlayfs-by-hand.md) | Copy-up and whiteouts — image layering with the marketing removed. |
| 14 | [The old root has to become unreachable](14-pivot-root-vs-chroot.md) | Performs the `chroot` escape, then makes the same code fail. |
| 15 | [Predict whether a mount crosses the boundary](15-mount-propagation.md) | Three modes, three answers, and a failure mode that produces no error at all. |
| 16 | [0.C4 — the writable layer fills](16-fill-the-upper-layer.md) | Reads keep working, copy-up fails worst, and `df` describes the wrong thing. |
| 17 | [Drop one capability, lose one syscall](17-drop-a-capability.md) | Root is not a capability set, and the bounding set is the ceiling. |
| 18 | [A filter that kills on a syscall](18-seccomp-one-syscall.md) | `SIGSYS` versus `EPERM` — why a seccomp denial usually looks like an unexplained crash. |
| 19 | [Find one operation only the privileged version can do](19-the-privileged-delta.md) | Turns `privileged: true` from a scary phrase into a specific list. |
| 20 | [A container with no container runtime](20-container-from-scratch.md) | **The capstone.** Six primitives, one script, verified from outside on every axis. |
| 21 | [Every container flag, mapped to its primitive](21-docker-flags-to-primitives.md) | The second gate condition, and it finds the one flag with no kernel primitive at all. |
| 22 | [Find your script inside the OCI runtime spec](22-find-your-container-in-config-json.md) | A runtime is a program that reads that JSON and makes the calls you just made. |

**[Module 0.6](../../phases/00-linux-primitives.md#m0-6) has no exercise, and that is
deliberate.** It is the foundational reading — Borg, `architecture.md`, `principles.md`,
`object-lifecycle.md`, `controllers.md` — which runs alongside the hands-on modules and
produces written answers, not a lab. Its question-and-answer table stays in the phase
file where the rest of the reading lives.

**Exercise 22 needs no topology at all.** It is a spec and a git clone, so it can be done
on the Mac, on a train, or while `bare` is already destroyed.
