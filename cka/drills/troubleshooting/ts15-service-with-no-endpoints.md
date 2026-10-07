<a id="ts15"></a>
# TS15 — A Service has no endpoints: which of the four is it?

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot services and networking

> **Four independent faults produce one identical symptom.** The backend list is empty, the Service looks healthy, and the client hangs. The skill is not repairing it — each repair is one line — it is **naming which of the four it was** before touching anything, because the wrong guess costs you the rung below it.

> **Pinned for a structural reason.** [The diagnostic](../../plan.md#diagnostic) probes four of Troubleshooting's five sub-competencies and probes this one nowhere, so the gap rule cannot see it. An operator cold here can still score well on Troubleshooting and be allocated zero hours against it. This drill runs regardless of what the diagnostic said.

**Break it** — *pass 1 only; you induce this yourself.*

Build a working Deployment and ClusterIP as in [N5](../networking/n05-clusterip-and-endpoints.md), then produce each of the four in turn:

1. **Selector mismatch.** The Service selects a label no pod carries.
2. **Pod labels changed.** The selector is right; the pods drifted out from under it.
3. **Readiness failing.** The pods match and are `Running`, but not `Ready` — so they are excluded from the backend list by design. `kubectl get pods` looks almost fine; the `READY` column is the tell.
4. **`targetPort` mismatch.** A number that no container exposes, or a **port name** that does not match the container's. This one is different in kind: the backend list is *not* empty for the pod-selection reason — the Service binds and the traffic goes nowhere.

**Work it** — the ladder, in this order, because each rung is cheaper than the next:

```sh
kubectl describe svc <svc> | sed -n '/Selector/,/Endpoints/p'   # rung 1: what does it select?
kubectl get pods --show-labels                                   # rung 2: what do the pods carry?
kubectl get pods -o wide                                         # rung 3: READY column, then describe for the probe
kubectl get pod <pod> -o jsonpath='{.spec.containers[*].ports}'  # rung 4: names and numbers
```

**Observe**

```sh
kubectl get endpointslices -l kubernetes.io/service-name=<svc> -o wide
kubectl describe pod <pod> | sed -n '/Conditions/,/Events/p'
kubectl get events --field-selector involvedObject.name=<pod> --sort-by=.lastTimestamp
```

**Done when** — you name the rung *before* you fix it, and the fix is the one that rung implies. Fixing it by trying all four in sequence is a fail even if the Service ends up working.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean namespace. You induce each of the four and read its signature. | 10 min |
| **2** | A namespace someone left messy. The fault is known; the noise is not. | 8 min |
| **3** | **Injected.** `cka-inject.sh` plants one and does not say which. Cold, no notes, clock visible. | **5 min** |

**Teardown** — `cka-inject.sh revert`, then delete the namespace. Confirm the cluster is clean before the next drill; a half-reverted injection is worse than no injection.

**See also** — [N5](../networking/n05-clusterip-and-endpoints.md), the same machinery built rather than diagnosed, and **TS18**, which starts where this one ends: the backends are present and traffic still does not arrive.
