# k8s-academy

A self-paced **expert-track Kubernetes curriculum** — from never having touched Kubernetes to
control-plane-level mastery: able to design, operate, debug, extend and secure production
clusters, read and reason about `kubernetes/kubernetes` source, and diagnose problems from
first principles. CKAD, CKA and CKS along the way as external validation.

Optimised hard for **depth over speed**. A month on etcd internals beats a week skimming ten
topics.

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

## Lab environment

The lab is the [`k3ii/factory`](https://github.com/k3ii/factory) homelab: a single Proxmox VE 9
node, Debian 13 guests provisioned by OpenTofu and configured by Ansible, on an isolated NAT'd
`10.10.10.0/24` bridge reachable only through the `factory` bastion.

The binding constraint on the whole curriculum: **~9.9GB available RAM and 6 cores**
(i5-8400T). Labs are designed for that ceiling — one cluster at a time, aggressive teardown,
and deliberate use of topics that need no cluster at all. Resource pressure, OOMKills and
eviction cascades are on the syllabus anyway, so a cramped lab produces them for real.

## Layout

Filled in as the map resolves. The document format is itself a ticket
([#11](../../issues/11)) — a full phase gets drafted first so the structure is chosen against
something concrete rather than in the abstract.

| Path | Contents |
|------|----------|
| `research/` | Findings from `wayfinder:research` tickets — source-reading corpus, talk lists, exam curricula, tooling comparisons |
