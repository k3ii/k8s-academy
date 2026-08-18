<a id="7c1-a-partition-named-by-path"></a>
# 7.C1 — the same partition through two different Linux primitives, and which of the four paths broke

**Artifact** — drill [7.C1](../../phases/07-networking.md#chaos): a cross-node pod partition produced twice, once with `netem` and once with `iptables`, with **`tc -s qdisc show` evidence for the first and a rule dump for the second**, and each run labelled with which of [exercise 1's](01-the-four-paths-and-what-p0-wired.md) four communication paths it severed and which three it left alone.

**Rests on** — [exercise 1](01-the-four-paths-and-what-p0-wired.md) for the four paths, and [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md)'s Service for something to partition. The reason both mechanisms are run is [the chaos strand's design claim](../../strands/chaos.md#mechanisms) — one Linux primitive per fault — which is checkable rather than decorative, and this is the drill where checking it costs two commands.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Chaos Mesh arrives on this cluster here.

**Setup** — install Chaos Mesh from [the strand's minimised block](../../strands/chaos.md#install), unchanged. The capability-to-mechanism reading was done once, as [an exercise in P6](../../phases/06-kubelet-node.md#chaos); from there on it is one line of setup, and this is one of those lines.

```sh
kubectl -n chaos-mesh get pods
```

Then put an endpoint on each node, so that a partition between nodes is visible as a *partial* failure rather than as an outage:

```sh
kubectl -n svc patch deployment web --type=merge -p '{"spec":{"replicas":2,"template":{"spec":{"topologySpreadConstraints":[{"maxSkew":1,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule","labelSelector":{"matchLabels":{"app":"web"}}}]}}}}'
kubectl -n svc get pods -o wide
kubectl -n svc run probe --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
  --overrides='{"spec":{"nodeName":"<the control-plane node>","tolerations":[{"operator":"Exists"}]}}' -- sleep 3600
```

**Do — part 1, `netem`.** 100% loss is a partition built out of a queueing discipline:

```sh
kubectl apply -f - <<'YAML'
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata: {name: p7c1-loss, namespace: svc}
spec:
  action: loss
  mode: all
  selector: {namespaces: [svc], labelSelectors: {app: web}}
  loss: {loss: "100", correlation: "0"}
  direction: both
  duration: 5m
YAML
```

**Observe — find the primitive, do not take its word for it:**

```sh
kubectl -n svc exec probe -- sh -c 'for i in 1 2 3 4 5 6; do curl -s -m2 http://web.svc/hostname || echo FAIL; echo; done'
ssh zain@10.10.10.131 'sudo ip netns list | head'
ssh zain@10.10.10.131 'sudo nsenter -t $(sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.pod.name=<a web pod>) | jq -r .info.pid) -n tc -s qdisc show'
```

**Do — part 2, `partition`.** Same symptom, different mechanism:

```sh
kubectl -n svc delete networkchaos p7c1-loss
kubectl apply -f - <<'YAML'
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata: {name: p7c1-part, namespace: svc}
spec:
  action: partition
  mode: all
  selector: {namespaces: [svc], labelSelectors: {app: web}}
  direction: both
  target: {mode: all, selector: {namespaces: [svc], labelSelectors: {run: probe}}}
  duration: 5m
YAML
ssh zain@10.10.10.131 'sudo nsenter -t <same pid> -n sh -c "tc -s qdisc show; iptables -S"'
```

**Expect** — in part 1, a `netem` qdisc on the pod's `eth0` with a non-zero `dropped` counter that climbs while you `curl`, and `tc -s qdisc show` as the whole of the evidence. In part 2, **`tc` back to its default qdisc and the rules in `iptables -S` instead**. Same CRD, same field names, two primitives — and the only way to know which one is in play is to look inside the pod's netns, which is what the strand's claim actually amounts to.

Expect the failure to be a **timeout** in both cases, not a refusal, and expect that to distinguish this drill from [7.C3](19-7c3-delete-one-endpoint-rule.md) at the client without any further investigation.

**Expect the four paths to be affected asymmetrically**, and this is the required deliverable. Fill the table from measurement, not from the CRD:

| Path | Broken? | How you checked |
|---|---|---|
| container ↔ container within the `web` pod | | a second process in the same netns |
| pod ↔ pod across nodes (`probe` → `web`) | | the `curl` above |
| pod ↔ pod on the same node | | a second pod on `.131` |
| `web` pod → outside the cluster | | `ping 1.1.1.1` from inside |

Expect at least one row to surprise you: `direction: both` on a *pod-selected* chaos with no `target` is not the same blast radius as one with a target, and the row that changes between part 1 and part 2 tells you which.

**Verify from outside** — the control plane's view, throughout:

```sh
kubectl -n svc get endpointslice -o json | jq -c '.items[].endpoints[]|{ip:.addresses[0],c:.conditions}'
kubectl -n svc get pods
```

Ready endpoints, running pods, and a Service that half works. Same gap as [7.C3](19-7c3-delete-one-endpoint-rule.md), reached from a completely different direction, and worth saying once more in the notes: **readiness is a statement about a process, not about a path.** A readiness probe is executed by the kubelet on the node, so it never crosses the link that is broken.

**Write down** — the four-path table for both runs, the `tc -s qdisc show` output for part 1 with its drop counter, and one sentence on what a readiness probe would have to do differently to catch this. That sentence is most of the argument for a service mesh, which is [P9's](../../phases/09-service-mesh.md) opening and not this phase's business.

**Footprint note** — **Chaos Mesh is [582 Mi](../../strands/chaos.md#install)**, and this is where the phase's steady state goes up. `pair` at 5.0GB plus `forge` at 1536MB is unchanged as a *guest* total — the 582 Mi is spent inside the control plane's 3072MB, alongside the API server. It is the first of three things this phase wants resident at once, and [the index](README.md) sets out the order they arrive and leave in, because Cilium at [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) is the third and Chaos Mesh is uninstalled before it.

**Teardown** — the chaos objects, and the extra pod:

```sh
kubectl -n svc delete networkchaos --all
kubectl -n svc delete pod probe
ssh zain@10.10.10.131 'sudo nsenter -t <pid> -n tc qdisc show'     # default qdisc, no netem
kubectl -n svc exec deploy/web -- curl -s -m3 -o /dev/null -w '%{http_code}\n' http://web.svc/hostname
```

**Chaos Mesh stays installed** — [7.C2](26-7c2-it-was-dns.md) needs it. **The topology stays.**
