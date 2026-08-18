<a id="the-same-failure-two-layers"></a>
# Two `too old` errors, one wording, different causes

**Claim** — `410 too old resource version` from the apiserver and etcd's `ErrCompacted` are produced by different components for different reasons, and a client that sees the 410 cannot tell from the message which one happened; you can distinguish them from the server side, and you can produce each without the other.

**Rests on** — [the ring overflow](33-overflow-the-ring.md), which produced the cache-layer one, and [P2's compaction work](../../phases/02-etcd.md#m2-2), which produced the etcd-layer one on an etcd with no Kubernetes near it. This is the exercise where the phase's write-down for [module 3.5](../../phases/03-api-machinery.md#m3-5) gets its second half.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Produce the cache-layer error **without any compaction**: repeat [the previous exercise](33-overflow-the-ring.md)'s steps 1–3, and immediately record etcd's current compaction state on `.130`:

   ```sh
   ssh zain@10.10.10.130 "sudo ETCDCTL_API=3 etcdctl \
     --cacert /etc/kubernetes/pki/etcd/ca.crt --cert /etc/kubernetes/pki/etcd/server.crt \
     --key /etc/kubernetes/pki/etcd/server.key endpoint status -w json" | jq '.[0].Status.header.revision'
   ```

2. Produce the etcd-layer error, deliberately, at a revision the watch cache would still have served. Compact by hand well past a recorded revision, then ask for it with a **quorum** read that must go to etcd rather than to the cache:

   ```sh
   kubectl get --raw "/api/v1/namespaces/ring/configmaps?resourceVersion=$RV&resourceVersionMatch=Exact"
   ```

   Work out from [module 3.5's reading](../../phases/03-api-machinery.md#m3-5) which request parameters force the storage layer and which are served from cache, and write down how you knew before you ran it.

3. Read `storage/etcd3/watcher.go` for where etcd's compaction error is caught and what it is turned into on the way out. Then read `storage/cacher/cacher.go` for where the cache's own version is raised. Two call sites, one wire format.

4. Compare the two responses byte for byte:

   ```sh
   diff <(jq -S . /tmp/cache-410.json) <(jq -S . /tmp/etcd-410.json)
   ```

**Observe** — the apiserver log at `-v=4` for each, and:

```sh
kubectl get --raw /metrics | grep -E 'apiserver_watch_cache_events_(dispatched|received)_total'
ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | grep -i compact | tail'
```

**Expect** — the two `Status` bodies are close enough that a client library cannot branch on them, and the numbers in the message are the only thing that differs in kind: the cache reports the oldest revision *it* still holds, etcd reports the compaction revision. Neither says which component answered.

The server side does distinguish them, in the logs and in which metrics move. That asymmetry is the point: **the diagnosis lives on the server, and the client is expected to do the same thing either way** — re-list and resume. Every informer in Kubernetes is written to that contract, which is why [P4](../../phases/04-controllers.md) can treat both as "start over" without establishing which happened.

**Write down** — the sentence [the module's write-down](../../phases/03-api-machinery.md#m3-5) asks for: the ring-buffer origin with its `watch_cache.go` citation, tied to `ErrCompacted`, naming which component raises each and why the wire format cannot tell them apart. Add the pair to [the running list of look-alike failures](04-mis-sign-a-client-cert.md) — this is the sixth entry and the first where both sides are *correct* behaviour.

**Teardown** — `kubectl delete ns ring churn` if they survived. Note that the compaction in step 2 is not reversible and is now part of this cluster's history; nothing later in the phase depends on old revisions. **The topology stays.**
