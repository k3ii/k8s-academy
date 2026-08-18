<a id="eleven-kilobytes-of-endpointslice"></a>
# Predict `Ready`, `Serving` and `Terminating` for five pod states, from the comments alone

**Claim** — you can fill in a fifteen-cell table of `EndpointConditions` for five pod states **before touching the cluster**, using only the field comments in `discovery/v1/types.go`, and the cluster will agree with every cell. The one cell that is easiest to get wrong is `ready` on a terminating pod that is still serving traffic perfectly well, and the comment on `Ready` says so in as many words.

**Rests on** — [exercise 2](02-the-kernel-both-sides-must-share.md) for the cluster. This is [Area 5's entry point](../../strands/source-reading.md#area-5-networking) and it is the data structure [P6's capstone trace](../../phases/06-kubelet-node.md#capstone) passed through without being read; from here on, every exercise in [module 7.3](../../phases/07-networking.md#m7-3) consumes it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — on `forge`, in the phase's clone:

```sh
ssh zain@10.10.10.125
cd ~/src/kubernetes && git log -1 --format='%H %s'
$EDITOR staging/src/k8s.io/api/discovery/v1/types.go
```

11 KB, read linearly, once. The four things to come out with, each of which is a comment and not an inference: what `Ready` is defined to be **for a terminating endpoint**; what `Serving` adds that `Ready` does not have; what `Terminating` is derived from; and why `addressType` is on the *slice* rather than on each `Endpoint`.

**Do — part 1, the prediction.** Write the table out in full before the next command runs:

| Pod state | `ready` | `serving` | `terminating` | in the slice at all? |
|---|---|---|---|---|
| just scheduled, readiness probe not yet passing | | | | |
| running, readiness passing | | | | |
| `kubectl delete` issued, still passing readiness, inside its grace period | | | | |
| in its grace period and now failing readiness | | | | |
| container gone, pod object deleted | | | | |

**Do — part 2, the cluster.** A grace period long enough to watch, and a readiness probe you can turn off from outside the pod:

```sh
kubectl create ns esl
kubectl -n esl apply -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata: {name: web, namespace: esl}
spec:
  replicas: 2
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web}}
    spec:
      terminationGracePeriodSeconds: 120
      containers:
      - name: web
        image: registry.k8s.io/e2e-test-images/agnhost:2.47
        args: ["netexec", "--http-port=8080"]
        readinessProbe:
          httpGet: {path: /readyz, port: 8080}
          periodSeconds: 2
        lifecycle:
          preStop: {exec: {command: ["sleep", "90"]}}
YAML
kubectl -n esl expose deployment web --port=8080
```

Watch the slice while you drive the pod through the states, in one terminal:

```sh
kubectl -n esl get endpointslice -w -o json | jq -c '{name:.metadata.name, at:.metadata.resourceVersion, e:[.endpoints[]|{ip:.addresses[0], c:.conditions}]}'
```

and in another:

```sh
kubectl -n esl delete pod <one pod> &                                 # state 3 begins
sleep 5
kubectl -n esl exec <the same pod> -- curl -s -XPOST 'localhost:8080/readyz?ready=false'   # state 4
```

**Expect** — `terminating: true` and `serving: true` together, with `ready: false`, for the whole of state 3. That combination is the point of the type: **a load balancer that wants to drain connections needs to know an endpoint is still answering while also knowing not to send it new work**, and one boolean cannot say both. Expect `serving` to flip to `false` within two probe periods of the `POST`, with `terminating` unchanged.

Expect state 1 to put the endpoint **in the slice** with `ready: false` — not to omit it. An endpoint's absence and an endpoint's un-readiness are different facts and the API keeps them different.

**Verify from outside** — the same conditions, seen by the consumer rather than by `kubectl`:

```sh
kubectl -n esl get endpoints web -o wide       # the mirrored, older API — one column poorer
```

`Endpoints` splits into `subsets[].addresses` and `subsets[].notReadyAddresses`, which can encode two of the three conditions and cannot encode the third at all. That gap is one of the reasons for [exercise 6](06-the-api-that-is-being-deleted.md).

**Write down** — the prediction table with the observed column beside it, marking each cell right or wrong, and the `file:line` of the `Ready` comment that decides row 3. The cells you got wrong are the ones worth a sentence each.

**Footprint note** — two `agnhost` pods, about 30 MiB. No change to the phase's 6.5GB.

**Teardown**

```sh
kubectl delete ns esl --wait=true
```

**The topology stays** — [exercise 5](05-make-the-packing-visible.md) changes a control-plane flag on it.
