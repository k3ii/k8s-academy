<a id="ts10"></a>
# TS10 — `kubectl top` returns nothing, or lies

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Monitor cluster and application resource usage

> **`kubectl top` has no built-in implementation.** It reads `metrics.k8s.io`, which only exists if something registers an APIService for it. On a kubeadm cluster that something is metrics-server, it is not installed by default, and when installed it fails closed against the kubelet's self-signed certificate. Three distinct causes, one identical empty output.

**Break it** — *pass 1 only.* Produce each, and note that the **error text differs** even though the outcome does not.

1. **Not installed.** `error: Metrics API not available` — there is no APIService at all.
2. **Installed, not ready.** The APIService exists and reports `False (MissingEndpoints)` or similar, because the Deployment is not serving.
3. **Installed, failing TLS to the kubelet.** The Deployment is `Running`, looks healthy, and its logs are full of `x509: cannot validate certificate ... because it doesn't contain any IP SANs`. This is the one that wastes the most time, because everything *looks* fine.
4. **The lie.** Numbers that are stale or absent for some pods only — metrics are a rolling window, so a pod younger than the scrape interval has none. That is not a fault.

**Work it**

- **Check the APIService first**, not the Deployment. `kubectl get apiservice v1beta1.metrics.k8s.io` and its `AVAILABLE` column is the single most informative command here, and it distinguishes cause 1 from causes 2 and 3 immediately.
- **Then the Deployment and its logs.** `-n kube-system`, and read the log rather than the status, because cause 3 is `Running 1/1` with a broken data path.
- **Know the fix and why it is a fix.** `--kubelet-insecure-tls` on the metrics-server args: the kubelet serves a self-signed certificate with no IP SANs, and metrics-server validates it by default. The honest alternative is signing kubelet serving certificates properly, which is more than a drill. **B4** installs it with this flag; this drill is the other end of that.
- **Confirm the data path by hand**, which is the thing that makes the whole stack concrete: query the kubelet's summary endpoint through the API server and watch the raw numbers come back. If that works and `top` does not, the fault is between metrics-server and you, not between the kubelet and metrics-server.
- Then use it properly: `kubectl top pod --containers`, `--sort-by=cpu`, across all namespaces. Know that these are **live** numbers, that they are not requests or limits, and that `top` showing low usage says nothing about whether a pod will schedule (**W1**).

**Observe**

```sh
kubectl top nodes
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl -n kube-system get deploy metrics-server
kubectl -n kube-system logs deploy/metrics-server --tail=30
kubectl get --raw /api/v1/nodes/pair-w1/proxy/stats/summary | head -20
kubectl top pod -A --sort-by=memory | head
```

**Done when** — you name which of the three causes you are looking at from one command, and you can explain the TLS flag rather than just pasting it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Produce all three, fix all three. | 10 min |
| **2** | metrics-server healthy but one node missing from `top`. Explain it. | 8 min |
| **3** | Cold, no notes. `top` empty, cause named in one command. | 5 min |

**Teardown** — restore metrics-server to working, because **W10** depends on it and will fail confusingly otherwise.

**See also** — **B4** installs it; **W10** consumes it; **TS11** is resource trouble that `top` will not show you.
