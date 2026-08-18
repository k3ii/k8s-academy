<a id="7c4-a-policy-that-reads-correct"></a>
# 7.C4 — three policies that read correct, picked blind, named from the policy map in ten minutes

**Artifact** — drill [7.C4](../../phases/07-networking.md#chaos), run as three blind rounds: a script applies one of three policies whose YAML reads correct to a hostile reviewer, and you name **which class of wrong it is** and **prove it from the eBPF policy map**, not from a `curl`. The deliverable is the differential procedure you end up with — three checks in an order, each of which rules something out.

**Rests on** — [exercise 32](32-the-prediction-scored-at-the-datapath.md) for the scored semantics and the `pol`/`pol-other` namespaces, and [exercise 30](30-a-drop-decided-by-a-map-entry.md) for the habit of treating a map dump as evidence and a request as an anecdote.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, on Cilium. Nothing is installed; this is a by-hand drill for [the reason the phase gives](../../phases/07-networking.md#chaos) — reading the rule that broke *is* the exercise.

**Setup — three policies and a picker you do not read the output of**

Write all three now, while you are calm, and then do not look at the directory again:

```
/root/7c4/a.yaml   ingress from {podSelector: app=a, namespaceSelector: team=x}   — one list element
/root/7c4/b.yaml   ingress from two separate list elements, same two selectors
/root/7c4/c.yaml   spec.podSelector: {matchLabels: {app: bb}}  — everything else identical to b
```

The intent, in English, for all three: *pods labelled `app=a` in namespaces labelled `team=x` may reach `b`; nobody else may.* Each of the three is a plausible transcription of that sentence and each has a different relationship to it.

```sh
cat > /root/7c4/pick.sh <<'SH'
#!/bin/sh
set -e
f=$(ls /root/7c4/[abc].yaml | shuf -n1)
kubectl -n pol delete netpol --all >/dev/null 2>&1 || true
kubectl -n pol apply -f "$f" >/dev/null
echo "$f" > /root/7c4/.answer
date -Is
SH
chmod +x /root/7c4/pick.sh
```

**Do — one round.** Start a clock. Ten minutes. You may run anything except `cat /root/7c4/.answer` and anything that reveals the applied YAML — **`kubectl get netpol -o yaml` is off limits for the first five minutes**, because reading the policy is what a reviewer already did and it did not help.

```sh
sudo /root/7c4/pick.sh
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list | grep -E 'pol|POLICY'
EP=<b's endpoint id>
kubectl -n kube-system exec ds/cilium -- cilium-dbg bpf policy get $EP
kubectl -n kube-system exec ds/cilium -- cilium-dbg identity list | grep -E 'app=a|k8s:io.kubernetes.pod.namespace=pol'
kubectl -n pol exec a -- curl -sS -m3 -o /dev/null -w '%{http_code}\n' http://b:8080/hostname
kubectl -n pol-other exec a -- curl -sS -m3 -o /dev/null -w '%{http_code}\n' http://b.pol:8080/hostname
```

**Gate** — name the class **before** opening `.answer`, and state the single command whose output decided it. Run three rounds; the drill is passed when all three are named from the map rather than from the two `curl`s, because the `curl`s cannot distinguish two of the three cases and the map can distinguish all three in one dump.

| Class | What the author meant | What the cluster does | The check that names it |
|---|---|---|---|
| Over-restrict | | | |
| Over-allow | | | |
| No-op | | | |

**Expect** — the identity list to be where this becomes readable: Cilium compiles selectors into **numeric identities**, and the policy map for `b` lists the identities allowed to reach it. One selector combined with AND produces a *narrower* identity set than two selectors combined with OR, and the difference is visible as a count of allowed keys — a small integer, in a dump, that answers a question the YAML cannot.

Expect the no-op case to be the fastest to name and the most alarming: `cilium endpoint list` shows `policy-enabled: none` on `b` while `kubectl get netpol` shows a policy that exists, is accepted, has no error, and selects nothing. **A typo in a label selector is a silent, cluster-wide permit**, and it is the same silence as [exercise 23](23-a-policy-nobody-enforces.md) — a policy nothing enforces — arriving by a different route.

Expect the over-allow case to be the slowest, and this is the drill's real lesson: **nothing is broken, so nothing shows up.** No drop event, no failing request, no alert. It is found only by sending traffic you expect to be refused and noticing that it was not — a negative test, which is the one kind of test people leave out. Write that down as a sentence about monitoring, not about policy: an over-restrict announces itself and an over-allow never will.

**Write down** — the three-row table with your final differential procedure in order; the identity counts for the AND and OR forms; and one sentence for a reviewer's checklist — the question to ask about any NetworkPolicy that reads correct, phrased so that it takes ten seconds to answer. That sentence closes [the checklist's](../../phases/07-networking.md#checklist) policy item, which [exercise 24](24-the-semantics-are-in-the-comments.md) opened, [exercise 32](32-the-prediction-scored-at-the-datapath.md) tested, and this drill has now tried to fool you with three times.

**Footprint note** — one policy at a time on an existing cluster. Nothing.

**Teardown**

```sh
kubectl -n pol delete netpol --all
kubectl delete ns pol pol-other
rm -rf /root/7c4
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list | grep -c 'Disabled' || true
```

**The topology stays** — [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) is next and needs this cluster, this CNI and one live policy. It is also where the topology finally goes.
