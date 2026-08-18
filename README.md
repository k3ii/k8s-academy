# k8s-academy

A self-paced **expert-track Kubernetes curriculum** — from never having touched Kubernetes to
control-plane-level mastery: able to design, operate, debug, extend and secure production
clusters, read and reason about `kubernetes/kubernetes` source, and diagnose problems from
first principles. Then back up the stack, to building GitOps delivery and internal platforms on
top of it. CKAD, CKA and CKS along the way as external validation.

Optimised hard for **depth over speed**. A month on etcd internals beats a week skimming ten
topics.

The curriculum runs in two directions. Eleven phases **remove** abstraction — down through the
API machinery to Raft, cgroups and veth pairs, building toy versions of the scheduler, the
controller, the CNI plugin and the CSI driver along the way. One final phase **rebuilds** it
deliberately, as a platform other people could use. Knowing what your abstraction costs its
users is the point of doing it in that order.

## Status

**The curriculum is written.** All thirteen phase files (P0–P12) are on `main` in
[`phases/`](phases/), every [strand doc](strands/) exists, and
`python3 strands/check-anchors.py` is green with no dangling links in either direction.
What remains is to *walk* it — the labs, source traces and writeups are the learner's to run.

### Phases

Two directions: **descend** (P0–P10), remove abstraction to the syscalls; **synthesise** (P11),
trace one request all the way down; **rebuild** (P12), put abstraction back deliberately.

| # | Phase | Weeks | Cert |
|---|-------|-------|------|
| P0 | [Linux & container primitives](phases/00-linux-primitives.md) | 3–4 | |
| P1 | [Operate a cluster (deliberately shallow)](phases/01-operate-shallow.md) | 2–3 | **CKAD** |
| P2 | [etcd internals](phases/02-etcd.md) | 4–5 | |
| P3 | [API machinery](phases/03-api-machinery.md) | 5–6 | |
| P4 | [Controllers & reconciliation](phases/04-controllers.md) | 4 | |
| P5 | [Scheduler](phases/05-scheduler.md) | 4 | |
| P6 | [kubelet, the node, and observability](phases/06-kubelet-node.md) | 3–4 | |
| P7 | [Networking, L3/L4 datapath](phases/07-networking.md) | 4–5 | |
| P8 | [Storage](phases/08-storage.md) | 3–4 | **CKA** |
| P9 | [Service mesh & L7](phases/09-service-mesh.md) | 2–3 | |
| P10 | [Security & supply chain](phases/10-security.md) | 4–5 | **CKS** |
| P11 | [Synthesis](phases/11-synthesis.md) | 2–3 | |
| P12 | [GitOps & platform engineering](phases/12-gitops-platform.md) | 5–6 | |

[`phases/08-storage.md`](phases/08-storage.md) is the worked example the other twelve were
copied from — the phase drafted first, against real source, to settle the format.

### How it was planned

Planning ran as a [wayfinder map](../../issues/1) in this repo's issues, now complete — every
ticket closed, the frontier empty. The record is worth reading before the phases, because it
carries the *why*:

- The **map** ([#1](../../issues/1), label `wayfinder:map`) holds the destination, the fixed
  inputs, and every decision made along the way — including the learner profile and lab
  constraints that every phase assumes. **Read it first.**
- Each **ticket** was a child issue resolving exactly one decision or question
  (`wayfinder:research` agent-driven, `wayfinder:grilling` worked with a human,
  `wayfinder:prototype`, `wayfinder:task`), chained by GitHub's native issue dependencies so
  only the frontier was ever takeable.
- The **phase spine** ([#10](../../issues/10)) is the single resolution to read before any phase
  file — thirteen phases, their order, durations, capstones and strand attachment, plus the
  recorded argument for where "Kubernetes the Very Hard Way" sits and why kubeadm and k0s are
  deliberately separated. Everything in this repo is written in Go ([#9](../../issues/9)).

## Lab environment

The lab is the [`k3ii/factory`](https://github.com/k3ii/factory) homelab: a single Proxmox VE 9
node, Debian 13 guests provisioned by OpenTofu and configured by Ansible, on an isolated NAT'd
`10.10.10.0/24` bridge reachable only through the `factory` bastion.

The binding constraint on the whole curriculum: **~9.9GB available RAM and 6 cores**
(i5-8400T). Labs are designed for that ceiling — one cluster at a time, aggressive teardown,
and deliberate use of topics that need no cluster at all. Resource pressure, OOMKills and
eviction cascades are on the syllabus anyway, so a cramped lab produces them for real.

## Layout

The document format is settled ([#11](../../issues/11)) — chosen by drafting one full phase
against real source material rather than in the abstract. That prototype,
[`phases/08-storage.md`](phases/08-storage.md), and the six [strand docs](strands/) it links
into ([#16](../../issues/16)) came first; the other twelve phases were copied from it and are
now all on `main`.

| Path | Contents |
|------|----------|
| `phases/NN-name.md` | One file per phase, `00`–`12`. Ten fixed sections: objectives, modules, build artifact, chaos drills, talks, ecosystem, cert drill block, capstone, checklist, gate — absent sections omitted, not padded |
| `strands/` | The cross-cutting material each phase links into rather than restates: source corpus, chaos catalogue, talk index, cert curricula, build mechanics, source archaeology. The **living** form — corrected as paths move and tools release. See [`strands/README.md`](strands/README.md) |
| `research/` | Findings from `wayfinder:research` tickets. The **dated record** of what was verified, against which tree, on which date — including what could not be verified. Not edited to stay current; a stale research doc is still an accurate record |
| `journal/NN-name.md` | The learner's own notes, traces and lab writeups |
| `build/NN-artifact/` | The learner's Go modules — eleven of them, real and buildable, so the hand-wired-versus-scaffolded comparisons are a `git diff` |

Three conventions worth knowing before reading any phase file. **No source-reading item gets a
bare link** — every one carries a question to answer from the source, so reading has a target. The
words *understand* and *know* appear in no objective, checklist item or gate; everything is an
artifact, a timed production, or a claim you could be publicly wrong about. And **a fact lives in
exactly one place**: if it appears in both a strand doc and a phase file, the phase file is wrong
and the phase file is what gets edited. Phase files reach strand docs through explicit
`<a id>` anchors, which `python3 strands/check-anchors.py` verifies in both directions.
