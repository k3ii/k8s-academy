<a id="the-request-that-does-not-fit"></a>
# Install Istio as shipped and read the scheduler's refusal: a 2Gi request against a 2048MB node

**Claim** — `istiod`'s chart default is **un-installable on this lab**, and the proof is a `FailedScheduling` event naming two different reasons for two nodes: `0/2 nodes are available: 1 Insufficient memory, 1 node(s) had untolerated taint`. [The phase header asserts this](../../phases/09-service-mesh.md) as planning information; here it becomes an event you read, and the override you write to get past it is the phase's first honest statement of what a mesh costs.

**Rests on** — [which object owns the failure](03-which-object-owns-the-failure.md) for the object model, and nothing else. This is the first exercise in P9 that costs RAM.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), provisioned here and **held for the rest of the phase**. [The capstone](25-one-request-both-halves.md) releases it.

**Setup** — bring the topology up [the standard way](../../strands/lab-topologies.md#provision), then put `istioctl` on the control-plane node so that every `istioctl` and `kubectl` line in this phase is typed in the same place:

```sh
ssh hopper
cd factory && git pull
just tofu labs apply -var 'topology=pair'
just gate 130 && just gate 131
just play
scp zain@10.10.10.125:~/istio-*/bin/istioctl zain@10.10.10.130:~/bin/istioctl
ssh zain@10.10.10.130 'istioctl version --remote=false'      # the version from exercise 1
```

**Do — part 1, install what the project ships.** No overrides, no tuning, and `--skip-confirmation` so the failure is the cluster's and not a prompt you mis-answered:

```sh
istioctl install --set profile=minimal -y
kubectl -n istio-system get pods -o wide
kubectl -n istio-system describe pod -l app=istiod | sed -n '/Requests/,+3p;/Events/,$p'
```

**Observe — the arithmetic behind the event.** Do not skip to the fix; the two halves of the message have two different causes and the exercise is worth nothing if you conflate them:

```sh
kubectl get nodes -o custom-columns=\
'NAME:.metadata.name,ALLOC-MEM:.status.allocatable.memory,ALLOC-CPU:.status.allocatable.cpu'
kubectl get nodes -o json | jq -r '.items[] | "\(.metadata.name) \(.spec.taints // [])"'
kubectl -n istio-system get deploy istiod -o jsonpath='{.spec.template.spec.containers[0].resources}'; echo
```

**Do — part 2, the smallest override that makes it fit.** Two changes, and each one is a decision you can defend: a request sized from what `istiod` actually uses here, and a placement that keeps the worker free:

```sh
cat > ~/istiod-academy.yaml <<'YAML'
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  profile: minimal
  components:
    pilot:
      k8s:
        resources:
          requests: {cpu: 100m, memory: 512Mi}
          limits: {memory: 768Mi}
        nodeSelector: {node-role.kubernetes.io/control-plane: ""}
        tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
YAML
istioctl install -f ~/istiod-academy.yaml -y
kubectl -n istio-system get pods -o wide
kubectl -n istio-system get deploy istiod -o jsonpath='{.spec.template.spec.containers[0].resources}'; echo
```

**Observe — what it uses, as opposed to what it asked for.** `kubectl top` needs a metrics server this cluster has no reason to run; the kubelet's own summary API is already there:

```sh
CP=$(kubectl get node -l node-role.kubernetes.io/control-plane -o name | cut -d/ -f2)
kubectl get --raw "/api/v1/nodes/$CP/proxy/stats/summary" \
  | jq -r '.pods[] | select(.podRef.namespace=="istio-system")
           | "\(.podRef.name) \(.memory.workingSetBytes/1048576|floor)Mi"'
```

**Expect** — part 1's pod **`Pending`**, with the two-clause scheduler message above. Read it in both directions: the **worker** advertises roughly **1948Mi allocatable** — a 2048MB guest minus what the kubelet reserves — so a 2048Mi request cannot fit on it *even on an empty node*, and the **control plane** has the memory but carries `node-role.kubernetes.io/control-plane:NoSchedule`, which `istiod`'s chart does not tolerate. Expect the **500m CPU request not to be the binding constraint**: each node has 2 cores, so CPU had room. It is the memory request that is impossible and the taint that closes the only node with room.

Expect part 2 to schedule in seconds, onto the **control-plane node**, and expect the summary API to report `istiod`'s working set **well under the 512Mi you requested** with no proxies connected yet. That gap is the lesson, not an embarrassment for the chart: **2Gi is sized for a mesh with thousands of proxies on a node built for it**, and a request is an admission-time promise rather than a measurement. Re-read this number [when the sidecars arrive](19-what-a-sidecar-costs.md) — `istiod` grows with the number of proxies it pushes to, and this lab will have two.

Expect `profile=minimal` to give you **`istiod` and nothing else** — no ingress gateway, no egress gateway, no addons. Confirm that: one Deployment in `istio-system`, and no `Service` of type `LoadBalancer` waiting forever for an address this cluster cannot give it.

**Write down** — `~/istiod-academy.yaml` copied into `journal/p9-istiod-values.yaml`, the `FailedScheduling` message verbatim, the worker's allocatable memory, and one sentence naming which of the two clauses you would have hit if the control plane had been untainted. The values file is setup for every remaining exercise in this phase, so it is written once and cited, not retyped.

**Footprint note — this is the exercise the phase's ceiling problem lands in, so the whole arithmetic is here.** [`pair` is 5.0GB and `forge` is 1536MB](../../strands/lab-topologies.md#ceiling): the phase opens at **6.5GB against the 9.5GB ceiling**, with 3.0GB of margin — and none of that margin can be given to the worker, because guest sizes are fixed by the topology. **The constraint is not the host's spare RAM, it is the worker's 1948Mi allocatable**, which is what part 1 just proved.

Four things a mesh install normally brings were declined, each for a number:

| Declined | Cost | Why the phase does not need it |
|---|---|---|
| Prometheus + Grafana + Kiali addons | ~900Mi+ | Every objective's evidence is an `iptables` rule or a config dump; `istiod`'s `:15014/metrics` supplies [the push counters](12-a-scale-event-is-one-resource-type.md) directly. |
| The `bookinfo` sample | 600–900Mi | Three Java `reviews` pods to demonstrate traffic splitting, which **no P9 objective asks for**. `httpbin` + `sleep` are two pods and answer every question. |
| An ingress gateway | ~100Mi + a `LoadBalancer` that never resolves | The phase reads interception *into a pod*, not ingress at the edge. |
| Chaos Mesh | [582Mi](../../strands/chaos.md#install) | [The phase's own drill table](../../phases/09-service-mesh.md#chaos) makes 9.C4 mesh-native, and injecting an L7 fault with an external tool would hide the filter being taught. |

**Nothing about the mesh itself was softened.** A real `istiod`, real sidecars, real ambient `ztunnel`, and the capstone's full request path all remain — what was cut is telemetry that would have shown the same facts second-hand, and a sample application whose extra pods teach a different phase's lesson. The two overrides above are the smallest changes that make the install possible: sizing the request, and putting `istiod` on the node with room so **the worker stays a clean instrument** for [the sidecar cost curve](19-what-a-sidecar-costs.md) and [the flat one beside it](21-the-same-curve-flat.md).

**Teardown** — nothing to remove if part 2 succeeded; confirm the failed install left no second Deployment behind, and that `istio-system` holds exactly what you asked for:

```sh
kubectl -n istio-system get deploy,svc,pods
kubectl -n istio-system get events --field-selector reason=FailedScheduling
```

**`istiod` stays** — [the injected pod](05-a-pod-the-webhook-rewrote.md) is next and every remaining exercise needs a control plane. **The topology stays.** If you stop for the day here, `just tofu labs destroy` releases it and this exercise re-runs in about six minutes from the values file you just wrote — which is the reason it was written to a file.
