<a id="ts16"></a>
# TS16 — One pod resolves the name, another does not. CoreDNS is fine.

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot services and networking

> **If one pod resolves and another does not, the server is working.** Everything that matters is in the client's `/etc/resolv.conf`, and that file is written by the kubelet from the pod's own spec. Four fields decide it, none of them live in CoreDNS, and reaching for CoreDNS first costs you the whole task.

> **Pinned for a structural reason.** [The diagnostic](../../plan.md#diagnostic) probes four of Troubleshooting's five sub-competencies and probes this one nowhere, so an operator who is cold here can still score well on Troubleshooting and be allocated no hours against it. This drill runs regardless of what the diagnostic said.

**Break it** — *pass 1 only.* Make two pods disagree, four ways:

1. **Different namespaces.** The search list's first entry is the pod's own namespace, so an unqualified `web` resolves in the namespace that holds `web` and nowhere else. This is the one that catches people who are certain it is a cluster fault.
2. **`dnsPolicy: Default`.** Not the default. It means *inherit the node's resolver*, which does not know `cluster.local` at all, so cluster names fail and external names work — a very distinctive signature.
3. **`hostNetwork: true` without `dnsPolicy: ClusterFirstWithHostNetwork`.** Same outcome as above, arrived at by accident rather than on purpose, and the spec gives no hint that DNS was involved in the decision.
4. **A custom `dnsConfig`** that sets `ndots` or replaces the search list. Lower `ndots` and short names stop being tried as cluster names; raise it and every external lookup takes several extra round trips first.

**Work it** — read the file, then do the arithmetic:

```sh
kubectl exec <pod> -- cat /etc/resolv.conf
kubectl get pod <pod> -o jsonpath='{.spec.dnsPolicy}{"\n"}{.spec.dnsConfig}{"\n"}{.spec.hostNetwork}'
kubectl exec <pod> -- nslookup -debug <name>
```

On this lab a healthy pod's file reads, measured rather than assumed:

```
search <namespace>.svc.cluster.local svc.cluster.local cluster.local factory.lan
nameserver 10.96.0.10
options ndots:5
```

**Four search entries, not the three every tutorial shows.** `factory.lan` is the node's own search domain, inherited because `ClusterFirst` appends the host's. So a lookup of `web.other-ns` — two dots, fewer than `ndots:5` — is tried as a suffixed name **four times** before it is ever tried bare. **The exam's cluster will not have `factory.lan`**, so take the mechanism from here and the count from whatever is in front of you.

**Done when** — you reach the right one of the four from `resolv.conf` and the pod spec alone, having never looked at CoreDNS, and you can explain `ndots:5` as a cost rather than as a setting.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build all four disagreements and read each signature. | 10 min |
| **2** | Messy. The working pod and the broken one are in a namespace with six others. | 8 min |
| **3** | **Injected.** Two pods, one resolves, nobody says why. Cold, clock visible. | **5 min** |

**Teardown** — `cka-inject.sh revert`, then delete the namespace.

**See also** — **TS8** is the case where CoreDNS genuinely is the fault, and the first question in both drills is the same: does any other pod resolve? **N8** builds the three forms of a cluster name that the search list exists to serve.
