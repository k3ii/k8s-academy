<a id="w11"></a>
# W11 — Liveness, readiness and startup: break one, watch what happens

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / Self-healing primitives

> **A failing liveness probe restarts the container; a failing readiness probe takes it out of the Service.** One is visible as `RESTARTS` climbing, the other as endpoints emptying with the pod still `Running`. The second is the one people miss, because `kubectl get pods` shows `Running 1/1`… except the `READY` column says `0/1`, and that column is the whole answer.

**Do**

1. A Deployment behind a Service. Add **readiness** against a path you control. Break the path. Pod stays `Running`, `READY` goes `0/1`, and the Service's endpoints empty. Watch the endpoints, not the pod.
2. Fix it, confirm the endpoint returns. Readiness is continuous — it does not latch.
3. **Liveness** against the same path. Break it. Now `RESTARTS` climbs and the container is killed and restarted on a backoff. Read `kubectl describe` and find `Liveness probe failed:` with the actual probe output in the events.
4. **Do the arithmetic out loud**, because the defaults catch people: `failureThreshold × periodSeconds` after `initialDelaySeconds` is how long a container lives before a failing liveness probe kills it. Defaults are `periodSeconds: 10`, `failureThreshold: 3`, `timeoutSeconds: 1`. That `timeoutSeconds: 1` is the one that bites — a slow but healthy endpoint fails.
5. **Startup probes exist to stop liveness killing a slow starter.** Give a container a long start and a tight liveness probe and watch it be killed forever in a loop. Add a startup probe: liveness is **suspended** until startup succeeds, then takes over. That is the correct fix, and raising `initialDelaySeconds` is the wrong one, because it degrades detection for the whole life of the container.
6. The three handler types — `httpGet`, `exec`, `tcpSocket` — one of each, so none is unfamiliar. An `exec` probe's exit status is the result.

**Observe**

```sh
kubectl get pods            # READY 0/1 while Running
kubectl get endpoints web
kubectl describe pod web | sed -n '/Events/,$p'
kubectl get pod web -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'
kubectl get pod web -o jsonpath='{.spec.containers[0].livenessProbe}' | python3 -m json.tool
```

**Done when** — given a pod's symptoms you name which probe is failing without reading the spec, and you write all three from memory with sane thresholds.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. All three probes, both failure modes, the arithmetic. | 10 min |
| **2** | A Deployment with probes that are already wrong. Fix without a restart loop. | 8 min |
| **3** | Cold, no notes. Readiness and liveness on a Deployment, both proved. | 5 min |

**Teardown** — delete the namespace.

**See also** — **TS15** is empty endpoints arrived at from the other direction; **TS2** is the restart loop with the cause unknown.
