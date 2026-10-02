<a id="n13"></a>
# N13 — A minimal Gateway and one HTTPRoute

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Gateway API

> **Gateway API is four objects where Ingress was one, and the four are owned by different people on purpose.** `GatewayClass` is the installation, `Gateway` is the listener, `HTTPRoute` is the application's routing, and the Service is the backend. Nearly every failure is an *attachment* failure between two of them, and the status conditions say which — if you read them.

> **Depends on B4**, which installs the Gateway API CRDs and a controller. This drill is why B4 runs on the first weeknight of week 2. Note that the CRDs are **not** part of the controller's chart; a controller installed without them crash-loops in a way that reads like a controller bug.

**Do**

1. Find the `GatewayClass` the controller installed and read its `controllerName`. A `Gateway` naming a class whose controller is not running sits `Accepted` and never `Programmed`, forever, with no event to explain it.
2. Write the `Gateway`: one HTTP listener on port 80. Watch it get an address — on this cluster, out of the MetalLB pool B4 configured.
3. Write the `HTTPRoute`: a `parentRefs` entry pointing at the Gateway, a hostname, one path rule, one `backendRefs` Service. Curl it.
4. Break the attachment three ways and read each status: a `parentRefs` naming a Gateway that does not exist; a `backendRefs` naming a Service that does not exist; and a listener whose `allowedRoutes` does not permit the route's namespace.
5. **Cross-namespace is deliberately hard.** A route attaching to a Gateway in another namespace needs a `ReferenceGrant` in the *target* namespace. This is the headline difference from Ingress — the gateway owner must opt in — and it is exactly what a scenario question tests.

**Observe**

```sh
kubectl get gatewayclass
kubectl get gateway -o wide
kubectl describe gateway <name> | sed -n '/Status/,$p'
kubectl describe httproute <name> | sed -n '/Status/,$p'
curl -H 'Host: <hostname>' http://<gateway-address>/
```

**Done when** — the Gateway is `Programmed=True`, the HTTPRoute is `Accepted=True` and `ResolvedRefs=True`, curl returns the backend, and you can name which of the two objects' conditions to read for each of the three breakages.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build all four objects with the docs open. | 10 min |
| **2** | A namespace with an existing Gateway you must attach to rather than replace. | 8 min |
| **3** | Cold, no notes, clock visible. All four from memory, including `parentRefs`. | 5 min |

**Teardown** — delete the HTTPRoute and the Gateway; **leave the GatewayClass and the controller**, which are B4's fixtures.

**See also** — **N12** is the same job with Ingress, and running both back to back is the fastest way to see what Gateway API was for. **N7** is the LoadBalancer address this Gateway gets.
