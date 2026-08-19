<a id="11c1-wedge-a-create-at-admission"></a>
# 11.C1 — a create that wedges at the admission line you just cited, diagnosed from apiserver logs alone

**Claim** — corrupt the `caBundle` on a `failurePolicy: Fail` validating webhook and a new create wedges **at the exact admission frame [Seam A](02-seam-a-client-apiserver-etcd.md) cited** — never reaching `store.go`, never becoming a `Txn` — and the apiserver log names that frame with no other instrument. The outage is the proof of the ordering: if admission ran *after* durability, the object would be in etcd and the log would say something else. It is not, and it does not.

**Rests on** — [Seam A](02-seam-a-client-apiserver-etcd.md), whose cited admission line this drill makes fail on purpose; and [the P3/P10 admission chain](../../phases/10-security.md#m10-1), the webhook dispatch you read as mechanism in P3 and as attack surface in P10.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the drill's row in the phase's chaos table](../../phases/11-synthesis.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills): this one is **by hand** and stays that way — the skill is recognising *your own* misconfiguration from the system's behaviour, which injecting the fault externally would remove.

**Do** — register a `failurePolicy: Fail` `ValidatingWebhookConfiguration` pointed at any endpoint, then corrupt its `caBundle` so the apiserver cannot complete the TLS call to it, and try to create a pod:

```sh
# with a Fail-policy webhook whose caBundle is now garbage:
kubectl patch validatingwebhookconfiguration wedge \
  --type=json -p='[{"op":"replace","path":"/webhooks/0/clientConfig/caBundle","value":"'"$(echo bogus | base64)"'"}]'
kubectl run wedged --image=nginx --restart=Never
kubectl -n kube-system logs -l component=kube-apiserver --tail=40 | grep -i 'admission\|webhook\|x509'
```

**Observe** — the create is refused, the pod never appears, and there is **no etcd key** for it (`etcdctl get /registry/pods/default/wedged` returns nothing) — because the request died at admission, above the store. The apiserver log names the webhook call failing at the admission frame you cited in Seam A. The fault is in *your* YAML, and the system's behaviour is what tells you so.

**Expect** — an `x509`/`context deadline`-shaped admission failure and an object that never persisted. This is the ordering guarantee stated as an outage: validated-before-durable means a broken validator blocks durability entirely, rather than letting an unvalidated object slip into etcd.

**Write down** — the apiserver log line, the Seam-A admission frame it corresponds to, and the confirmation that no etcd key was created — the negative half of the [Seam A](02-seam-a-client-apiserver-etcd.md) artifact.

**Teardown** — remove the webhook (the repair is part of the drill — a create must succeed again before you move on) and delete the pod if it exists; **the topology stays**:

```sh
kubectl delete validatingwebhookconfiguration wedge
kubectl delete pod wedged --ignore-not-found
kubectl run repaired --image=nginx --restart=Never && kubectl delete pod repaired
```
