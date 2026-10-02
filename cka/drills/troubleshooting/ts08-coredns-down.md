<a id="ts08"></a>
# TS8 — The cluster "is broken": find your way to CoreDNS from the symptom

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot cluster components

> **Nobody reports a DNS fault as a DNS fault.** It arrives as "nothing can talk to anything", because every workload in the cluster addresses its dependencies by name. The drill is the route *in* — from a cluster-wide symptom to a single Deployment in `kube-system` — and the rule that gets you there fast: **if it works by ClusterIP and fails by name, it is DNS, and it is one of four things.**

**Break it** — *pass 1 only.* Four causes, which need four different fixes:

1. **The pods are down.** Scaled to zero, evicted, or unschedulable.
2. **The Service has no backends.** The `kube-dns` Service survives, pods do not match it, and clients get a ClusterIP that answers nothing — the [TS15](ts15-service-with-no-endpoints.md) shape, one namespace over.
3. **The Corefile is wrong.** Syntactically bad, which `reload` refuses and survives, or syntactically fine and semantically wrong, which it applies immediately and which is much worse.
4. **A forwarding loop.** Point the forwarder at a resolver that points back, and the `loop` plugin detects it and CoreDNS deliberately **exits**. This is why [the baseline](../../baseline.md#cluster) records `resolvConf: /run/systemd/resolve/resolv.conf` rather than `/etc/resolv.conf`: on a systemd-resolved host the latter is a `127.0.0.53` stub, and pointing CoreDNS at it is precisely the loop. A CoreDNS that crash-loops from a clean start is almost always this.

**Work it**

```sh
kubectl run q --rm -it --image=busybox:1.37.0 --restart=Never -- nslookup kubernetes.default
kubectl -n kube-system get deploy,pod -l k8s-app=kube-dns
kubectl -n kube-system get svc kube-dns -o wide
kubectl -n kube-system get endpointslices -l kubernetes.io/service-name=kube-dns
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=50 --previous
kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'
```

Note `--previous` on the log read. If CoreDNS is crash-looping, the current container has nothing to say and the reason is in the one that died.

**Done when** — you reach the right one of the four without having read the Corefile first, because three of the four are visible before you get there and the Corefile is the most expensive thing to read.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Induce all four and record each signature. | 10 min |
| **2** | Messy. Another workload is also failing, for an unrelated reason. | 8 min |
| **3** | **Injected.** One of the four, unlabelled. Cold, clock visible. | **5 min** |

**Teardown** — `cka-inject.sh revert`, restore the Corefile, and confirm resolution works from a fresh pod before stopping. **Confirm from a new pod, not an old one**: a pod that already has an open connection will keep working and tell you nothing.

**See also** — [N9](../networking/n09-corefile-forward.md), the Corefile edited on purpose, where the `reload` behaviour this drill depends on is built rather than diagnosed.
