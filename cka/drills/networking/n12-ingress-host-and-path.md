<a id="n12"></a>
# N12 — Ingress with host and path rules, against a real controller

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Ingress

> **An Ingress object with no controller behind it is inert, and it will not tell you so.** It is accepted, it shows in `get ingress`, and its `ADDRESS` column stays empty forever. The exam cluster has a controller; recognising the empty `ADDRESS` as "nothing is reconciling this" is what transfers.

> **Prerequisite this cluster does not yet meet.** There is **no IngressClass and no ingress controller installed** — confirmed by `kubectl get ingressclass` returning nothing. **B4** installs metrics-server, a *Gateway* controller and MetalLB; it does **not** install an Ingress one. Install `ingress-nginx` once, as a fixture, before pass 1 — it takes a few minutes and is not part of the ten. Give it a `LoadBalancer` Service so it takes an address from the MetalLB pool B4 created.

**Do**

1. Two Deployments with two Services, `a` and `b`, serving distinguishable responses.
2. One Ingress, **path**-based: `/a` → `a`, `/b` → `b`. Curl both through the controller's address and confirm you reach different backends.
3. **`pathType` is graded and is not optional.** Write all three and know the difference: `Exact` matches the string; `Prefix` matches on *path segments*, so `/a` matches `/a/x` but not `/ax`; `ImplementationSpecific` hands the decision to the controller. Prove the `/ax` case rather than taking the sentence on trust.
4. Add a **host** rule — two hosts to two backends — and test with `curl -H 'Host: …'` rather than touching DNS. A rule with a host only matches requests carrying that host; the same Ingress can have both host-scoped and catch-all rules.
5. **`ingressClassName` is how the object finds its controller.** Set it explicitly. Then remove it and see what happens: with a default IngressClass it still works, without one it is ignored silently. That silence is the failure mode.
6. Add a `defaultBackend` for unmatched requests, and check the rewrite annotation your controller uses — annotations are controller-specific and the exam will have told you which controller is installed.

**Observe**

```sh
kubectl get ingressclass
kubectl get ingress -o wide            # ADDRESS empty == nothing reconciling
kubectl describe ingress web | sed -n '/Rules/,$p'
curl -s -H 'Host: a.example.com' http://<ingress-address>/
curl -s http://<ingress-address>/ax    # Prefix /a must NOT match this
kubectl -n ingress-nginx logs -l app.kubernetes.io/component=controller --tail=20
```

**Done when** — both paths and both hosts route correctly, and you can state from memory what an empty `ADDRESS` and a missing `ingressClassName` each mean.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean, controller already installed. Paths, then hosts. | 10 min |
| **2** | An existing Ingress that already claims `/`. Add yours without breaking it. | 8 min |
| **3** | Cold, no notes. Two hosts, two backends, correct `pathType`. | 5 min |

**Teardown** — delete the namespace. Leave the controller; it is a fixture, like MetalLB.

**See also** — **N13** is the Gateway API answer to the same problem and the direction the project is moving. **N7** is the address this controller sits on.
