<a id="w02"></a>
# W2 — `nodeAffinity`, required against preferred

**Reflex** · **Core** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Workloads and Scheduling / Pod admission and scheduling

> **Required is a filter; preferred is a score.** A `required` rule nothing satisfies leaves the pod `Pending` forever. A `preferred` rule nothing satisfies changes nothing at all — the pod schedules somewhere and gives no sign the rule was ignored. Confusing the two produces both of the classic outcomes: a pod that never runs, and a placement rule that silently does nothing.

**Do**

1. Label the three nodes with something you choose — `disk=ssd` on one, `disk=hdd` on the others. Real node labels (`kubernetes.io/hostname`, `node-role.kubernetes.io/control-plane`) also work and are worth reading first.
2. `requiredDuringSchedulingIgnoredDuringExecution` for `disk=ssd`. It lands on the one node. Delete the label while the pod is running — **it keeps running**. That is the `IgnoredDuringExecution` half of the name, and it is the half that gets forgotten.
3. Recreate the pod with the label gone. Now it is `Pending`, and the event names node-affinity as the reason. Compare that event text to W1's `Insufficient cpu`; being able to tell those two apart at a glance is the skill.
4. `preferredDuringSchedulingIgnoredDuringExecution` with a `weight`, for a label no node has. It schedules anyway, with nothing in the events to say the preference failed. Confirm the silence.
5. **The operators beyond `In`.** Write `NotIn`, `Exists` and `DoesNotExist`, and `Gt`/`Lt` for a numeric label. `NotIn` plus `Exists` is how anti-placement is expressed; there is no `nodeAntiAffinity`.
6. Then the blunt instrument for contrast: `nodeSelector`, which is an exact-match AND over labels and has no preferred form. Know when it is enough — on the exam it usually is, and it is four lines shorter.

**Observe**

```sh
kubectl get nodes --show-labels
kubectl label node <n> disk=ssd
kubectl get pod pinned -o wide
kubectl describe pod pinned | sed -n '/Events/,$p'
kubectl label node <n> disk-          # running pod survives
```

**Done when** — you write both forms from memory and can say, for a given pod and cluster, whether it will be `Pending` or merely placed somewhere unexpected.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both forms, the operators, the live label removal. | 10 min |
| **2** | A Deployment already using `nodeSelector`. Convert it to affinity without downtime. | 8 min |
| **3** | Cold, no notes. Required affinity onto one named node. | 5 min |

**Teardown** — delete the pods **and remove the node labels**. A stray label on a node outlives the namespace and will confuse a later drill.

**See also** — **W3** is the node's own veto; **W4** spreads rather than pins.
