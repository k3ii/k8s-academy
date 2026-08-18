<a id="two-heartbeats-two-frequencies"></a>
# Predict how long a dead node stays Ready, from four numbers you can read

**Claim** — a node reports it is alive in two different ways at two different rates, for two different readers, and the delay before a dead node is noticed is an arithmetic consequence of four settings — three on the node, one on the controller manager. You can compute it before you break anything.

**Rests on** — nothing in this phase; it is the prerequisite for [6.C2](22-6c2-the-kubelet-stops-the-pods-do-not.md) and [6.C1](23-6c1-the-node-vanishes.md), which are the two ways of testing the number.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, restored to its default kubelet configuration.

**Read** — KEP-589, node heartbeat via Lease (item 18), for the *why*: what was expensive about the old mechanism, and what is written now instead. Then find the node side in `pkg/kubelet/nodestatus/` and the lease controller beside it. The question to answer: **which of the two heartbeats does the node-lifecycle controller actually watch**, and what is the other one for?

**Do**

1. Watch both heartbeats at once, for a minute, and time them:

   ```sh
   kubectl -n kube-node-lease get lease pair-worker -o jsonpath='{.spec.renewTime}{"\n"}'
   for i in $(seq 1 12); do
     kubectl -n kube-node-lease get lease pair-worker -o jsonpath='{.spec.renewTime}{"\t"}{.spec.leaseDurationSeconds}{"\n"}'
     sleep 5
   done
   ```

   ```sh
   for i in $(seq 1 6); do
     kubectl get node pair-worker -o jsonpath='{.status.conditions[?(@.type=="Ready")].lastHeartbeatTime}{"\n"}'
     sleep 15
   done
   ```

2. Collect the four numbers:

   ```sh
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" \
     | jq '.kubeletconfig | {nodeStatusUpdateFrequency, nodeStatusReportFrequency, nodeLeaseDurationSeconds}'
   ssh zain@10.10.10.130 'sudo grep -e node-monitor -e "node-monitor-grace-period" /etc/kubernetes/manifests/kube-controller-manager.yaml || echo "not set — find the default"'
   ```

   If the grace period is not on the command line, it is a default: find it in `cmd/kube-controller-manager` rather than in a blog post, and cite the file.

3. **Compute the worst case** — from the moment a node dies to the moment `Ready` becomes `Unknown` — and write it down as a single number with the arithmetic beside it. Then compute a second number: how long until the pods on that node are marked for deletion, which is a *different* controller with its own timer.

**Observe** — the two heartbeat intervals against each other. One should be several times slower than the other, and the lease should be renewing far more often than the node status changes.

**Expect** — the lease to renew every few seconds and carry nothing but a timestamp, while the full node status is written on a much longer cycle unless a condition actually changes. That asymmetry is the whole KEP: a node object is large and a lease is tiny, so at a thousand nodes the cheap write can be frequent and the expensive one rare.

Expect your computed detection latency to be around 40 seconds with the shipped defaults, and expect the pod-eviction timer to be *minutes* longer. The gap between "the node is Unknown" and "its pods are gone" is deliberate and it is the number that decides how long a workload is unavailable after a node dies — [6.C1](23-6c1-the-node-vanishes.md) measures it for real.

Expect `lastHeartbeatTime` on the Ready condition to move even when nothing else in the status does. It is the one field that made the old heartbeat expensive.

**Write down** — the four settings with their sources, the two computed latencies with the arithmetic, and one sentence naming which controller owns each. [The chaos table's 6.C1 row](../../phases/06-kubelet-node.md#chaos) asks you to explain the latency from this mechanism; this is the explanation, written before the evidence.

**Footprint note** — reading only.

**Teardown** — nothing created. **The topology stays** — the next two exercises test these numbers.
