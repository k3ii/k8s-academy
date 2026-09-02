<a id="probes-three-kinds"></a>
# Three probes, three different consequences

**Claim** — you can make one container fail each probe type in turn. You can then name the distinct consequence of each failure: the container is restarted, the pod is removed from service, or the container never starts at all. Two of the three failures produce a pod that looks fine in `kubectl get pods`.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Deploy one container that serves three endpoints, and give each endpoint a file-backed switch that you can toggle. Two shapes work here. Use a `busybox httpd` over a directory, or use an `nginx` whose `/ready` is a file that you `rm` with `kubectl exec`. The point is control: *you* decide when each probe fails, from outside the container.
2. Wire all three probes to their own endpoint. Give the probes deliberately different timings, so that you can tell them apart in the events:

   ```yaml
   startupProbe:   {httpGet: {path: /started, port: 8080}, failureThreshold: 30, periodSeconds: 2}
   livenessProbe:  {httpGet: {path: /healthz,  port: 8080}, periodSeconds: 5,  failureThreshold: 3}
   readinessProbe: {httpGet: {path: /ready,    port: 8080}, periodSeconds: 2,  failureThreshold: 2}
   ```

3. **Predict first, then break one probe at a time.** Before each break, write down three things: what changes in `kubectl get pods`, what changes in `kubectl get endpointslices`, and whether `RESTARTS` moves.
   - Fail **readiness** only.
   - Fail **liveness** only.
   - Fail **startup** from the very beginning. Deploy a fresh pod whose `/started` never appears.
4. While liveness fails, watch the restart happen. Then keep watching. Count the restarts over two minutes, and note the *gap* that grows between them.
5. Fail liveness and readiness at the same time. Predict which of the two you can still observe. One of them stops mattering.

**Observe**

```sh
kubectl get pods -w
kubectl describe pod <name> | tail -20        # the Events block is the probe transcript
kubectl get endpointslices -w
```

**Expect** — each failure has its own signature:

- Readiness failure. The pod shows `READY 0/1`. It is still `Running`. It is gone from the EndpointSlice. `RESTARTS` does not change.
- Liveness failure. `RESTARTS` climbs, with a back-off that doubles up to a five-minute cap. The pod cycles through `Ready` in between the restarts.
- Startup failure. The container is killed after `failureThreshold × periodSeconds`, and **liveness never ran at all**.

That last point is the whole reason why the third probe exists. It also explains why a slow-booting application with only a liveness probe restart-loops forever. The failure that surprises people is readiness. It gives you a pod that is `Running`, has never restarted, and serves nothing.

**Write down** — the consequence table of three rows. Then write one sentence on why a slow-starting application with a liveness probe and no startup probe can never start.

**Teardown** — restore every toggled endpoint, and confirm that the pod is `1/1`. Keep the Deployment, because [the EndpointSlice drain](15-endpointslice-drains.md) uses this readiness switch. **The topology stays.**
