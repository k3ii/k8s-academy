<a id="the-stack-that-must-not-be-evicted"></a>
# Install the metrics stack on the node it is not measuring

**Artifact** — `kube-prometheus-stack` running on `pair` inside a measured budget, **pinned to the control plane**, scraping the worker's kubelet, cAdvisor and node-exporter — with a Grafana dashboard showing node memory, cgroup pressure and pod restarts on one screen.

**Rests on** — [the cgroup files you read by hand](15-the-cgroup-tree-under-one-pod.md). Every number on the dashboard is one of those files, scraped on a timer, and [the phase's ecosystem note](../../phases/06-kubelet-node.md#ecosystem) makes that the required internals claim rather than an aside.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, back on its default kubelet configuration.

**Setup**

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

**Do**

1. Install it minimised, and pinned. Every flag below is either a cost cut or the pin:

   ```sh
   cat > /tmp/kps-values.yaml <<'EOF2'
   alertmanager:
     enabled: false
   prometheusOperator:
     resources: {limits: {memory: 128Mi}, requests: {memory: 96Mi}}
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     admissionWebhooks: {enabled: false}
   prometheus:
     prometheusSpec:
       retention: 2h
       scrapeInterval: 30s
       evaluationInterval: 30s
       replicas: 1
       resources: {limits: {memory: 512Mi}, requests: {memory: 384Mi}}
       nodeSelector: {node-role.kubernetes.io/control-plane: ""}
       tolerations: [{operator: Exists}]
       storageSpec: null
   grafana:
     resources: {limits: {memory: 128Mi}, requests: {memory: 96Mi}}
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     persistence: {enabled: false}
     defaultDashboardsTimezone: browser
   kube-state-metrics:
     resources: {limits: {memory: 64Mi}, requests: {memory: 48Mi}}
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
   prometheus-node-exporter:
     resources: {limits: {memory: 32Mi}, requests: {memory: 24Mi}}
   EOF2
   helm install kps prometheus-community/kube-prometheus-stack \
     -n monitoring --create-namespace -f /tmp/kps-values.yaml
   kubectl -n monitoring get pods -o wide
   ```

2. Confirm the pin took — this is the whole point of the exercise and it is one command:

   ```sh
   kubectl -n monitoring get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
   ```

   Everything except the two node-exporters must be on `pair-cp`.

3. Check the scrape targets are actually up, rather than assuming a green install means green scrapes:

   ```sh
   kubectl -n monitoring port-forward svc/kps-kube-prometheus-stack-prometheus 9090:9090 &
   curl -s localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.health)\t\(.labels.job)\t\(.labels.instance)"' | sort | uniq -c
   ```

4. Measure what it cost, by the same method you used for [Chaos Mesh](08-chaos-mesh-at-582mi.md):

   ```sh
   for n in pair-cp pair-worker; do
     kubectl get --raw "/api/v1/nodes/$n/proxy/metrics/cadvisor" \
       | grep '^container_memory_working_set_bytes{' | grep 'namespace="monitoring"'
   done
   ```

5. Build one dashboard with three panels — node memory available, `container_memory_working_set_bytes` for the pods on the worker, and `kube_pod_container_status_restarts_total`. Grafana's login is in `kubectl -n monitoring get secret kps-grafana -o jsonpath='{.data.admin-password}' | base64 -d`.

**Expect** — the whole stack up in a couple of minutes, all targets `up`, and the measured total in the region of 850–900Mi. Expect the two `kubelet` scrape jobs to be distinct — the kubelet's own metrics and its cAdvisor metrics are separate endpoints on the same port, and [exercise 26](26-the-metric-is-the-file.md) needs both.

Expect a target to be `down` if anything in the cluster is unhealthy, and expect that to be *informative*: Prometheus pulls, so a node that dies stops producing data rather than reporting an error. That is the property that makes [drill 6.C1's](23-6c1-the-node-vanishes.md) graph a gap rather than a spike, and it is worth confirming now while you still have both nodes.

**Write down** — the measured footprint per component against the budget, the target list, and the dashboard's three queries.

**Footprint note — this is the phase's real ceiling risk, and it is handled by two choices rather than by more RAM.**

`pair` is 5.0GB and `forge` is 1536MB, so the guests total 6.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling). The pressure is *inside* the control-plane guest: 3072MB now holds the control plane, Chaos Mesh's controller and roughly 800Mi of monitoring. It fits, and the two choices that make it fit are:

1. **Metrics only. No logs, no traces.** [The lab-fit review flagged metrics + logs + traces co-resident as a candidate that does not fit](../../strands/lab-topologies.md#ceiling), and on these numbers it does not: Loki with its ingester and Tempo with its distributor add roughly 700–900Mi more, which is the control-plane guest's remaining headroom spent twice over. **The smallest change is not to install them** — this phase's questions are all answerable from metrics, and nothing here needs a log aggregator when `journalctl` is one `ssh` away. A phase that genuinely needs traces can install one signal at a time and tear it down between; that is P9's problem, not this one's.
2. **The stack is pinned away from the node it measures.** An observability stack living on the worker would be a Burstable workload sitting on a node you are about to drive into eviction — it would be ranked, evicted, and take the recording of its own eviction with it. Pinning it to the control plane leaves the worker's 2048MB as a clean instrument and keeps the recorder alive through the event it is recording. **This is not tidiness; it is the difference between having a time series of the eviction and having a gap where it was.**

If the control-plane guest does come under pressure, cut in this order — Grafana off between exercises (query Prometheus directly), then retention to 1h, then scrape interval to 60s. Raising the guest is the last resort and would put `pair` over 5.0GB, which changes every footprint statement in the phase.

**Teardown** — **nothing yet.** The stack is the instrument for the next three exercises and is destroyed with the topology at [the capstone](29-the-capstone-trace.md). Stop the port-forward when you are done with it. **The topology stays.**
