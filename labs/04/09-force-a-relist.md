<a id="force-a-relist"></a>
# The delete you never saw, delivered anyway

**Claim** — when a watch breaks and the reflector re-lists, `Replace` does something a plain re-send of the list cannot: it compares the list against what the store already holds and **synthesises a `Deleted` delta for every object that is no longer there**, carrying a `DeletedFinalStateUnknown` instead of an object. You can construct the situation, predict the delta, and read the tombstone.

**Rests on** — [the probe](08-deltas-are-per-key.md) and its `KnownObjects` indexer, which exists for exactly this. The interruption is [P3's 3.C4 move](../../phases/03-api-machinery.md#m3-5), reused here from the client's side rather than the server's.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The apiserver you stop is the static pod on `.130`.

**Setup** — the escape hatch first, as always: the apiserver is a static pod, so the kubelet restarts it the moment its manifest is back. Move the file, never delete it.

```sh
ssh zain@10.10.10.130 'sudo mkdir -p /root/parked'
```

Start the probe from [exercise 8](08-deltas-are-per-key.md) and let the initial list land, so `busy` and `quiet` are both in its indexer. Note its PID on `forge`.

**Do**

1. Freeze the probe, so it cannot reconnect while you work:

   ```sh
   kill -STOP <probe-pid>
   ```

2. Stop the apiserver, wait for the connection to be well and truly dead, and bring it back:

   ```sh
   ssh zain@10.10.10.130 'sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/parked/'
   sleep 20
   ssh zain@10.10.10.130 'sudo mv /root/parked/kube-apiserver.yaml /etc/kubernetes/manifests/'
   until kubectl get --raw /readyz; do sleep 2; done
   ```

3. Delete one of the two ConfigMaps **while the probe is still frozen**. This is the whole construction: a change the probe's watch can never deliver, because there is no watch.

   ```sh
   kubectl -n academy-lab delete configmap quiet
   ```

4. Thaw it:

   ```sh
   kill -CONT <probe-pid>
   ```

5. Run the whole sequence a second time with `EmitDeltaTypeReplaced: false`, which is the compatibility default.

**Observe** — the `POP` lines after the thaw: their delta types, and what the `Deleted` one contains.

**Expect** — the reflector's watch returns an error, `ListAndWatch` re-lists, and `Replace` produces one delta per object still present plus **one `Deleted` for `quiet` that your probe never watched happen**. Its object is not a `ConfigMap`: it is a `cache.DeletedFinalStateUnknown` holding the key and the last version the store had. A handler that type-asserts straight to `*corev1.ConfigMap` panics here, and this is the single most common place a hand-written controller crashes in production — it runs for weeks and then falls over during an apiserver restart.

With `EmitDeltaTypeReplaced: false` the same deltas arrive typed `Sync` instead of `Replaced`. **The flag changes nothing about the behaviour and everything about your ability to tell a re-list apart from a periodic resync**, which are two very different reasons for your handler to be called and are indistinguishable by default for backwards compatibility.

**Write down** — the two `POP` excerpts side by side, the tombstone's contents, and the three-line type switch a handler needs to survive it.

**Footprint note** — nothing new. The apiserver outage is ~20 seconds on a two-node cluster with nothing depending on it.

**Teardown** — confirm the manifest is back and `kubectl get nodes` answers. Leave the probe and `busy` in place; [the next exercise](10-the-410-under-your-own-informer.md) uses both. **The topology stays.**
