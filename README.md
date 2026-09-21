# k8s-academy

k8s-academy is a self-paced Kubernetes curriculum. It starts at zero and ends at
control-plane-level skill.

When you finish, you can do these things:

- design, operate, debug, extend, and secure production clusters
- read and reason about the `kubernetes/kubernetes` source code
- find the cause of a problem from first principles
- build GitOps delivery and internal platforms on top of Kubernetes

The curriculum also prepares you for three certificates: CKAD, CKA, and CKS.

This curriculum chooses depth, not speed. It is better to study one topic for a
month than ten topics for a week.

## How the curriculum works

The curriculum goes in two directions.

- **Descend (P0–P10).** You remove one layer of abstraction at a time. You go
  down to the API machinery, Raft, cgroups, and veth pairs. You build small
  versions of the scheduler, the controller, the CNI plugin, and the CSI driver.
- **Synthesise (P11).** You follow one request all the way down the stack.
- **Rebuild (P12).** You put the abstraction back. You build a platform for
  other people to use.

You build the platform last for a reason. First you learn what each abstraction
costs the people who use it.

## Status

The curriculum and its labs are complete.

- All 13 phase files (P0–P12) are in [`phases/`](phases/).
- All 13 lab directories are in [`labs/`](labs/).
- The [strand docs](strands/) hold the cross-cutting material.
- The labs hold 357 exercises. Each exercise is one file. Each file gives a
  claim to test or an artifact to build, the exact commands, the expected
  result, the resource cost, and the teardown steps.
- `python3 strands/check-anchors.py` passes in both directions.

The rest of the work is yours. Walk the exercises. Write your journal and source
traces. Build the Go modules.

## Phases

The phases run in three stages: **descend** (P0–P10), **synthesise** (P11), and
**rebuild** (P12).

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

[`phases/08-storage.md`](phases/08-storage.md) is the worked example. It was
written first, against real source code, to set the format. The other twelve
phases follow it.

## Lab environment

The lab is the [`k3ii/factory`](https://github.com/k3ii/factory) homelab. It has
one Proxmox VE 9 node. The guests run Debian 13. OpenTofu provisions the guests.
Ansible configures them. The network is an isolated NAT `10.10.10.0/24` bridge.
You reach it through the `factory` bastion.

The hardware sets the main limit: about 9.9 GB of RAM and 6 cores (i5-8400T).
About [9.5 GB is available for a lab topology](strands/lab-topologies.md#ceiling)
after the always-on guests and the page-cache reserve. The labs work within this
limit. They run one cluster at a time and tear it down quickly. Some topics need
no cluster at all. Resource pressure, OOMKills, and eviction cascades are part of
the syllabus, so a small lab creates them for real.

## Layout

| Path | Contents |
|------|----------|
| `phases/NN-name.md` | One file per phase, `00`–`12`. Each file has up to ten fixed sections: objectives, modules, build artifact, chaos drills, talks, ecosystem, cert drill block, capstone, checklist, and gate. A phase omits a section it does not need. |
| `labs/NN/` | One directory per phase. One numbered file per exercise, in the order the phase intends. Each file gives a claim to test or an artifact to build, the exact commands, the observable result, its [topology](strands/lab-topologies.md#topologies), and its teardown. |
| `strands/` | The cross-cutting material each phase links to instead of repeating: source corpus, chaos catalogue, talk index, cert curricula, build mechanics, source archaeology, and lab topologies. This material is kept current as paths move and tools release. See [`strands/README.md`](strands/README.md). |
| `research/` | The findings from research tickets. This is a dated record of what was verified, against which tree, and on which date. It also records what could not be verified. It is not edited to stay current. A stale research doc is still an accurate record. |
| `journal/NN-name.md` | Your own notes, traces, and lab writeups. |
| `build/NN-artifact/` | Your Go modules. There are eleven of them. They are real and they build, so the hand-wired-versus-scaffolded comparison is a `git diff`. |

Three rules apply to every phase file.

- **Every source-reading item has a question.** No item is only a bare link. You
  read the source to answer something.
- **The words *understand* and *know* are not used** in any objective, checklist
  item, or gate. Every goal is an artifact, a timed task, or a claim that someone
  can prove wrong.
- **Each fact lives in one place.** If a fact is in both a strand doc and a phase
  file, the phase file is wrong, and you edit the phase file. Phase files link to
  strand docs through `<a id>` anchors. `python3 strands/check-anchors.py` checks
  these anchors in both directions.
