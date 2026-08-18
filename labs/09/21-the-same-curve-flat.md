<a id="the-same-curve-flat"></a>
# Run the same curve in ambient: the per-pod slope goes to zero and the cost moves to a per-node line

**Artifact** — the second half of `journal/p9-sidecar-cost.md`: the **identical measurement** at 1, 2, 4 and 8 replicas with no sidecars, in one table beside the first, plus `ztunnel`'s working set at each step. The deliverable is two slopes and one honest sentence about where the cost went — not a claim that it disappeared.

**Rests on** — [the sidecar curve](19-what-a-sidecar-costs.md) for the numbers being compared and the `mem` function being reused, and [the ambient switch](20-a-namespace-with-no-sidecars.md) for the data plane being measured.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the same function, the same node, and `ztunnel` added to what is watched:**

```sh
CP=$(kubectl get node -l node-role.kubernetes.io/control-plane -o name | cut -d/ -f2)
WK=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o name | cut -d/ -f2)
mem() { kubectl get --raw "/api/v1/nodes/$1/proxy/stats/summary" \
  | jq -r '.pods[] | .podRef.name as $p | .containers[]
           | "\($p) \(.name) \(.memory.workingSetBytes/1048576|floor)Mi \(.cpu.usageNanoCores/1000000|floor)m"'; }
mem $WK | grep -E 'httpbin|sleep|ztunnel|cni'
kubectl -n mesh get pods            # 1/1, no proxies
```

**Do — the same four steps.** Keep the load generator running through them, because an idle proxy and a proxy carrying connections are different measurements and ambient's cost is connection-shaped:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- \
  sh -c 'while true; do curl -s -o /dev/null http://httpbin:8000/get; done' &
for n in 1 2 4 8; do
  kubectl -n mesh scale deploy httpbin --replicas=$n
  kubectl -n mesh rollout status deploy httpbin --timeout=180s || echo "STOPPED AT $n"
  sleep 20
  echo "=== replicas=$n"
  mem $WK | grep httpbin | awk '{app += $3+0} END {printf "  app total %dMi\n", app}'
  mem $WK | grep -E 'ztunnel|cni'
  mem $CP | grep istiod
done
kill %1
```

**Observe — where the connections actually are:**

```sh
kubectl -n istio-system logs ds/ztunnel --tail=5
kubectl -n istio-system exec ds/ztunnel -- curl -s localhost:15020/metrics | grep -E '^istio_tcp_connections_(opened|closed)_total' | head
ssh zain@10.10.10.131 "sudo ls -l /proc/\$(sudo crictl inspect \$(sudo crictl ps -q --label io.kubernetes.container.name=ztunnel) | jq -r .info.pid)/fd | grep -c 'net:'"
```

**Expect** — the app total to climb exactly as before and the **proxy column to be absent**, because there is no per-pod proxy to have a column. Expect `ztunnel`'s working set to rise **slowly and not proportionally**: it is one process handling more connections, not eight processes handling one each. Compute both slopes and put them side by side; the ratio between them is this exercise's single number.

Expect `ztunnel`'s open `net:` descriptors to **track the replica count** — one per enrolled pod — which is the resource that does scale per pod in ambient, and it is a file descriptor rather than a process. Expect the 8-replica step to complete comfortably where [the sidecar run may have run out of node](19-what-a-sidecar-costs.md); if the sidecar run stopped at 4 or 8, say so explicitly in the table, because "this fits and that did not" is a stronger result than a slope.

**Expect the honest caveats, and write them down rather than the headline.** Three of them:

1. **The comparison is L4 against L4.** These ambient pods have no HTTP-aware proxy in their path at all. The moment [an L7 policy needs a waypoint](22-the-waypoint-l7-policy-needs.md), an Envoy comes back — one per namespace instead of one per pod, which is a better ratio and not a zero.
2. **`ztunnel` grows with connections, not with pods.** A workload with many concurrent connections per pod moves cost into `ztunnel` in a way this eight-idle-replica test cannot show. Name the shape of the workload that would break this result.
3. **`istiod` is unchanged in both runs.** The control plane was never the expensive part of a sidecar mesh; the data plane was, and only the data plane moved.

**Write down** — complete `journal/p9-sidecar-cost.md`: both curves in one table, both slopes, `ztunnel`'s per-node figure, the descriptor count, and the three caveats above in your own words. Then the sentence [the phase's ecosystem note](../../phases/09-service-mesh.md#ecosystem) claims and this exercise is the only place that tests: ambient is the escape hatch when per-pod Envoys will not fit. Say whether your numbers support it and by how much.

**Teardown**

```sh
kubectl -n mesh scale deploy httpbin --replicas=1
kubectl -n mesh rollout status deploy httpbin
jobs; kill %1 2>/dev/null
kubectl -n mesh exec deploy/sleep -c sleep -- pgrep -f 'while true' || echo "no loop left running"
mem $WK | grep -E 'httpbin|ztunnel'
```

**Kill the load loop before leaving.** A `curl` loop left running is a background variable in every later measurement, and it is the kind of thing that is discovered three exercises later as an unexplained baseline. **Ambient stays. The topology stays.**
