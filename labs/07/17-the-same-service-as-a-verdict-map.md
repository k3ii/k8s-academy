<a id="the-same-service-as-a-verdict-map"></a>
# The same Service, same endpoints, one map lookup: switch the backend and diff the two dumps

**Artifact** — the same ClusterIP traced a second time in nftables, the two dumps' sizes measured against each other, and a written statement of **the structural reason nftables scales where a chain per service does not** — which is [a checklist claim](../../phases/07-networking.md#checklist) and has to be a mechanism, not an adjective. Plus `syncProxyRules` in `pkg/proxy/nftables/proxier.go` cited, which completes [P6's third debt](../../phases/06-kubelet-node.md#capstone) across both backends.

**Rests on** — [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) entirely: same namespace, same Service, same three pods, and the dump saved at `/root/nat-iptables-mode.rules`. Changing the workload as well as the backend would make the comparison worthless.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The switch is cluster-wide — kube-proxy is a DaemonSet — so both nodes change, which is itself worth noticing: **there is no per-node backend.**

**Read** — `syncProxyRules` in `pkg/proxy/nftables/proxier.go`, **only**, with [exercise 16's](16-a-clusterip-followed-to-its-kube-sep.md) notes open beside it. Three questions:

| Find | Because |
|---|---|
| what is written **once per sync** versus **once per service port** | in the iptables backend, almost everything was per service port |
| the map (or maps) a ClusterIP is looked up in | this is the structural answer |
| how the backend applies an update — the whole ruleset, or a delta | this is the *other* structural answer, and it is the one people miss |

**Do — switch the backend.** One field, and a rollout:

```sh
kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' > /tmp/kp.conf
sed -i 's/^\( *mode:\).*/\1 "nftables"/' /tmp/kp.conf
kubectl -n kube-system create cm kube-proxy --from-file=config.conf=/tmp/kp.conf \
  --from-file=kubeconfig.conf=<(kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.kubeconfig\.conf}') \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n kube-system rollout restart ds kube-proxy
kubectl -n kube-system rollout status ds kube-proxy
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=20 | grep -iE 'nftables|cleanup|mode'
```

**Observe — the cleanup first, because it is the first observable and it is easy to miss.** kube-proxy removes the other backend's rules on startup; the `KUBE-` chains you spent [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) reading should be gone:

```sh
ssh zain@10.10.10.131
sudo -i
iptables-save -t nat | grep -c '^:KUBE-'
nft list tables
nft list table ip kube-proxy > /tmp/kp.nft; wc -l /tmp/kp.nft /root/nat-iptables-mode.rules
```

**Then follow the same ClusterIP again**, and it is two greps rather than four:

```sh
CIP=<the same ClusterIP>
grep -n "$CIP" /tmp/kp.nft
grep -n -A8 'chain service-' /tmp/kp.nft | grep -B2 -A6 'numgen\|dnat'
```

**Expect** — the ClusterIP to appear as **an element of a map**, on one line, pointing at a per-service chain; and the per-service chain to select an endpoint with a single `numgen random mod <n> vmap` rather than a ladder of probabilistic jumps. Expect the DNAT itself to look almost identical to the iptables one, because it is the same operation — **what changed is the dispatch, not the translation.**

Expect the two structural answers to be separable, and write both, because the checklist claim is only correct if it names them both:

1. **Lookup.** A ClusterIP is a key in a map, so the cost of deciding *which* service a packet is for does not grow with the number of services. In the iptables backend, `KUBE-SERVICES` is a list of `-d <clusterIP>` rules traversed in order, so it does.
2. **Update.** nftables supports adding and removing a map element. `iptables-restore` takes a table at a time, so a one-endpoint change means re-sending every rule for every service on the node — which is why the iptables backend's sync time is a function of total cluster size and not of the size of the change.

The second is the more expensive one in practice and it is the one the line counts show: compare `wc -l` on the two dumps, then compare what each backend would have to *write* to add one endpoint.

**Verify from outside** — the Service must still balance across three pods, or the comparison is between a working ruleset and a broken one:

```sh
kubectl -n svc run c --rm -it --restart=Never --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- \
  sh -c 'for i in $(seq 1 30); do curl -s http://web.svc/hostname; echo; done' | sort | uniq -c
```

**Expect the distribution to be flatter than the iptables run's.** `numgen random mod n` is one uniform draw; the probabilistic ladder is a sequence of independent draws that is uniform only if every probability is exactly right. Both are correct; only one is obviously correct by construction.

**Write down** — the ClusterIP's map element and per-service chain quoted verbatim, the two line counts, the two structural reasons as separate numbered claims, and the `nftables/proxier.go` `file:line` for its DNAT site with the commit. Then close P6's ledger: all three hops of [trace #2's far half](../../strands/source-reading.md#trace-pod-dies) now have citations, in two backends for the last one.

Answer in one line from [KEP-5343](../../strands/source-reading.md#area-5-networking): what is the stated blocker on making this the default, given that it is GA?

**Footprint note** — no new workload. A DaemonSet restart on two nodes.

**Teardown** — **stay on nftables** for the rest of the phase. It is the backend [KEP-5343](../../strands/source-reading.md#area-5-networking) is making the default, [exercise 19](19-7c3-delete-one-endpoint-rule.md)'s drill is more interesting against a map than against a chain, and switching back and forth costs a rollout each time for nothing. Keep both dumps on `.131`:

```sh
cp /tmp/kp.nft /root/kp-nftables-mode.nft; ls -l /root/*.rules /root/*.nft
```

**The topology stays.**
