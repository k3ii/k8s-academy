<a id="ts18"></a>
# TS18 — NodePort or Ingress unreachable from off-node: work the chain

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot services and networking

> **There are five places this can break and they are strictly ordered, so test in order and stop at the first failure.** Pod → Service endpoints → kube-proxy's rules on the node → the node's firewall → whatever sits in front. Jumping to the firewall because the symptom is external is how twenty minutes disappear; the fault is usually two rungs earlier.

**Break it** — *pass 1 only.* Produce several, because the point is the chain, not any one fault. **F08** — a Service selector matching nothing — is the catalogue's version of rung 2.

1. A selector that matches no pod. `get svc` looks perfect.
2. A `targetPort` that no container listens on.
3. A readiness probe failing, so endpoints empty while pods run (**W11**).
4. `externalTrafficPolicy: Local` with no pod on the node you are curling (**N6**).
5. An `iptables` DROP on the node for the NodePort range.

**Work it** — rung by rung, each with one command:

- **Rung 0 — in-cluster first.** Curl the ClusterIP from a pod. **If that fails, the external path is irrelevant** and you have just eliminated kube-proxy, the firewall and the controller in one command. This is the single highest-value step and it is the one most often skipped.
- **Rung 1 — the pod.** Curl the pod IP directly. Rules out the Service entirely.
- **Rung 2 — endpoints.** `kubectl get endpointslice`. Empty means selector, labels, readiness or `targetPort` — the four causes **TS15** enumerates. Do not go further until this is populated.
- **Rung 3 — kube-proxy.** Confirm its mode (`iptables` on this cluster) and that its pod is running on the node you are curling. Then find your Service's rules: `iptables-save | grep <nodeport>` or `-t nat -L KUBE-NODEPORTS`. **No rule means kube-proxy never programmed it**, which is a kube-proxy fault, not a networking one — and the logs will say why.
- **Rung 4 — the node.** `ss -lntp | grep <nodeport>` to confirm something is listening, then the firewall. Curl **on the node itself** first: if local works and remote does not, it is the firewall or the route, and nothing above rung 4 can be at fault.
- **Rung 5 — the front.** For Ingress, the controller's own logs and its Service's external address (**N12**); for a LoadBalancer, MetalLB's speaker logs (**N7**).

**Observe**

```sh
kubectl exec probe -- wget -qO- --timeout=3 http://<clusterip>
kubectl get endpointslice -l kubernetes.io/service-name=<svc>
kubectl -n kube-system get ds kube-proxy -o wide
kubectl -n kube-system logs ds/kube-proxy --tail=30
sudo iptables-save | grep <nodeport>
sudo ss -lntp | grep <nodeport>
curl -s --max-time 3 http://10.10.10.131:<nodeport>/
```

**Done when** — you always start at rung 0, you can name the rung before fixing, and an empty endpoint list sends you to **TS15** rather than to `iptables`.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Produce all five, work the chain each time. | 10 min |
| **2** | Two faults at once — empty endpoints *and* a firewall rule. | 8 min |
| **3** | **Injected.** **F08**, cause unknown. | **5 min** |

**Teardown** — `cka-inject.sh revert`, **remove any firewall rule you added** — check `iptables-save` on both nodes — and delete the namespace.

**See also** — **TS15** is rung 2 in full; **N6** is the NodePort built rather than debugged; **N12** is the Ingress in front.
