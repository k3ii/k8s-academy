<a id="the-reconciler-and-its-packing-heuristic"></a>
# The first debt repaid: `reconciler.go`, cited, against the packing you already watched

**Artifact** — the pod→endpoint mapping in `staging/src/k8s.io/endpointslice/reconciler.go` cited as `file:line`, **verified live** on the commit your clone is at, and matched against the four changes recorded in [exercise 5](05-make-the-packing-visible.md). This is the first of [P6's three owed citations](../../phases/06-kubelet-node.md#capstone).

**Rests on** — [exercise 5](05-make-the-packing-visible.md), whose `--max-endpoints-per-slice=5` is still in place and whose observations are the evidence this reading is checked against; and [exercise 14](14-the-model-files-before-the-machine.md) for the consumer's side of the same data.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Reading on `forge`, one confirmation run on the cluster.

**Read** — 28 KB, and the most readable substantial piece of networking code in the tree, which is why it is the one place in this phase where reading a whole file is the right call. Four things to come out with, each as a `file:line`:

| Find | The question it settles |
|---|---|
| where a `*v1.Pod` becomes a `discovery.Endpoint` | which pod fields become which endpoint fields, and where `Ready`/`Serving`/`Terminating` are computed rather than copied |
| the function that decides **which existing slice** a new endpoint goes into | your change A: one slice touched, two untouched |
| whatever the code calls the "leave it partly full" decision | your change B: a slice left below the limit rather than repacked |
| where the limit itself is read | that the flag you set is read here and not in the controller |

**Verify the citations rather than trusting them**, [to P2's standard](../../strands/source-archaeology.md#drills) — these are staging-repo paths that move between releases, and the phase's own capstone says a copied line number rots fast:

```sh
ssh zain@10.10.10.125
cd ~/src/kubernetes && git log -1 --format='%H %ci'
kubectl version -o json | jq -r '.serverVersion.gitVersion'
git describe --tags --abbrev=0
```

If the clone and the cluster are not the same minor version, say so in the write-up beside every line number. That is not pedantry: `reconciler.go` moved into staging under KEP-3685 precisely so that other projects could vendor it, so it moves.

**Do — score the four changes against the code.** For each of A through D from [exercise 5](05-make-the-packing-visible.md), name the function that produced the outcome you recorded, and mark the row *explained* or *unexplained*:

```sh
kubectl create ns pack2
kubectl -n pack2 create deployment idle --image=registry.k8s.io/pause:3.10 --replicas=13
kubectl -n pack2 expose deployment idle --port=80
kubectl -n pack2 get endpointslice -o json | jq -c '.items[]|{n:.metadata.name,count:(.endpoints|length)}'
kubectl -n kube-system logs -l component=kube-controller-manager --tail=40 | grep -i endpointslice
```

Then the one observation the reading predicts and [exercise 5](05-make-the-packing-visible.md) did not produce: **delete a slice by hand** and watch the reconciler notice that its own output is missing.

```sh
kubectl -n pack2 delete endpointslice <one of the three>
sleep 3; kubectl -n pack2 get endpointslice -o json | jq -c '.items[]|{n:.metadata.name,count:(.endpoints|length)}'
```

**Expect** — a *new* slice with a new name, not the old one recreated, and the surviving slices untouched. Expect the total endpoint count to return to thirteen. That is level-triggered reconciliation on an object whose name is generated, and it is worth pausing on: the reconciler does not remember what it created, it compares what exists to what should exist — the same shape as [P4's controllers](../../phases/04-controllers.md) and the same shape as your own `CHECK` in [exercise 8](08-add-and-del-that-cnitool-accepts.md).

Expect one of the four rows to be harder to explain than the others. Whichever it is, the honest write-up says *unexplained* with the counts attached rather than reaching for a plausible function name — that distinction is what makes the citation checkable.

**Write down** — the four `file:line` citations with the commit they were read at, the four changes marked explained or not, and the sentence P6 asked for: *the EndpointSlice reconciler removes the endpoint* — now with a line number under it. One debt down, two to go ([exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) and [exercise 18](18-the-tracker-between-two-syncs.md)).

**Footprint note** — thirteen `pause` pods again, under 50 MiB, on the worker. Note that they are getting their addresses from **your** CNI plugin now, which is a quiet piece of evidence for [exercise 10](10-the-plugin-the-kubelet-calls.md) that costs nothing to collect.

**Teardown** — clean up, and **put the control-plane flag back**, because everything from [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) onward should see a default cluster:

```sh
kubectl delete ns pack2 --wait=true
ssh zain@10.10.10.130 'sudo cp /root/kcm.yaml.orig /etc/kubernetes/manifests/kube-controller-manager.yaml'
sleep 20
kubectl -n kube-system get pod -l component=kube-controller-manager \
  -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -c max-endpoints    # must be 0
```

**The topology stays.**
