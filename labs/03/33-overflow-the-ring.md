<a id="overflow-the-ring"></a>
# `too old resource version`, produced on demand

**Claim** — you can make the apiserver return `410 Gone: too old resource version` at will, and you can predict from `watch_cache.go`'s constants roughly how much write traffic it takes; and a *slow* watcher is terminated by a different mechanism, with a different symptom, in the same package.

**Rests on** — [P2's `ErrCompacted`](../../phases/02-etcd.md#m2-2), which is the same words at a lower layer. Naming the two apart is [the next exercise](34-the-same-failure-two-layers.md); this one produces the upper one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the conversion drill](32-3c2-garbage-from-the-conversion-webhook.md), now with none of module 3.4's apparatus running.

**Setup** — read before you type. In your clone on [`forge`](../../strands/lab-topologies.md#build-guest), open `staging/src/k8s.io/apiserver/pkg/storage/cacher/watch_cache.go` and find:

- the fields that make it a ring — the two indices and the slice they index into;
- the capacity bounds, as named constants, and whether capacity is fixed at construction or resized at runtime in **your** checked-out sha (this changed; do not take a blog's word for it);
- the method that decides an event is no longer available, and the exact string it produces;
- how `eventFreshDuration` participates, if it exists in your tree.

Write the capacity down as a number before you try to overflow it. The prediction is the exercise; the 410 is just confirmation.

**Do**

1. Make a namespace and record a resource version you can come back to:

   ```sh
   kubectl create ns ring
   RV=$(kubectl get cm -n ring -o jsonpath='{.metadata.resourceVersion}')
   echo $RV
   ```

2. Hammer one resource type in a different namespace, so the objects you are burning revisions with are not the ones you are watching:

   ```sh
   kubectl create ns churn
   for i in $(seq 1 3000); do
     kubectl create cm c$i -n churn --from-literal=k=v >/dev/null
     kubectl delete cm c$i -n churn >/dev/null
   done
   ```

   Predict, before running it, whether churn in `churn` can evict events for `ring`. The answer is in what the cacher is keyed by — one cacher per **resource**, not per namespace — and confirming it is half the value of this step.

3. Ask for the old resource version:

   ```sh
   kubectl get --raw "/api/v1/namespaces/ring/configmaps?watch=true&resourceVersion=$RV"
   ```

4. Now the other mechanism. Start a watch and *do not read from it*:

   ```sh
   kubectl get --raw "/api/v1/configmaps?watch=true" | (sleep 300; cat)
   ```

   With that stalled, run step 2's loop again and watch what happens to the stalled watch.

5. Find both behaviours in the code. Step 3's is in `watch_cache.go`. Step 4's is in `cache_watcher.go` — look for the non-blocking send and what it does when the channel is full.

**Observe**

```sh
kubectl get --raw /metrics | grep -E 'watch_cache_(capacity|events)'
kubectl get --raw /metrics | grep -E 'apiserver_terminated_watchers_total'
ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | grep -i "too old\|forget" | tail -20'
```

**Expect** — step 3 returns a `Status` object, `code: 410`, `reason: Expired`, message `too old resource version: <RV> (<current>)`. The two numbers in that message are the whole diagnosis: how far behind you asked from, and how far back the cache can still serve.

The `watch_cache_capacity` metric tells you whether your prediction was right, and if the capacity moved while you were hammering, you have found the dynamic-resizing behaviour and should go back and re-read the constructor.

Step 4 does not produce a 410. The watcher is **forgotten** — the connection closes with no error object at all, and `apiserver_terminated_watchers_total` increments. From a client's perspective that is indistinguishable from a network drop, which is why every real informer re-lists rather than trusting a closed stream. Note that this is a defence of the *apiserver*, not of the client: an unread watch cannot be allowed to pin memory.

**Write down** — the predicted capacity and the observed one, the `file:line` for the eviction string, the `file:line` for the non-blocking send, and one sentence contrasting the two failure signatures — one names itself, one is silent.

**Teardown** — `kubectl delete ns ring churn`. **The topology stays** — [the two-layer comparison](34-the-same-failure-two-layers.md) is next and reuses this cluster.
