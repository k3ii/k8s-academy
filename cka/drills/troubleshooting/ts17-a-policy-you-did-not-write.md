<a id="ts17"></a>
# TS17 — Traffic that should flow is silently dropped: prove it is the policy, not the app

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot services and networking

> **A NetworkPolicy drop looks exactly like an application hang.** No log line, no event, no error anywhere in the cluster — the packet is simply not delivered, and the client sits there until it times out. The skill is getting from "the app is broken" to "something is dropping this" in under a minute, and then to *which* policy.

**Break it** — *pass 1 only.*

Recreate the three shapes that actually occur, and note that two of them are policies on the **other** end:

1. **Egress with no DNS carve-out** — the common one. See [N3](../networking/n03-egress-with-dns-carve-out.md) for how it is built.
2. **An ingress policy on the destination namespace** that does not select your client. Your side is clean; nothing you can see from the client's namespace explains it.
3. **A default-deny** applied namespace-wide weeks ago by someone else, which every new workload inherits silently.

**Work it** — the tell first, then the ladder:

- **Timeout, not refused.** `Connection refused` means something answered — a live host with nothing listening, so the path is fine and the fault is the app or the port. A **hang** means the packet died in transit. Learn to read these two apart before anything else; it halves the search immediately.
- **DNS fails before TCP does.** If `nslookup` hangs too, suspect egress on the *client* side, because almost nothing else breaks name resolution and connectivity together.
- **Both ends.** List policies in the client's namespace *and* the server's. A connection must be permitted by egress at the source and ingress at the destination, independently, and the policy that is dropping you is frequently in a namespace you were not looking at.
- **Prove it, do not infer it.** Temporarily relabel the client pod so the restrictive policy no longer selects it, re-test, and relabel back. That is a one-line, reversible experiment that turns a suspicion into a fact. Deleting the policy proves the same thing and is much harder to undo on a cluster you do not own.

**Observe**

```sh
kubectl get netpol -A
kubectl describe netpol -n <client-ns>; kubectl describe netpol -n <server-ns>
kubectl get pods --show-labels -n <client-ns>
kubectl exec <client> -- nslookup <svc>
kubectl exec <client> -- wget -qO- --timeout=3 http://<svc>      # hang vs refused
kubectl -n kube-system logs ds/kube-network-policies --tail=50
```

**Done when** — you name the policy and the direction (its egress or their ingress) before changing anything, and your proof is a reversible relabel rather than a deletion.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. You plant each of the three yourself. | 10 min |
| **2** | A namespace with four policies in it, three of them irrelevant. | 8 min |
| **3** | **Injected.** One is already in place and nobody says which, or in which namespace. | **5 min** |

**Teardown** — `cka-inject.sh revert`, then delete both namespaces. A forgotten default-deny poisons every later drill in that namespace and presents as something else entirely.

**See also** — [N3](../networking/n03-egress-with-dns-carve-out.md), the policy written rather than discovered.
