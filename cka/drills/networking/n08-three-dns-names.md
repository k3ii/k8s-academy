<a id="n08"></a>
# N8 — Resolve `svc`, `svc.ns` and the FQDN, and say why each works

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / CoreDNS

> **All three names resolve, but only one of them is a name.** The other two are prefixes that the resolver completes using the pod's search list. Knowing which is which decides whether you reach for the search list or for CoreDNS when a lookup fails, and that fork is most of DNS troubleshooting.

**Do**

1. A Service `web` in namespace `shop`. From a pod **in `shop`**, resolve `web`, `web.shop`, `web.shop.svc`, `web.shop.svc.cluster.local`. All four work.
2. From a pod in a **different** namespace, run the same four. The bare `web` now fails and the rest work. Explain that from the search list before reading on.
3. **Read `/etc/resolv.conf` in a pod and count the search entries.** On this cluster there are four:

   ```
   search shop.svc.cluster.local svc.cluster.local cluster.local factory.lan
   nameserver 10.96.0.10
   options ndots:5
   ```

   The fourth, `factory.lan`, is inherited from the node because `dnsPolicy` is `ClusterFirst`. **The exam cluster will not have it** — do not learn the count, learn where each entry comes from.
4. **Work `ndots:5` out loud.** A name with fewer than 5 dots is tried *suffixed first*, against every search entry, before being tried bare. `web.other-ns` has one dot, so it gets four suffixed attempts before the bare one. That is why an external name like `api.example.com` — three dots — costs four failed lookups before it succeeds, and why the FQDN with a trailing dot short-circuits all of it.
5. Resolve a headless Service and compare: you get pod addresses, not a single ClusterIP. Then resolve a pod's own A record form.

**Observe**

```sh
kubectl exec -n shop pod/c -- cat /etc/resolv.conf
kubectl exec -n shop pod/c -- nslookup web
kubectl exec -n other pod/c -- nslookup web            # NXDOMAIN
kubectl exec -n other pod/c -- nslookup web.shop       # works
kubectl exec -n other pod/c -- nslookup web.shop.svc.cluster.local.
```

**Done when** — you predict each of the eight results before running it, and can say which failures mean "wrong name" and which mean "DNS is broken".

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Four names, two namespaces, read the search list. | 10 min |
| **2** | A pod with `dnsPolicy: None` and a custom `dnsConfig`. Predict what breaks. | 8 min |
| **3** | Cold, no notes. Given a failing name, say in one step whether it is the name or the resolver. | 5 min |

**Teardown** — delete both namespaces.

**See also** — **N9** edits the Corefile this resolves against; **TS16** is the same mechanism met as a fault; **TS6** is CoreDNS itself down.
