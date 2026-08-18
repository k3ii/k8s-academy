<a id="deltas-are-per-key"></a>
# One Pop, one key, several deltas

**Artifact** — a ~70-line probe on [`forge`](../../strands/lab-topologies.md#build-guest) wiring a `Reflector` to a `DeltaFIFO` backed by an `Indexer`, with a deliberately slow `Pop` loop — and a log excerpt in which a single `Pop` returns **four deltas for one key** because four writes landed while the loop was asleep.

**Rests on** — [module 4.2's](../../phases/04-controllers.md#m4-2) `delta_fifo.go` reading question. This is the crux of that file made visible: a plain FIFO would have handed you four items, and this hands you one item containing four.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The probe runs on `forge` against the cluster's API, using the kubeconfig from [exercise 3](03-sample-controller-against-a-real-cluster.md).

**Setup**

```sh
mkdir -p ~/probes/informer && cd ~/probes/informer
go mod init probe && go get k8s.io/client-go@latest
kubectl create namespace academy-lab
```

**Build the probe** — the three pieces from your [drawing](01-draw-it-before-you-read-it.md), wired by hand rather than by a factory, because the factory is what hides them:

```go
idx  := cache.NewIndexer(cache.MetaNamespaceKeyFunc, cache.Indexers{})
fifo := cache.NewDeltaFIFOWithOptions(cache.DeltaFIFOOptions{
    KeyFunction:           cache.MetaNamespaceKeyFunc,
    KnownObjects:          idx,               // exercise 9 needs this; note why below
    EmitDeltaTypeReplaced: true,
})
lw := cache.NewListWatchFromClient(cs.CoreV1().RESTClient(), "configmaps", "academy-lab", fields.Everything())
go cache.NewReflector(lw, &corev1.ConfigMap{}, fifo, 0).Run(stop)

for {
    _, _ = fifo.Pop(func(obj interface{}, isInInitialList bool) error {
        ds := obj.(cache.Deltas)
        fmt.Printf("POP  n=%d  key=%s  types=%v\n", len(ds), keyOf(ds.Newest()), typesOf(ds))
        for _, d := range ds { applyToIndexer(idx, d) }   // Added/Updated -> Add, Deleted -> Delete
        time.Sleep(4 * time.Second)                        // the slow consumer
        return nil
    })
}
```

`applyToIndexer` is four lines and it is not optional: the `Indexer` is the "current objects" box in your drawing, and nothing else writes to it. A `DeltaFIFO` whose `KnownObjects` never learns about anything is a `DeltaFIFO` that cannot tell you what has disappeared — which is [exercise 9](09-force-a-relist.md).

**Do**

1. Start the probe and let the initial list drain.

2. In another session, write to one ConfigMap four times in under a second, then to a second ConfigMap once:

   ```sh
   kubectl -n academy-lab create configmap busy --from-literal=n=0
   for i in 1 2 3 4; do kubectl -n academy-lab patch configmap busy --type=merge -p "{\"data\":{\"n\":\"$i\"}}"; done
   kubectl -n academy-lab create configmap quiet --from-literal=n=0
   ```

**Observe** — the `POP` lines: their count, the `n=` on each, and the key each one carries.

**Expect** — one `POP` with `n=4` (or 3, or 5, depending on where the sleep fell) for `busy`, and a separate `POP` with `n=1` for `quiet`. **Deltas coalesce per key and never across keys**, which is the property that makes the structure a `DeltaFIFO` rather than a queue of events: the ordering guarantee is per object, and work for two objects is never merged, never reordered relative to itself, and never made to wait for each other beyond the single consumer.

Two consequences to write down while they are in front of you:

- Your handler is called with a *list*, and the only element most controllers look at is `Newest()`. Everything before it is history you are permitted to ignore — which is the same permission [exercise 2](02-the-line-that-enqueues-a-key.md)'s key-not-object design gives you one layer up. The two are the same idea implemented twice.
- If the consumer keeps up, `n` is 1 every time and this structure looks pointless. It earns its keep exactly when the consumer is slow, which in a real controller means *when the cluster is busiest*.

**Write down** — the `POP` excerpt, and one sentence on what a plain FIFO of events would have delivered instead, with the cost that would have carried under load.

**Footprint note** — one small Go process on `forge` and two ConfigMaps. Nothing measurable.

**Teardown** — stop the probe; **keep `~/probes/informer/` and the two ConfigMaps** — [the next exercise](09-force-a-relist.md) restarts this same probe against them. **The topology stays.**
