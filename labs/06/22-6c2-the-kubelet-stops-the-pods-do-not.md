<a id="6c2-the-kubelet-stops-the-pods-do-not"></a>
# 6.C2 — Stop the kubelet under load and time everything that does not happen

**Claim** — the kubelet is not in the data path. Stop it and every container keeps running, every established connection keeps working, and the only thing that breaks is the cluster's *picture* of the node — on the schedule you computed from the lease.

**Rests on** — [the two heartbeats](21-two-heartbeats-two-frequencies.md). This drill scores that arithmetic. It is [6.C2](../../phases/06-kubelet-node.md#chaos).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, default kubelet configuration restored.

**Setup — put real load on the node first**, because "nothing broke" is only interesting if something was running:

```sh
kubectl create ns c2
kubectl -n c2 create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=3 -- /agnhost netexec --http-port=8080
kubectl -n c2 patch deployment web -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"pair-worker"}}}}}'
kubectl -n c2 expose deployment web --port=8080
kubectl -n c2 rollout status deployment web
```

Drive traffic continuously from the control plane so an interruption is visible as a gap rather than as a memory:

```sh
ssh zain@10.10.10.130 'CLUSTERIP=<web service IP>; while :; do \
  printf "%s %s\n" "$(date +%T)" "$(curl -s -m 2 -o /dev/null -w %{http_code} http://$CLUSTERIP:8080/)"; sleep 1; done' | tee /tmp/c2-traffic.log
```

**Do**

1. Note the wall-clock second, then stop the kubelet — and only the kubelet:

   ```sh
   ssh zain@10.10.10.131 'date +%T; sudo systemctl stop kubelet'
   ```

2. Immediately, and then every 10 seconds, record three things: the node's `Ready` condition, the lease's `renewTime`, and whether traffic is still flowing.

   ```sh
   kubectl get nodes -w -o custom-columns=NAME:.metadata.name,READY:'.status.conditions[?(@.type=="Ready")].status',REASON:'.status.conditions[?(@.type=="Ready")].reason'
   kubectl -n kube-node-lease get lease pair-worker -o jsonpath='{.spec.renewTime}{"\n"}'
   ```

3. On the node itself, confirm what is still true while the cluster believes otherwise:

   ```sh
   ssh zain@10.10.10.131 'sudo crictl ps | head; systemctl is-active containerd kubelet'
   ```

4. Try to change something while the kubelet is down, and watch it not happen:

   ```sh
   kubectl -n c2 scale deployment web --replicas=5
   kubectl -n c2 get pods -o wide
   kubectl -n c2 delete pod <one of the running pods>
   ```

5. Note the second the taints appear, then start the kubelet and time the recovery:

   ```sh
   kubectl get node pair-worker -o jsonpath='{range .spec.taints[*]}{.key}={.effect}{"\n"}{end}'
   ssh zain@10.10.10.131 'date +%T; sudo systemctl start kubelet'
   ```

**Expect** — traffic **uninterrupted** across the whole outage. The containers were started by the kubelet and are supervised by containerd; the kubelet's death is not their death, and `kube-proxy`'s rules on the other node were programmed from EndpointSlices that nothing has changed. That is the drill's claim and the log file is the evidence.

Expect `Ready` to become `Unknown` — not `False` — with a reason naming the missing status update, at roughly the latency you computed. `Unknown` is the honest value: nobody has said the node is unhealthy, only that nobody has heard from it.

Expect the deleted pod to sit in `Terminating` and stay there. The API server accepted the delete and set a `deletionTimestamp`; the only component that can stop the container and confirm it is the one you stopped. **A `Terminating` pod that never terminates is a node problem, and this is the shortest path to internalising that.**

Expect the two new replicas from the scale-up to be scheduled **elsewhere or nowhere** once the node is tainted, and expect the whole picture to converge within seconds of the kubelet starting: it re-lists its pods, finds the running containers, adopts them, and completes the deletion it never saw.

**Write down** — the timeline with real timestamps: stop → last lease renewal → `Ready=Unknown` → taint → kubelet start → `Ready=True` → deletion completed. Beside each interval, the setting that governs it. Compare with [exercise 21's](21-two-heartbeats-two-frequencies.md) prediction and account for the difference.

**Footprint note** — three small `agnhost` pods, a few tens of MB. No change to the 6.5GB steady state, and no chaos tooling is used: [the fault is `systemctl stop`](../../strands/chaos.md#manual-drills), which is more precise than anything a tool would inject here.

**Teardown**

```sh
kubectl delete ns c2
ssh zain@10.10.10.131 'systemctl is-active kubelet'
```

Kill the traffic loop, keep `/tmp/c2-traffic.log`. **The topology stays.**
