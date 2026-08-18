<a id="chaos-io-errors"></a>
# Chaos drill 8.C2 — I/O errors on a fraction of calls

**Claim** — partial failure is harder to diagnose than total failure, and you can state exactly what the application saw versus what the kubelet reported.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [8.C1](14-chaos-slow-disk.md), Chaos Mesh still installed.

**Do**

1. Inject `EIO` on a percentage of calls, not all of them:

   ```yaml
   apiVersion: chaos-mesh.org/v1alpha1
   kind: IOChaos
   spec:
     action: fault
     errno: 5          # EIO
     percent: 30
     volumePath: /data
     path: '/data/**'
     selector: {labelSelectors: {app: <your-workload>}}
     duration: '5m'
   ```

2. Run it at 100% first and record the symptom. Then at 30%, and record how different the diagnosis is.
3. Check what, if anything, reached the Kubernetes API: events, conditions, restart counts.

**Observe**

```sh
kubectl logs <pod> --tail=100
kubectl get events --sort-by=.lastTimestamp | tail -20
kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[0].restartCount}'
ssh zain@10.10.10.131 'dmesg -T | grep -i "I/O error"'
```

**Expect** — at 100% the application fails cleanly and something restarts. At 30% it mostly works, retries hide the rest, and the cluster reports nothing at all. **The API surface is silent for the harder of the two failures** — which is the drill.

**Write down** — what the application saw versus what the cluster reported, at both percentages.

**Teardown** — delete the `IOChaos`. Leave everything up for [8.C3](16-chaos-detach-failure.md).
