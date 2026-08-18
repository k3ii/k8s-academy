<a id="make-the-packing-visible"></a>
# Shrink the slice limit to five and watch the packing heuristic do its job

**Artifact** — the write-amplification arithmetic from KEP-752 worked for a concrete cluster size, plus a live demonstration of slice packing at a limit small enough to see: `--max-endpoints-per-slice=5`, thirteen endpoints, and a record of **how many slices were rewritten** for each of four changes.

**Rests on** — [exercise 4](04-eleven-kilobytes-of-endpointslice.md) for the object's shape. The flag set here stays set until [exercise 15](15-the-reconciler-and-its-packing-heuristic.md), which is where the heuristic is read in `reconciler.go` against the behaviour recorded here; setting it twice would be wasted work and unsetting it in between would throw away the observations.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do — part 1, the arithmetic, before the flag is touched.** From KEP-752, for a Service with **5,000 endpoints in a 1,000-node cluster**, and using ~150 bytes per endpoint as the KEP does:

1. One pod becomes not-ready. Under `v1.Endpoints`, how many bytes does the API server write to etcd, and how many bytes does it push to watchers? (There is one kube-proxy per node and each holds a watch.)
2. The same event under EndpointSlice with the default limit of 100.
3. The ratio.

Write all three numbers down. They are the entire argument for the API existing, and they are arithmetic you can do in a minute.

**Do — part 2, make the limit small.** On the control plane:

```sh
ssh zain@10.10.10.130
sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.orig
sudo sed -i '/- kube-controller-manager/a\    - --max-endpoints-per-slice=5' /etc/kubernetes/manifests/kube-controller-manager.yaml
```

The static pod restarts itself — the mechanism from [P6](../../phases/06-kubelet-node.md#m6-5). Confirm the flag is live rather than merely written:

```sh
kubectl -n kube-system get pod -l component=kube-controller-manager \
  -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep max-endpoints
```

**Do — part 3, thirteen endpoints and four changes.** Record the slice count, each slice's endpoint count, and each slice's `resourceVersion` after every step:

```sh
kubectl create ns pack
kubectl -n pack create deployment idle --image=registry.k8s.io/pause:3.10 --replicas=13
kubectl -n pack expose deployment idle --port=80
watch() { kubectl -n pack get endpointslice -o json | jq -c '.items[]|{n:.metadata.name, rv:.metadata.resourceVersion, count:(.endpoints|length)}'; }
watch
kubectl -n pack scale deployment idle --replicas=14 ; sleep 3; watch     # change A: one added
kubectl -n pack delete pod $(kubectl -n pack get pod -o name | sed -n 3p) ; sleep 5; watch   # change B: one removed, one added
kubectl -n pack scale deployment idle --replicas=6  ; sleep 5; watch     # change C: eight removed at once
kubectl -n pack scale deployment idle --replicas=13 ; sleep 5; watch     # change D: seven added at once
```

**Expect** — three slices at thirteen endpoints, and the sizes **not** to be 5/5/3 forever. Expect change A to touch exactly **one** slice: the reconciler fills an existing slice that has room rather than creating a new one, and the `resourceVersion` of the other two does not move. Expect change B to leave a slice *below* the limit rather than repacking everything to close the gap — the heuristic prefers a partly-empty slice to a rewrite storm, which is exactly the cost model in part 1 applied to itself.

Expect change C to leave you with **more slices than the endpoint count needs**, and expect change D to fill those holes before allocating anything new. If change D creates a fourth slice while a hole is open, that is a finding worth writing down with the exact counts, not a mistake.

**Write down** — the four changes with a column for *slices whose `resourceVersion` moved*, and the arithmetic from part 1. The claim this feeds — [the checklist's](../../phases/07-networking.md#checklist) *why `Endpoints` didn't scale and slicing fixed it* — should be writable from these two things and nothing else.

**Footprint note** — fourteen `pause` pods at a few MiB each, all on the worker. Under 50 MiB total and nothing that runs code. **The flag change costs nothing** — it is a control-plane restart, not an addition.

**Teardown**

```sh
kubectl delete ns pack --wait=true
```

**Leave `--max-endpoints-per-slice=5` in place** — [exercise 15](15-the-reconciler-and-its-packing-heuristic.md) needs it and restores the original manifest from `/root/kcm.yaml.orig` at its own teardown. **The topology stays.**
