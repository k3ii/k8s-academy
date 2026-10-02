<a id="s07"></a>
# S7 — RWO against RWX, attempted from two nodes at once

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Access modes

> **An access mode is a request, not an enforcement.** `ReadWriteMany` on a backend that cannot do it does not fail at creation — it fails later, in whatever way that backend fails, or silently does the wrong thing. The CKA tests whether you know what each mode *means*; production tests whether you checked the backend supports it.

> **Measured on this cluster: the only provisioner is `rancher.io/local-path`, which is node-local directories under `/opt/local-path-provisioner`.** It does not implement RWX in any meaningful sense, and the PV it creates carries a `nodeAffinity` pinning it to one node. So the headline experiment here is the **failure**, and that is more instructive than a success would be.

**Do**

1. Know the four modes cold, because the abbreviations are what appear in `kubectl get pv`:
   - `ReadWriteOnce` / **RWO** — by one **node**, not one pod. Several pods on the *same* node can share it. That is the most commonly misremembered fact in this topic.
   - `ReadOnlyMany` / **ROX** — read-only, many nodes.
   - `ReadWriteMany` / **RWX** — read-write, many nodes. Needs a network filesystem.
   - `ReadWriteOncePod` / **RWOP** — exactly one *pod*, cluster-wide. The newer one, and the one that does what people think RWO does.
2. **RWO, two pods, same node.** Pin both with `nodeName`. Both mount it. Write from one, read from the other. Prove the "once" is per node.
3. **RWO, two pods, different nodes.** Pin them apart. The second pod will not run — read the event. With a `nodeAffinity`-pinned local PV the scheduler refuses it outright; with a network-attached backend you would instead see a `FailedAttachVolume`. Both are the same lesson from different layers.
4. **RWX, requested.** Create a PVC asking for `ReadWriteMany` against `local-path`. Observe what actually happens rather than predicting it — whether it binds, and if it does, whether two pods on different nodes see the same bytes. If they see *different* directories, you have found the silent-wrong-answer case, which is the real hazard and worth writing down.
5. **RWOP.** One pod, cluster-wide. Create a second pod against it anywhere and read the refusal.

**Observe**

```sh
kubectl get pv -o custom-columns=NAME:.metadata.name,MODES:.spec.accessModes,CLAIM:.spec.claimRef.name
kubectl get pods -o wide
kubectl describe pod second | sed -n '/Events/,$p'
kubectl exec first  -- sh -c 'echo A > /data/f'
kubectl exec second -- cat /data/f      # same bytes, or not?
```

**Done when** — you can state what each of the four modes permits, and you have *measured* what RWX does on this cluster rather than assumed it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. All four modes, both RWO placements. | 10 min |
| **2** | An existing RWO PVC. Get a second pod sharing it — legitimately. | 8 min |
| **3** | Cold, no notes. Name the mode for a given requirement and justify it. | 5 min |

**Teardown** — delete the namespace, then confirm no PVs survive.

**See also** — **S1** is the single-pod happy path; **S2** covers a wrong access mode as a bind failure.
