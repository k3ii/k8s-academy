<a id="n05"></a>
# N5 — ClusterIP and its endpoints: break the selector, watch the backends empty

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Service types · endpoints

> **A Service is a selector and a port map, and nothing else.** This drill makes that concrete by building one that works, breaking exactly one field, and watching the backend list go empty while the Service itself stays perfectly healthy. The Service never reports an error — that is the whole lesson.

**Do**

1. Deployment of two replicas, labelled `app=web`, container port **named** `http`.
2. `ClusterIP` Service selecting `app=web`, with `targetPort: http` — the **name**, not the number. Prove traffic lands on both pods.
3. Now break the selector: change it to `app=weeb`. Re-read the backends. Note that `kubectl get svc` is unchanged, the ClusterIP is unchanged, and `curl` from a client pod now hangs or refuses rather than 404s.
4. Fix it, confirm the backends repopulate, then break it once more in a *different* way — rename the container port — and see the same empty list from a different cause.

**Observe**

```sh
kubectl get endpointslices -l kubernetes.io/service-name=web -o wide
kubectl describe svc web | sed -n '/Selector/,/Endpoints/p'
kubectl get pods --show-labels
kubectl run c --rm -it --image=nicolaka/netshoot --restart=Never -- curl -m 3 -sv http://web
```

> On this lab's v1.37 cluster, `kubectl get endpoints` prints `v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`. **The command still works, and the exam's v1.35 cluster behaves the same way**, so take the warning as noise rather than as a symptom. `describe svc` still prints an `Endpoints:` line either way.

**Done when** — you can state, without looking, that an empty backend list means *the Service matched no pod*, and name the four independent fields that can cause it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean namespace. Build it, break the selector, fix it. | 10 min |
| **2** | A namespace with three other Services already in it. Same work, more noise. | 8 min |
| **3** | Cold, no notes, clock visible. Build the whole thing from scratch and break it twice. | 5 min |

**Teardown** — delete the namespace.

**See also** — **[TS15](../troubleshooting/ts15-service-with-no-endpoints.md) is this same object from the other side**: there the breakage is already in place and unlabelled, and the task is attribution rather than construction. The pair is written together deliberately; [the plan](../../plan.md#what-does-not-run) schedules only one of the two.
