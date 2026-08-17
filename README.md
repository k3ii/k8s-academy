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

The curriculum is being **charted**, not yet written. Planning happens as a
[wayfinder map](../../issues/1) in this repo's issues:

- The **map** ([#1](../../issues/1), label `wayfinder:map`) holds the destination, the fixed
  inputs, the decisions made so far, and the fog not yet sharp enough to ticket.
- Each **ticket** is a child issue of the map resolving exactly one decision or question.
  Types: `wayfinder:research` (agent-driven), `wayfinder:grilling` (worked with a human),
  `wayfinder:prototype`, `wayfinder:task`.
- Blocking uses GitHub's native issue dependencies, so the **frontier** — what's takeable
  right now — is visible in the issue list without opening the map.

Read the map first. It carries the learner profile and lab constraints that every ticket
assumes.

The **phase spine** ([#10](../../issues/10)) is settled — thirteen phases, their order, durations,
capstones and strand attachment, plus the recorded argument for where "Kubernetes the Very Hard
Way" sits and why kubeadm and k0s are deliberately separated. It is the resolution to read
before any other. Everything in this repo is written in Go
([#9](../../issues/9)).

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
against real source material rather than in the abstract. The prototype,
[`phases/08-storage.md`](phases/08-storage.md), is now on `main`: the six
[strand docs](strands/) it links into exist ([#16](../../issues/16)), so it is the worked
example to copy from.

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
