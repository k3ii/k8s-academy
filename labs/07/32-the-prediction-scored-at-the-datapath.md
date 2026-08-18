<a id="the-prediction-scored-at-the-datapath"></a>
# Ten predictions opened, scored, and each miss traced to the comment that would have prevented it

**Artifact** — [exercise 24's](24-the-semantics-are-in-the-comments.md) sealed table, checked out of git unmodified, scored row by row against a cluster that can now enforce policy, with a third column added: **which component gave the answer** — the API server, Cilium's policy engine, or the kernel's connection tracker. That column is the point. A semantics table with no attribution reads as though Kubernetes decided all ten, and it decided fewer than half.

**Rests on** — [exercise 24](24-the-semantics-are-in-the-comments.md) for the predictions and [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) for the enforcer. It also settles [exercise 23's](23-a-policy-nobody-enforces.md) open question, which was what the deny-all was going to do once something read it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, on Cilium, with kube-proxy gone.

**Setup — open the envelope, and do not edit it**

```sh
cd ~/src/k8s-academy && git show <the exercise-24 commit>:journal/p7-policy-predictions.md
kubectl create ns pol && kubectl label ns pol team=x
kubectl create ns pol-other
kubectl -n pol create deployment b --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- /agnhost netexec --http-port=8080
kubectl -n pol expose deployment b --port=8080
kubectl -n pol run a --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --labels app=a --command -- sleep 3600
kubectl -n pol-other run a --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --labels app=a --command -- sleep 3600
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list | head
```

Score into a **copy**. The committed file is evidence and stays as written, including the rows that turn out wrong — a prediction quietly corrected after the fact teaches nothing on the second reading.

**Do — instrument first, so that every result has a witness other than `curl`**

```sh
kubectl -n kube-system exec ds/cilium -- cilium-dbg monitor --type drop &
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list -o json | \
  jq -r '.[] | [.status.external-identifiers.pod-name, .status.policy.realized["policy-enabled"]] | @tsv'
```

`policy-enabled` per endpoint is the single most useful field in this exercise: it is `none` until something selects the pod and then it names the directions, which is [exercise 24's](24-the-semantics-are-in-the-comments.md) first comment turned into an observable field.

**Do — walk the ten rows.** Apply the manifests your predictions were about, one at a time, and after each: run the traffic, read `cilium monitor`, and read `policy-enabled` again. The three that need care:

```sh
# rows 5 and 6 — one list element with two selectors, then two list elements
kubectl -n pol apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: and-form}
spec:
  podSelector: {matchLabels: {app: b}}
  ingress:
  - from:
    - podSelector: {matchLabels: {app: a}}
      namespaceSelector: {matchLabels: {team: x}}
YAML
kubectl -n pol exec a -- curl -sS -m3 -o /dev/null -w '%{http_code}\n' http://b:8080/hostname
kubectl -n pol-other exec a -- curl -sS -m3 -o /dev/null -w '%{http_code}\n' http://b.pol:8080/hostname
# then the same file with a `- ` before namespaceSelector, and both requests again
```

```sh
# row 7 — what the API server did to a policy whose policyTypes you omitted
kubectl -n pol apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: egress-only}
spec:
  podSelector: {matchLabels: {app: a}}
  egress:
  - to: [{podSelector: {matchLabels: {app: b}}}]
YAML
kubectl -n pol get netpol egress-only -o jsonpath='{.spec.policyTypes}{"\n"}'
```

```sh
# row 8 — a name, under an egress policy that allows the backend and says nothing about DNS
kubectl -n pol exec a -- curl -sS -m3 http://b:8080/hostname; echo "exit=$?"
kubectl -n pol exec a -- curl -sS -m3 http://<b-pod-ip>:8080/hostname; echo "exit=$?"
kubectl -n kube-system exec ds/cilium -- cilium-dbg monitor --type drop --related-to <a's endpoint id>
```

**Gate** — every row scored against the committed text, and **every miss carries the citation that would have prevented it** — a field comment, a line of `network-policy.md`, or "no document says this; it is the enforcer's choice". The third answer is a legitimate outcome for at most two rows, and identifying *which* two is the real result of the exercise.

**Expect** — rows 5 and 6 to differ, in the direction the comments said and possibly not in the direction you predicted; `policyTypes` in row 7 to come back **defaulted by the API server** with `["Egress"]` already filled in, which means that row could have been scored at [exercise 24](24-the-semantics-are-in-the-comments.md) with no enforcer at all — one of the ten was never a datapath question.

Expect **row 8 to fail on the name and succeed on the address**, with a drop event naming port 53 — the whole of [exercise 26](26-7c2-it-was-dns.md) arriving as a consequence of a policy that mentions neither DNS nor CoreDNS. Nothing in the manifest is wrong. This is the single most common NetworkPolicy outage there is, and having produced it deliberately, once, is worth more than the rule that prevents it.

Expect row 4 to be answered by **conntrack rather than by policy** — the reply to an allowed connection is allowed because the connection is tracked, not because a rule permits it — and row 10 to be answered by neither the API nor the comments but by **Cilium's identity model**, where host traffic carries a reserved identity. Those two rows are where the "which component answered" column earns itself.

**Write down** — the scored ten-row table with the attribution column; the two rows nothing documents; and the one-sentence AND-vs-OR statement from [exercise 24](24-the-semantics-are-in-the-comments.md), now either confirmed or corrected against the measurement. That sentence is [the checklist's](../../phases/07-networking.md#checklist) policy item and [drill 7.C4](33-7c4-a-policy-that-reads-correct.md) is about to test whether you can apply it under a false impression rather than recite it.

**Footprint note** — two namespaces, three small pods. `cilium monitor` is a stream, not a workload; leave it running only while you need it. No change to the tenancy [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) settled.

**Teardown**

```sh
kubectl -n pol delete netpol --all
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list -o json | jq -r '.[].status.policy.realized["policy-enabled"]' | sort | uniq -c
kill %1
```

Confirm every endpoint is back to `none` before moving on — [drill 7.C4](33-7c4-a-policy-that-reads-correct.md) diagnoses a policy that reads correct, and a leftover policy from this exercise would make it diagnosable by accident. Keep the `pol` and `pol-other` namespaces and the pods: the drill uses exactly this arrangement. **The topology stays.**
