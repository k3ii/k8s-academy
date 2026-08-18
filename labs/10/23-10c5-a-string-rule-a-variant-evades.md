<a id="10c5-a-string-rule-a-variant-evades"></a>
# 10.C5 — a rule that catches `nc` and misses `ncat`, and why the second command is the same attack

**Claim** — a Falco rule written as a string match on one command (`proc.name = nc`) fires on that exact binary and stays *silent* when the identical technique runs under a different name (`ncat`, `socat`, a copied-and-renamed `nc`). The attack is the same — an interactive reverse shell out of a container — but the rule was keyed on a spelling, not a behavior, so a one-word change defeats it. This is the exact failure the capstone's unseen-variant gate exists to catch, staged small so you cause it deliberately before it happens to you.

**Rests on** — [Falco running on the worker from exercise 22](22-falco-reads-the-syscall.md). This drill writes a bad rule into that same Falco.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Falco is still installed on the worker from [exercise 22](22-falco-reads-the-syscall.md).

**Read** — [Falco field reference](https://falco.org/docs/reference/rules/supported-fields/): `proc.name` is the executable's basename, `proc.cmdline` its argv — both *strings an attacker controls*. Contrast with `proc.pname`, `container.id`, and the fd fields, which describe *what the process is doing and where*. The question to answer: *which of these fields can an attacker change for free by renaming a file, and which describe behavior they cannot rename away?*

**Do** — load a string-match rule, trip it with the named binary, then run the same technique renamed:

```sh
WORKER=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
# a rule keyed on the command spelling
kubectl -n falco create configmap c5-rule --from-literal=c5.yaml='
- rule: Netcat In Container
  desc: naive string match
  condition: spawned_process and proc.name = nc
  output: "netcat run (command=%proc.cmdline container=%container.id)"
  priority: WARNING
'
# mount it and restart falco (helm upgrade with an extra rules file), then:
kubectl run box --image=nixery.dev/shell/netcat/socat --overrides="{\"spec\":{\"nodeName\":\"$WORKER\"}}" --restart=Never --command -- sleep 3600
kubectl wait --for=condition=Ready pod/box

# (a) the named binary — rule fires
kubectl exec box -- sh -c 'nc -w1 127.0.0.1 1 || true'
kubectl -n falco logs ds/falco | grep -i 'netcat run' | tail -1

# (b) the same technique, different name — rule silent
kubectl exec box -- sh -c 'cp $(command -v nc) /tmp/xx; /tmp/xx -w1 127.0.0.1 1 || true'
kubectl exec box -- sh -c 'ncat -w1 127.0.0.1 1 || true'   # if ncat present
kubectl -n falco logs ds/falco | grep -i 'netcat run' | tail -3
```

**Observe** — step (a) produces a `netcat run` alert; steps (b) produce *nothing new* — the renamed copy `/tmp/xx` and the sibling `ncat` did the identical thing and the rule never saw them, because `proc.name` was `xx` and `ncat`, not `nc`. That is the answer to the reading question made concrete: `proc.name` is attacker-controlled — a `cp` and a rename is all it takes — so a rule keyed on it detects only attackers who do not bother to rename. **The technique did not change; the string did, and the string was the whole rule.**

**Expect** — one alert for `nc`, silence for the renamed/sibling runs. This is a *demonstrated miss*, not a bug to fix here — [exercise 24](24-a-falco-rule-that-names-the-container.md) is the fix: a rule keyed on the connection behavior and the container context, which no rename evades.

**Write down** — the alert that fired, the two runs that did not, and the sentence: the rule matched a name the attacker chooses.

**Teardown** — remove the bad rule so it does not shadow [exercise 24](24-a-falco-rule-that-names-the-container.md); keep Falco and `box`; **the topology stays**:

```sh
kubectl -n falco delete configmap c5-rule
# helm upgrade falco back to its default rules, then:
kubectl delete pod box
```
