<a id="adminnetworkpolicy-read-and-banked"></a>
# Three rules NetworkPolicy cannot express, each written in the API that can — and then banked

**Artifact** — three `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` manifests, written from [KEP-2091](../../strands/source-reading.md#area-5-networking), each paired with **the NetworkPolicy attempt at the same rule and the sentence saying why it does not hold**. Written here, applied in [P10](../../phases/10-security.md#m10-2). Nothing is installed in this exercise and that is deliberate.

**Rests on** — [exercise 24](24-the-semantics-are-in-the-comments.md). The gap this API fills is exactly the semantics you predicted there: **selection implies deny-all-else and every rule is an allow**, so a policy author can widen but never narrow, and an admin cannot bound them.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair) is up but this exercise touches it once, for a negative result. Reading otherwise.

**Read** — KEP-2091, for six specific answers. Read the goals and the API before the examples; the examples make more sense once the tiers are clear:

| Read | Answer from it |
|---|---|
| The motivation section | Which of the three roles it names — cluster admin, namespace owner, application developer — does NetworkPolicy serve, and what does it give the other two? |
| `AdminNetworkPolicy` `spec.priority` | Lower number or higher number wins, and what is the range? |
| The three actions | What does **`Pass`** do that neither `Allow` nor `Deny` can, and which tier does it hand the decision to? |
| `BaselineAdminNetworkPolicy` | Why is it a **singleton with a fixed name and no priority**, and where in the evaluation order does it sit relative to NetworkPolicy? |
| The `subject` field | How does it differ from NetworkPolicy's `podSelector`, and what does that difference make possible for a namespace that does not exist yet? |
| `egress.to` peers | Which peer types exist here that NetworkPolicy has no equivalent for? |

The evaluation order is the whole API in one line, and it should end up in your notes as one line: **ANP by priority → NetworkPolicy → BANP**, with `Pass` as the only way down a tier and no way back up.

**Do — the three rules.** For each, write the ANP or BANP object, then the closest NetworkPolicy and one sentence on how it fails:

1. **A guardrail a namespace owner cannot override.** No pod in the cluster may reach `10.10.10.0/24` on port 22, whatever any namespace's own policies say. — The NetworkPolicy attempt fails for a reason about *who can create objects in which namespace*, not about selectors.
2. **A default a namespace owner *can* override.** Ingress from outside a namespace is denied unless that namespace's own NetworkPolicy allows it. — This is the one that needs BANP rather than ANP, and saying why is the exercise.
3. **An always-allow that survives every deny.** Every pod may reach the cluster DNS service, at a priority nothing else can outrank. — Note which of [exercise 24's](24-the-semantics-are-in-the-comments.md) ten rows this makes unnecessary to worry about, and that this rule is the single most common thing hand-written into every NetworkPolicy in a real cluster.

**Do — confirm it is absent, in one command.** This is not a formality; it establishes what "banked" means:

```sh
kubectl api-resources --api-group=policy.networking.k8s.io
kubectl explain adminnetworkpolicy 2>&1 | head -3
kubectl get crd | grep -i networkpolic
```

**Expect** — nothing, an error, and only Cilium's own CRDs if anything at all. `AdminNetworkPolicy` is **not a built-in type**: it lives out of tree in the `network-policy-api` project, ships as CRDs, and is implemented by CNIs rather than by Kubernetes — which is the same shape as NetworkPolicy itself one layer up, and is why [exercise 23's](23-a-policy-nobody-enforces.md) finding generalises instead of being a quirk.

**Write down** — the three manifests, the three failed NetworkPolicy attempts, the evaluation-order line, and one sentence naming which of the three roles from the motivation section each tier serves. That table is what [P10](../../phases/10-security.md#m10-2) picks up: it arrives there as three manifests to apply against an enforcer, not as an API to meet for the first time.

**Footprint note** — three `kubectl get`s against a cluster that is already up. Nothing.

**Teardown** — nothing created. **The topology stays**, and it is the last exercise that uses it before module 7.5 turns to the kernel: [exercise 28](28-a-counter-loaded-attached-read-detached.md) opens by re-checking [the lockstep](02-the-kernel-both-sides-must-share.md) in one line, and needs both this cluster's nodes and [`forge`](../../strands/lab-topologies.md#build-guest) still standing.
