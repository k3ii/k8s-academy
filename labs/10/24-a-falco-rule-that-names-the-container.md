<a id="a-falco-rule-that-names-the-container"></a>
# A rule keyed on the context, not the command — it fires on the renamed binary the last rule missed

**Artifact** — a Falco rule whose `condition` keys on *where and in what context* a process runs (an unexpected `execve` inside a specific workload's container, identified by an image or a k8s label, not by `proc.name`) — and the proof that it fires on the *same renamed binary* that [exercise 23](23-10c5-a-string-rule-a-variant-evades.md)'s string rule missed. This is the detector the phase capstone's gate demands: a rule an attacker cannot evade by renaming their tool, because the rule never looked at the tool's name.

**Rests on** — [the string-rule miss in exercise 23](23-10c5-a-string-rule-a-variant-evades.md). This exercise is that failure's answer; it only means something run immediately after the rule that missed.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Falco on the worker from [exercise 22](22-falco-reads-the-syscall.md); the bad `c5-rule` from [exercise 23](23-10c5-a-string-rule-a-variant-evades.md) removed.

**Read** — re-read [the Falco fields](https://falco.org/docs/reference/rules/supported-fields/), now for the *context* set: `container.image.repository`, `k8s.pod.label`, `proc.pname` (the parent), and `evt.type`. The question this exercise answers with a rule: *what is the field that identifies the process's container context rather than its argv* — the one from [the phase's source question](../../phases/10-security.md#m10-5) — and why is a rule built on it evasion-resistant where a `proc.name` rule is not?

**Do** — write a behavioral rule: *any exec inside the marked workload's container that is not the container's own entrypoint is suspect.* Mark a pod, load the rule, then run the renamed binary that evaded exercise 23:

```sh
WORKER=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
kubectl run guarded --image=nixery.dev/shell/netcat --labels=trust=locked \
  --overrides="{\"spec\":{\"nodeName\":\"$WORKER\"}}" --restart=Never --command -- sleep 3600
kubectl wait --for=condition=Ready pod/guarded
```

The rule keys on the k8s label and the event type, never on the binary name:

```yaml
- macro: locked_workload
  condition: k8s.pod.label.trust = locked
- rule: Unexpected exec in locked workload
  desc: any interactive/extra exec inside a workload marked trust=locked
  condition: >
    spawned_process and locked_workload
    and not proc.name in (sleep)
  output: >
    Exec in locked pod (proc=%proc.name parent=%proc.pname
    cmd=%proc.cmdline container=%container.id image=%container.image.repository
    pod=%k8s.pod.name)
  priority: CRITICAL
```

```sh
# load the rule via a rules-file configmap + helm upgrade, wait for rollout, then:
# the SAME evasion exercise 23 used — a renamed binary:
kubectl exec guarded -- sh -c 'cp $(command -v nc) /tmp/zz; /tmp/zz -w1 127.0.0.1 1 || true'
kubectl -n falco logs ds/falco | grep -i 'Exec in locked pod' | tail -3
```

**Observe** — the rule fires, and its output line names `proc=zz` — the very rename that made exercise 23's rule silent. The rule caught it because its `condition` asked *"is this an exec inside the `trust=locked` container?"*, and the answer is yes regardless of what the binary is called. The context field (`k8s.pod.label` / `container.id`) is the answer to the source question: it is reconstructed by `libsinsp` from the cgroup, is *not* part of the process's argv, and so is not something the attacker inside the container can rename or spoof. **The string rule watched what the attacker types; this rule watches where the attacker is.**

**Expect** — an alert on the renamed binary that exercise 23 missed. Tune it once: run the pod's own legitimate startup and confirm the rule does *not* fire on the entrypoint (that is the `not proc.name in (sleep)` clause, or better, an allowlist of the image's expected processes) — a detector that alerts on normal startup is a detector that gets muted.

**Write down** — the alert firing on `zz`, the one context field the rule keys on, and the sentence contrasting it with exercise 23: name vs. place. **Keep this rule; the [capstone](26-the-cve-incident.md) requires a learner-written Falco rule that survives an unseen variant, and this is its seed.**

**Teardown** — **keep the rule and Falco** for [the capstone](26-the-cve-incident.md); delete only the guarded pod; **the topology stays**:

```sh
kubectl delete pod guarded
```
