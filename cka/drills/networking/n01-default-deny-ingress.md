<a id="n01"></a>
# N1 — Default-deny ingress across a namespace, and prove it took

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Network Policies

> **An empty selector means "every pod", and that is the whole trick.** `podSelector: {}` with `policyTypes: [Ingress]` and no rules is the canonical default-deny, and it is four lines. Being able to write it from memory is worth more than understanding any other policy, because every other policy in the namespace is read against it.

> **Enforcement is not free here.** Flannel does not implement NetworkPolicy. Enforcement comes from the `kube-network-policies` DaemonSet in `kube-system`; confirm it is running before concluding anything, because an unenforced policy and a permissive one look identical.

**Do**

1. Two pods that can reach each other. Prove it before you break it — a baseline you did not take is a baseline you will argue with later.
2. Apply the default-deny. Re-test: the call now **hangs** rather than being refused, which is the NetworkPolicy signature.
3. **Check what it did not do.** Egress still works, because `policyTypes` named only `Ingress`. DNS still resolves. Pods can still reach the outside. A default-deny ingress is much narrower than people expect, and assuming otherwise is how an "allow" rule gets written in the wrong direction.
4. **Policies are additive and there is no deny rule.** Add a second, permissive policy and watch access come back — nothing "overrides" the deny, the union of all matching policies simply now permits it. Say that out loud; it is the model.
5. Prove the scope: a pod in another namespace is unaffected. A NetworkPolicy is a namespaced object and the empty selector means every pod *in this namespace*.

**Observe**

```sh
kubectl -n kube-system get ds kube-network-policies
kubectl exec a -- wget -qO- --timeout=3 http://b        # hangs once denied
kubectl describe netpol default-deny
kubectl get netpol -o yaml
```

**Done when** — you write the four-line policy from memory, and can state without testing which of DNS, egress and cross-namespace traffic it affects.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Baseline, deny, verify, add the permissive policy. | 10 min |
| **2** | A namespace with running workload. Apply deny without breaking what matters. | 8 min |
| **3** | Cold, no notes. Deny-all for **both** directions, and know what that costs DNS. | 5 min |

**Teardown** — delete the namespace. A forgotten default-deny is the most expensive litter on this cluster, because it presents as something else entirely.

**See also** — **N2** is the allow rule on top, **N3** the egress case and its DNS trap, **TS17** the whole thing met as a fault.
