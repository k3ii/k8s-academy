<a id="the-410-under-your-own-informer"></a>
# The third layer of a failure you have met twice

**Claim** — you can make your own reflector receive `410 Gone`, catch the line that handles it, and show what it does next — completing a chain whose first two layers you already produced: [etcd's compaction](../../phases/02-etcd.md#m2-3) and [the apiserver's watch cache](../../phases/03-api-machinery.md#m3-5). Neither of those mechanisms is restated here. **This exercise adds only the client's end**, which is the one that has to survive.

**Rests on** — the [`watchable_store.go` reading question](../../phases/02-etcd.md#m2-3) for what compaction does to a slow watcher, and [module 3.5](../../phases/03-api-machinery.md#m3-5) for the ring and the prediction of its capacity. Do not re-derive either; produce the event and read the client.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with [the probe](09-force-a-relist.md) running on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Find the handling before you cause it, and answer one question from the source that the log will not tell you:

   ```sh
   cd ~/src/kubernetes && git grep -n 'ErrResourceExpired\|IsResourceExpired\|isExpiredError\|too old resource version' \
     -- staging/src/k8s.io/client-go/tools/cache/reflector.go
   ```

   **The question:** after the expiry, which `resourceVersion` does the next LIST ask for — the last one the reflector held, `0`, or none at all? Read the function that chooses it, and say in one sentence what that choice costs and what it buys. There is a real trade there between a stale answer served cheaply and a fresh one served expensively, and the reflector picks a side.

2. Freeze the probe so its watch falls behind:

   ```sh
   kill -STOP <probe-pid>
   ```

3. Churn the resource it is watching, hard enough to push its position off the end of the ring. Start with 500 and go up if the thaw produces no expiry:

   ```sh
   for i in $(seq 1 500); do
     kubectl -n academy-lab create configmap churn-$i --from-literal=n=$i >/dev/null
   done
   ```

   Five hundred creates is deliberate: creates and deletes both count as events on the ring, but creates leave something behind you can count afterwards, so a run that failed to overflow is distinguishable from a run that overflowed and recovered.

4. Thaw it and read the log:

   ```sh
   kill -CONT <probe-pid>
   ```

**Observe** — the reflector's own log lines around the thaw, and the `POP` burst that follows.

**Expect** — a warning naming the resource type and the expiry, then a re-list, then `Replaced` deltas for everything that still exists. The controller does not crash, does not miss objects, and cannot say which specific changes it missed — **it re-derives the world instead of replaying the events**, which is the same property [exercise 5](05-stomp-it-back.md) showed at the reconcile layer, here at the cache layer.

If 500 objects produce no expiry, the ring grew; that growth is [module 3.5's](../../phases/03-api-machinery.md#m3-5) subject and the number to raise is the churn, not the freeze time. Confirm the failure is the one you wanted by checking that the message names an expired resource version and not a closed connection — [the two look alike in a log and are not the same failure](09-force-a-relist.md).

**Write down** — [the checklist's](../../phases/04-controllers.md#checklist) 4.2 artifact: the `410`-to-relist path with the `reflector.go` `file:line`, tied back to the two layers below it by name. This is [objective 3](../../phases/04-controllers.md#objectives) and it is [gate condition 3](../../phases/04-controllers.md#gate); after this it is assumed and never taught again.

**Footprint note** — 500 ConfigMaps is a few MB in etcd on a cluster with nothing else in it, and they are deleted in the teardown. This is the phase's only deliberate churn.

**Teardown**

```sh
kubectl -n academy-lab delete configmap --all
```

Stop the probe. **The topology stays** — [exercise 11](11-what-hassynced-actually-promises.md) restarts it against a clean namespace, which is precisely the state it needs.
