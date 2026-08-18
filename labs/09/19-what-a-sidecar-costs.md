<a id="what-a-sidecar-costs"></a>
# Measure the marginal pod: what one sidecar costs, four times over, on a node you can exhaust

**Artifact** — `journal/p9-sidecar-cost.md`: a table of **working-set memory per pod, split by container**, at 1, 2, 4 and 8 replicas, with `istiod`'s own footprint measured at each step and a **cost-per-pod** figure derived from the slope rather than from a single reading. The measurement is taken from the kubelet's summary API, because [this cluster has no metrics server and deliberately no telemetry stack](04-the-request-that-does-not-fit.md).

**Rests on** — [the injected workloads](05-a-pod-the-webhook-rewrote.md), and [the worker-thread question left open](03-which-object-owns-the-failure.md), which this exercise finally has a sidecar to answer.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — one command that reads every container's memory, kept as a shell function** because it is run five times:

```sh
CP=$(kubectl get node -l node-role.kubernetes.io/control-plane -o name | cut -d/ -f2)
WK=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o name | cut -d/ -f2)
mem() { kubectl get --raw "/api/v1/nodes/$1/proxy/stats/summary" \
  | jq -r '.pods[] | .podRef.name as $p | .containers[]
           | "\($p) \(.name) \(.memory.workingSetBytes/1048576|floor)Mi \(.cpu.usageNanoCores/1000000|floor)m"'; }
mem $WK | grep -E 'httpbin|sleep'
mem $CP | grep istiod
kubectl describe node $WK | sed -n '/Allocated resources/,+8p'
```

**Do — answer the question exercise 3 could not.** A sidecar is the same Envoy binary; the number it picks for worker threads is now readable in context:

```sh
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET server_info | jq '{concurrency, state}'
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- nproc
kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].spec.containers[?(@.name=="istio-proxy")].resources}'; echo
```

**Do — the curve.** Four steps, with a check between each; the check is not decoration:

```sh
for n in 1 2 4 8; do
  kubectl -n mesh scale deploy httpbin --replicas=$n
  kubectl -n mesh rollout status deploy httpbin --timeout=180s || echo "STOPPED AT $n"
  sleep 20
  echo "=== replicas=$n"
  mem $WK | grep httpbin | awk '{proxy += ($2=="istio-proxy")?$3+0:0; app += ($2=="httpbin")?$3+0:0}
                                 END {printf "  app total %dMi   proxy total %dMi\n", app, proxy}'
  mem $CP | grep istiod
  kubectl -n mesh get pods -l app=httpbin --no-headers | awk '{print $3}' | sort | uniq -c
done
```

**Expect** — a per-pod `istio-proxy` working set in the **tens of Mi** at idle, and the app container to be smaller than its own proxy. Expect the proxy total to be close to **linear** in replica count while `istiod` grows **sub-linearly** — it holds one push context and one stream per proxy, not a copy of the mesh per pod. Take the slope, not the intercept: the first sidecar carries startup cost the eighth does not, and the number worth writing down is the **difference between consecutive steps**.

Expect `concurrency` on the sidecar to be a small number and expect it **not** to be a mystery once you have looked at `nproc` and the container's CPU limit together — Istio derives the proxy's thread count from the CPU it is allowed, and the pod sees the node's cores. Record all three numbers and state which one the concurrency followed. This is the arithmetic behind the phrase "a core per busy sidecar": threads are allocated per pod from a per-node supply, and at 8 replicas the node has promised more Envoy worker threads than it has cores.

**Expect the ceiling to be reachable, and treat reaching it as a result rather than a failure.** [The worker has 1948Mi allocatable](04-the-request-that-does-not-fit.md), already carrying kubelet, the CNI and `kube-proxy`. If pods go `Pending` or the node reports memory pressure at 8, **record the number at which it happened and stop** — that number is the most useful line in the table, and it is the same measurement [the ambient run](21-the-same-curve-flat.md) will be compared against. Do not raise the guest to make the curve prettier; the guest size is [fixed by the topology](../../strands/lab-topologies.md#pair) and the constraint is the point.

**Write down** — `journal/p9-sidecar-cost.md`: the four-row table (replicas, app total, proxy total, `istiod`), the marginal cost per pod computed from the slope, the concurrency figure with the two numbers that explain it, and one sentence on what fraction of the pod's total memory is proxy. That fraction is the number [ambient](20-a-namespace-with-no-sidecars.md) exists to change, and the table is only half an artifact until the second curve is beside it.

**Footprint note** — this exercise deliberately walks the node toward its limit and is the only one in the phase that does. It is safe because nothing else is co-resident: [no telemetry stack, no Chaos Mesh, no `bookinfo`](04-the-request-that-does-not-fit.md), and `istiod` is pinned to the other node so that the thing being measured is the only thing growing. That is what "the worker stays a clean instrument" was for.

**Teardown — back to one replica, and verify the node recovered:**

```sh
kubectl -n mesh scale deploy httpbin --replicas=1
kubectl -n mesh rollout status deploy httpbin
sleep 15
mem $WK | grep -E 'httpbin|sleep'
kubectl describe node $WK | sed -n '/Allocated resources/,+8p'
kubectl get nodes -o json | jq -r '.items[] | "\(.metadata.name) \([.status.conditions[] | select(.status=="True") | .type] | join(","))"'
```

**Leaving eight sidecars running would silently break the next three exercises** — the ambient install adds two DaemonSets to the same node, and a worker already at its limit would make an ambient failure look like an ambient bug. Every condition back to `Ready` alone, and one `httpbin` pod, before moving on. **The topology stays.**
