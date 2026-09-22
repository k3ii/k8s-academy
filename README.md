# k8s-academy

k8s-academy is a self-paced Kubernetes curriculum. It starts at zero and ends at
control-plane-level skill.

This site holds the two parts you run yourself: the **Labs** and the **Blogwalk**.
The full curriculum sits behind them as reference material — see [Full
curriculum](#full-curriculum) below.

## Labs

The labs hold 357 hands-on exercises, grouped by phase (`00`–`12`). Each exercise is
one file. Each file gives you four things:

- a claim to test, or an artifact to build
- the exact commands
- the result you should see
- the resource cost and the teardown steps

Start at [Phase 0 — Linux and container primitives](labs/00/). Then work up one phase
at a time. Each exercise runs alone, so you can also start at the phase you want.

Each lab links its [topology](strands/lab-topologies.md#topologies) instead of
repeating a resource footprint, and ends with a teardown line. The framing for each
phase — why a module exists, what to read, and the question to answer — stays in the
[phase file](phases/).

## Blogwalk

The [Blogwalk](blogwalk/) walks eleven years of the Kubernetes blog, from March 2015
to August 2026. That is 767 posts, read one by one. Some posts are still exercises you
can run. Most of them broke over time, and the broken ones teach the most.

The Blogwalk is supplementary. It gates no lab. It has its [own reading
order](blogwalk/#where-to-start): start at 2015 and walk each year in turn, or follow
one topic across the years.

## Lab environment

The lab is the [`k3ii/factory`](https://github.com/k3ii/factory) homelab. It has one
Proxmox VE 9 node. The guests run Debian 13. The network is an isolated NAT
`10.10.10.0/24` bridge. The hardware sets the limit — about 9.9 GB of RAM and 6 cores
(i5-8400T). The labs run one cluster at a time and tear it down fast. Some topics need
no cluster at all. Resource pressure, OOMKills, and eviction cascades are part of the
syllabus, so a small lab creates them for real.

## Full curriculum

The labs are organised by 13 phases. The phases go in three stages: **descend**
(P0–P10) removes one layer of abstraction at a time, **synthesise** (P11) follows one
request down the whole stack, and **rebuild** (P12) puts the abstraction back as a
platform. The phase files are the reference material the labs draw on. They prepare
you for three certificates: CKAD, CKA, and CKS.

| # | Phase | Cert |
|---|-------|------|
| P0 | [Linux & container primitives](phases/00-linux-primitives.md) | |
| P1 | [Operate a cluster (deliberately shallow)](phases/01-operate-shallow.md) | **CKAD** |
| P2 | [etcd internals](phases/02-etcd.md) | |
| P3 | [API machinery](phases/03-api-machinery.md) | |
| P4 | [Controllers & reconciliation](phases/04-controllers.md) | |
| P5 | [Scheduler](phases/05-scheduler.md) | |
| P6 | [kubelet, the node, and observability](phases/06-kubelet-node.md) | |
| P7 | [Networking, L3/L4 datapath](phases/07-networking.md) | |
| P8 | [Storage](phases/08-storage.md) | **CKA** |
| P9 | [Service mesh & L7](phases/09-service-mesh.md) | |
| P10 | [Security & supply chain](phases/10-security.md) | **CKS** |
| P11 | [Synthesis](phases/11-synthesis.md) | |
| P12 | [GitOps & platform engineering](phases/12-gitops-platform.md) | |
