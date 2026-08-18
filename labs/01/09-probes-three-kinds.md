<a id="probes-three-kinds"></a>
# Three probes, three different consequences

**Claim** — you can make a single container fail each probe type in turn and name the distinct consequence of each: restarted, removed from service, or never started at all. Two of the three produce a pod that looks fine in `kubectl get pods`.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Deploy one container that serves three endpoints you can toggle, and a file-backed switch for each — a `busybox httpd` over a directory, or an `nginx` whose `/ready` is a file you `rm` with `kubectl exec`. The point is that *you* decide when each probe fails, from outside.
2. Wire all three probes to their own endpoint, with deliberately different timings so you can tell them apart in the events:

   ```yaml
   startupProbe:   {httpGet: {path: /started, port: 8080}, failureThreshold: 30, periodSeconds: 2}
   livenessProbe:  {httpGet: {path: /healthz,  port: 8080}, periodSeconds: 5,  failureThreshold: 3}
   readinessProbe: {httpGet: {path: /ready,    port: 8080}, periodSeconds: 2,  failureThreshold: 2}
   ```

3. **Predict, then break, one at a time.** For each, write down beforehand: what changes in `kubectl get pods`, what changes in `kubectl get endpointslices`, and whether `RESTARTS` moves.
   - Fail **readiness** only.
   - Fail **liveness** only.
   - Fail **startup** from the very beginning (deploy a fresh pod whose `/started` never appears).
4. While liveness is failing, watch the restart happen and then keep watching. Count restarts over two minutes and note the *gap* growing between them.
5. Fail liveness and readiness simultaneously and predict which one you can observe. One of them stops mattering.

**Observe**

```sh
kubectl get pods -w
kubectl describe pod <name> | tail -20        # the Events block is the probe transcript
kubectl get endpointslices -w
```

**Expect** — readiness failure: `READY 0/1`, still `Running`, gone from the EndpointSlice, `RESTARTS` unchanged. Liveness failure: `RESTARTS` climbing with a back-off that doubles to a five-minute cap, and the pod cycling through `Ready` in between. Startup failure: the container is killed at `failureThreshold × periodSeconds` and **liveness never ran at all** — that is the whole reason the third probe exists, and it is why a slow-booting app with only a liveness probe restart-loops forever. The one that surprises people is readiness: a pod that is `Running`, has never restarted, and is serving nothing.

**Write down** — the three-row consequence table, and one sentence on why a slow-starting application with a liveness probe and no startup probe cannot ever start.

**Teardown** — restore every toggled endpoint and confirm the pod is `1/1`. Keep the Deployment; [the EndpointSlice drain](15-endpointslice-drains.md) uses this readiness switch. **The topology stays.**
