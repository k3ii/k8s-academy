<a id="n09"></a>
# N9 — Edit the Corefile, add a forward, and make CoreDNS pick it up

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / CoreDNS

> **CoreDNS config is a ConfigMap, and editing it is not deploying it.** Two things can go wrong that look identical from outside: the change has not been picked up yet, and the change was picked up and rejected. Knowing which is the drill.

**Do**

1. Read the live Corefile before touching it. On this cluster it is a single `.:53` server block carrying `errors`, `health`, `ready`, `kubernetes cluster.local`, `prometheus`, `forward . /etc/resolv.conf`, `cache 30`, `loop`, `reload` and `loadbalance`. Know what each of the last four does; three of them are the subject of this drill.
2. Add a **stub zone** — a second server block that forwards one domain to a specific resolver, leaving everything else on the catch-all `forward . /etc/resolv.conf`. Resolve a name in that zone and confirm it took the new path.
3. **Do not restart anything.** The `reload` plugin is in the Corefile, so CoreDNS polls its own config and applies changes on its own, within about half a minute. Time it. That interval is the gap in which a correct change looks like a broken one.
4. Now break it deliberately — a missing brace — and watch what happens. **CoreDNS keeps serving the old config** and logs the parse failure rather than crashing. This is the single most useful thing to know about the `reload` plugin: a bad Corefile is survivable, and a cluster that is still resolving names does not prove your edit landed.
5. Fix it, then force the issue once with a rollout restart so you know the manual path too.

**Observe**

```sh
kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=30 | grep -i reload
kubectl -n kube-system rollout restart deploy/coredns
kubectl run q --rm -it --image=busybox:1.37.0 --restart=Never -- nslookup <name-in-stub-zone>
```

**Done when** — the stub zone resolves, the catch-all still resolves, and you can say from the logs alone whether a given edit was applied or rejected.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Add the stub zone, break it, repair it. | 10 min |
| **2** | Without a backup. Edit the live ConfigMap in place, with the discipline of saving the original first. | 8 min |
| **3** | Cold, no notes, clock visible. Stub zone from memory, including the block syntax. | 5 min |

**Teardown** — restore the original Corefile and confirm it reloaded. **Verify before you walk away**: a damaged Corefile left behind breaks every later drill in a way that points nowhere near DNS.

**See also** — [TS8](../troubleshooting/ts08-coredns-down.md) is this object as a fault: the Corefile is already wrong, you did not write it, and the symptom arrives as "the cluster is broken" rather than as "DNS is broken".
