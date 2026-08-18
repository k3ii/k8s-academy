<a id="chaos-slow-disk"></a>
# Chaos drill 8.C1 — a slow disk under a live workload

**Claim** — you can name which layer surfaced the symptom first, and explain how a pod is `Running` and useless at the same time.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with your driver from [the in-cluster driver](13-csi-driver-in-cluster.md) still deployed.

**Setup** — Chaos Mesh, installed once per [the minimised install](../../strands/chaos.md#install) at 582Mi. [Do it by hand first](../../strands/chaos.md#principle): this drill has a manual form and you owe yourself one run of it before the CR.

**Do**

1. Run a workload that writes to the volume continuously and exposes a latency metric you can watch — anything whose slowness you would notice.
2. Inject latency on the volume's mount path:

   ```yaml
   apiVersion: chaos-mesh.org/v1alpha1
   kind: IOChaos
   spec:
     action: latency
     delay: '500ms'
     percent: 100
     volumePath: /data
     path: '/data/**'
     selector: {labelSelectors: {app: <your-workload>}}
     duration: '5m'
   ```

3. Watch, in this order: the application, then the pod's readiness, then the node, then the API. Record which one moved first and how long each lagged.
4. Raise the delay until the liveness probe fails. Note the delay at which it does.

**Observe**

```sh
kubectl get pods -w
kubectl describe pod <pod> | sed -n '/Events/,$p'
kubectl top pod
ssh zain@10.10.10.131 'iostat -x 2; dmesg -T | tail -30'
```

**Expect** — the pod stays `Running` and `Ready` long after the application is unusable, because neither status is a statement about throughput. The [mechanism is a FUSE filesystem injected into the mount namespace](../../strands/chaos.md#catalogue), not a real slow disk, which is worth remembering when the symptoms look too clean.

**Write down** — the order the layers reacted in, and one sentence on what you would have to add to a readiness probe to catch this.

**Teardown** — delete the `IOChaos` object. Leave the cluster and Chaos Mesh up for [8.C2](15-chaos-io-errors.md).
