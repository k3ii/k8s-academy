<a id="the-semantics-are-in-the-comments"></a>
# Ten policy questions answered from the type comments, sealed, and scored eight exercises later

**Artifact** — a ten-row prediction table, written from the comments in `staging/src/k8s.io/api/networking/v1/types.go` and from `network-policy.md`, committed to the repository **before** anything can enforce it, and scored at [exercise 32](32-the-prediction-scored-at-the-datapath.md) against Cilium. The value is in the sealing: a semantics table written after the cluster has answered is a transcript, not a prediction.

**Rests on** — [exercise 23](23-a-policy-nobody-enforces.md), which established that this cluster cannot currently answer any of these questions, and that the API will accept every one of the manifests below regardless of whether it means what you think.

This mirrors [P3's reinvocation prediction](../../phases/03-api-machinery.md#m3-4), written at one exercise and scored eight later, for the same reason: **the normative semantics are the field comments**, and reading them well is a skill that only shows up when the answer is not yet available to peek at.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and idle. Nothing here is applied.

**Read** — the `NetworkPolicy` types and their comments, in full — 37 KB of file but the policy types are a small part of it, and **navigate by type name**. Then `network/network-policy.md` for intent. Five comments carry the whole semantics and each one is a sentence or two:

- what happens to a pod the moment **any** policy selects it, per direction;
- how multiple policies selecting the same pod combine;
- how multiple rules within one policy combine;
- how the peers **within a single `from` element** combine;
- what `policyTypes` does when it is omitted and an `egress` block is present.

**Do** — answer all ten. `ALLOW` or `DENY`, plus one clause of reasoning. No cluster, no guessing at implementation behaviour: every answer must be defensible from a comment.

| # | Scenario | Prediction |
|---|---|---|
| 1 | Namespace has [exercise 23's](23-a-policy-nobody-enforces.md) deny-all-ingress. Pod `a` → pod `b` on port 8080. | |
| 2 | Same, plus a second policy selecting `b` that allows ingress from `app=a`. Pod `a` → `b`. | |
| 3 | Same as 2. Pod `b` → pod `a`. | |
| 4 | Same as 2, and `b` replies to `a`'s established connection. | |
| 5 | A policy on `b` with `from: [{podSelector: {matchLabels: {app: a}}, namespaceSelector: {matchLabels: {team: x}}}]` — **one list element, two selectors**. Pod `a` in a namespace **without** `team: x` → `b`. | |
| 6 | The same two selectors as **two separate list elements**. Same traffic. | |
| 7 | A policy with `egress` rules and **`policyTypes` omitted entirely**. Does the pod's *ingress* become restricted? | |
| 8 | A pod restricted by egress policy, allowed to reach `app=web` pods, calls `http://web.svc/` **by name**. | |
| 9 | A policy with `ingress: [{ports: [{port: 8080}]}]` and no `from` at all. Traffic from anywhere on 8080. | |
| 10 | A policy selecting `b`, and traffic arriving from a pod with `hostNetwork: true` on the same node. | |

**Rows 5 and 6 are the classic mistake** and they are why this table exists — the same two selectors, the same intent in English, and two different answers. Row 8 is the second-most-expensive one in practice, and its answer is not in the `NetworkPolicy` comments at all: it is a consequence of *where* in the datapath the policy is evaluated relative to the Service DNAT, which means it is the one row you cannot fully defend yet. **Predict it anyway and mark it as reasoned rather than cited** — [exercise 32](32-the-prediction-scored-at-the-datapath.md) is where that reasoning is tested, and row 10's answer is implementation-defined in the same way.

**Do — seal it.** The commit is the mechanism; without it, the table is editable:

```sh
ssh zain@10.10.10.125
cd ~/src/k8s-academy
$EDITOR journal/p7-policy-predictions.md
git add -A && git commit -m "P7: NetworkPolicy semantics predicted before any enforcer exists" && git push
git log -1 --format='%H %ci'
```

Write that commit hash into the notes. [Exercise 32](32-the-prediction-scored-at-the-datapath.md) opens by checking it out.

**Expect** — to find rows 3, 4 and 7 easier than they look and rows 5, 6 and 9 harder. Expect at least one row where two comments seem to conflict; when that happens, the tie-break is `network-policy.md`'s statement of intent, and **which comment you had to fall back on is itself worth recording** — it is a fact about how well the type documents itself.

**Write down** — the ten predictions with a one-clause reason each, the commit hash, and separately: **the AND-vs-OR rule stated correctly in one sentence**, which is [a checklist item](../../phases/07-networking.md#checklist) in its own right and should be a sentence you would be happy to have quoted back at you.

**Footprint note** — reading and one git commit. Nothing.

**Teardown** — nothing created; the deny-all from [exercise 23](23-a-policy-nobody-enforces.md) stays in place. **The topology stays** — [exercise 25](25-a-name-resolved-in-five-hops.md) turns to DNS, which is where this phase's failures actually live.
