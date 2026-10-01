<a id="w10"></a>
# W10 — An HPA on CPU, driven under load that is actually real

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / Workload autoscaling

> **An HPA on CPU is a percentage of the request, not of the core.** Nearly every HPA that "does not work" is one of two things: no `resources.requests.cpu` on the container, so there is no denominator and the HPA reports `<unknown>`; or metrics-server is not returning data, so there is no numerator. Check both before touching the HPA itself.

> **Depends on B4** for metrics-server. On a kubeadm cluster metrics-server also needs `--kubelet-insecure-tls`, because the kubelet serves a self-signed certificate — the install otherwise fails closed, with a Deployment that looks nearly healthy.

**Do**

1. A Deployment with **`requests.cpu` set** and one replica. Confirm `kubectl top pod` returns a number for it; if it does not, stop and fix that first, because nothing downstream can work.
2. `kubectl autoscale` it on CPU, then read the HPA back as YAML and see what the shorthand actually generated.
3. **Generate real load** — a busy loop inside the pod, or a load pod hitting the Service. Do not fake it by editing the metric; the delay between load and reaction is part of what you are learning.
4. Watch the scale-up. It is not instant: metrics-server scrapes on an interval and the HPA reconciles on another, so expect tens of seconds. **Impatience here is what makes people conclude a working HPA is broken.**
5. Stop the load and watch the scale-*down*, which is deliberately much slower — a stabilisation window of several minutes by default, so a brief dip does not cause a flap. Know that this is configurable in `behavior`, and that the asymmetry is intentional.

**Observe**

```sh
kubectl top pods
kubectl get hpa -w
kubectl describe hpa <name> | sed -n '/Metrics/,/Events/p'
kubectl get deploy <name> -o jsonpath='{.spec.template.spec.containers[0].resources}{"\n"}'
```

**Done when** — the HPA shows a real percentage rather than `<unknown>`, replicas rise under load and fall after it, and you can state what each of the two missing pieces looks like from `describe hpa` alone.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build it, load it, watch both directions. | 10 min |
| **2** | A Deployment that already exists and has **no** CPU request. Diagnose the `<unknown>` and fix it. | 8 min |
| **3** | Cold, no notes, clock visible. From an empty namespace to a scaled-up Deployment. | 5 min |

**Teardown** — delete the namespace. Kill the load generator first; one left running quietly distorts every later measurement on the node.

**See also** — **TS10** is the three different reasons `kubectl top` returns nothing, which is step 1 of this drill as a fault. **TS11** is the other side of a CPU/memory request: what happens when the limit is the thing you got wrong.
