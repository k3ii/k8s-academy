<a id="a-name-resolved-in-five-hops"></a>
# One `curl` by name, counted in DNS queries and mapped to five distinct hops

**Claim** — resolving `web` from inside a pod costs two queries and resolving `github.com` from the same pod costs **eight**, and both answers travel the same nftables verdict map [exercise 17](17-the-same-service-as-a-verdict-map.md) read — so a DNS lookup is a *client* of this phase's datapath, not a layer beside it. Both halves are measurable in this cluster today.

**Rests on** — [exercise 17](17-the-same-service-as-a-verdict-map.md) for the map that `10.96.0.10` resolves through, and [exercise 15](15-the-reconciler-and-its-packing-heuristic.md) for the EndpointSlice that CoreDNS is itself watching.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — before measuring, answer three questions. The first two from the *It Wasn't DNS* talk ([`talks.md#networking`](../../strands/talks.md#networking)), the third from source:

| Read | Answer from it |
|---|---|
| The talk's diagnostic procedure | What are its **first three checks**, in order — and which of the three is the one people skip? |
| The same talk on `ndots` | Why is `ndots:5` the default when the names it exists to serve have one or two dots? |
| `pkg/kubelet/network/dns/dns.go` — the function that composes the file | **Who writes a pod's `/etc/resolv.conf`**, from which config field, and what do `dnsPolicy: ClusterFirst`, `Default` and `None` each select? Give the `file:line` for the search-list assembly. |

The third answer is the one that matters for the rest of the phase: the file is **not** mounted from the node and **not** written by CoreDNS.

**Setup** — a namespace of its own, because the module-7.3 namespace is called `svc` and `web.svc.svc.cluster.local` is a name no reader should have to parse:

```sh
kubectl create ns dns
kubectl -n dns create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=2 -- /agnhost netexec --http-port=8080
kubectl -n dns expose deployment web --port=80 --target-port=8080
kubectl -n dns expose deployment web --name=web-headless --cluster-ip=None --port=80 --target-port=8080
```

Then turn CoreDNS into an instrument by adding one plugin. Nothing else in this exercise needs a change:

```sh
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | tee /root/corefile.orig
kubectl -n kube-system get configmap coredns -o yaml > /root/coredns-cm.orig.yaml
kubectl -n kube-system edit configmap coredns     # add a line `log` inside the `.:53 { }` block
kubectl -n kube-system rollout restart deployment coredns
kubectl -n kube-system rollout status deployment coredns
```

Read the `Corefile` you just backed up before you edit it: the `kubernetes`, `cache`, `forward` and `ttl` directives each explain a measurement below, and `cache 30` in particular will make your query counts wrong if you reuse a name.

**Do — hop 1, the file nobody in the pod wrote**

```sh
kubectl -n dns run probe --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
  --restart=Never --command -- sleep 3600
kubectl -n dns exec probe -- cat /etc/resolv.conf
kubectl -n dns get pod probe -o jsonpath='{.spec.dnsPolicy}{"\n"}'
ssh zain@10.10.10.131 'sudo grep -i clusterDNS -A2 /var/lib/kubelet/config.yaml'
```

**Do — hops 2 and 3, counted.** Use a **fresh name each time** so `cache 30` does not answer for you, and read the counts from CoreDNS rather than from the pod:

```sh
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=0 -f > /tmp/dns.log 2>&1 &
kubectl -n dns exec probe -- getent hosts web                                   # A
kubectl -n dns exec probe -- getent hosts web.dns                       # B
kubectl -n dns exec probe -- getent hosts web.dns.svc.cluster.local     # C
kubectl -n dns exec probe -- getent hosts web.dns.svc.cluster.local.    # D
kubectl -n dns exec probe -- getent hosts github.com                            # E
sleep 2 && kill %1
grep -oE '"(A|AAAA) IN [^ ]+' /tmp/dns.log | sort | uniq -c
grep -c NXDOMAIN /tmp/dns.log
```

Fill this in from the log, one row per name, before reading the next paragraph:

| | Name asked for | Queries CoreDNS saw | NXDOMAINs among them |
|---|---|---|---|
| A | `web` | | |
| B | `web.dns` | | |
| C | `web.dns.svc.cluster.local` | | |
| D | `web.dns.svc.cluster.local.` | | |
| E | `github.com` | | |

**Expect** — **C and D differ**, and that is the exercise. `web.dns.svc.cluster.local` has four dots, four is less than five, so the resolver appends the search list *first* and asks for names like `web.dns.svc.cluster.local.dns.svc.cluster.local` before it ever tries the name you typed. Only the trailing dot in D declares the name absolute. Expect E to cost eight queries — three search-list attempts and the real one, each doubled by A and AAAA — for a name that has nothing to do with this cluster.

That is the `ndots` trap in one table, and it is why the fix for a chatty cluster is a trailing dot, a `dnsConfig` with a lower `ndots`, CoreDNS's `autopath` plugin or `NodeLocal DNSCache` — **four fixes at four different layers**, which is worth naming even though none of them is installed here.

**Do — hops 4 and 5, where the answer comes from**

```sh
kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide
kubectl -n dns exec probe -- getent hosts kube-dns.kube-system
sudo nft list map ip kube-proxy service-ips | grep -E '\.10 |53'
kubectl -n dns exec probe -- getent hosts web-headless
kubectl get endpointslices -n dns -o custom-columns=NAME:.metadata.name,ADDR:.endpoints[*].addresses
```

Then answer, from the `Corefile`'s `kubernetes` directive and CoreDNS's ClusterRole:

```sh
kubectl get clusterrole system:coredns -o jsonpath='{.rules}' | tr ',' '\n' | grep -iE 'resources|verbs'
```

**Expect** — the `nameserver` address in `resolv.conf` to be a ClusterIP with **no process listening on it anywhere**, resolved by the same map lookup as any other Service; the headless name to return **pod addresses directly**, skipping the second DNAT entirely; and the ClusterRole to be `get`/`list`/`watch` on Services, EndpointSlices, Pods and Namespaces — **CoreDNS answers from its own watch cache**, so a DNS answer is as stale as an informer and never as stale as etcd, and it asks the API server nothing at query time.

**Write down** — the five hops as five lines, each naming *the component that acts* and *the artifact it reads*; the A–E query table; and [the checklist's](../../phases/07-networking.md#checklist) DNS diagnostic checklist in the talk's order, with the hop number each check tests written beside it. That mapping is the deliverable, because [exercise 26](26-7c2-it-was-dns.md) runs the checklist against a fault chosen to be invisible to four of the five checks.

**Footprint note** — one `sleep` pod and a restarted CoreDNS Deployment. The `log` plugin's cost is log volume, not memory; it comes out at teardown so that [drill 7.C1's](20-7c1-a-partition-named-by-path.md) and 7.C2's noise floors stay comparable.

**Teardown**

```sh
kubectl -n dns delete pod probe
kubectl -n kube-system replace -f /root/coredns-cm.orig.yaml
kubectl -n kube-system rollout restart deployment coredns
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | diff - /root/corefile.orig && echo restored
```

The `dns` namespace and both Services **stay** — [exercise 26](26-7c2-it-was-dns.md) breaks resolution and needs a name that worked ten minutes ago. Keep `/root/corefile.orig` too: `DNSChaos` steers pods at a *different* CoreDNS rather than editing this file, and the comparison is how you catch it. **The topology stays.**
