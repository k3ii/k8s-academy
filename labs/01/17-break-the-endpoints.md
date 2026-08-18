<a id="break-the-endpoints"></a>
# Chaos drill 1.C2 — an empty endpoint list, diagnosed from describe alone

**Claim** — endpoints are reconciled from pod readiness rather than configured, and you can prove it by deleting one and by breaking one, then diagnose the second case from `kubectl describe` output alone in under two minutes.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. [By hand](../../strands/chaos.md#principle).

**Do**

1. **Delete the EndpointSlice** for the `web` Service and start a clock:

   ```sh
   kubectl delete endpointslice -l kubernetes.io/service-name=web
   kubectl get endpointslices -l kubernetes.io/service-name=web -w
   ```

   Predict first: does it come back, with the same name, and what recreated it?

2. Now the harder case. Change the Service's selector to a label no pod carries — one character is enough:

   ```sh
   kubectl patch svc web -p '{"spec":{"selector":{"app":"wbe"}}}'
   ```

3. **Diagnose it as though you did not do it.** Rules: `kubectl describe` only, no `get -o yaml`, no editor, and no looking at the patch you just ran. Time yourself. The path is `describe svc` → the line that gives it away → `describe pod` → compare.
4. Write the general triage order for "Service returns nothing" as a numbered list, and then test it against **four** causes, restoring between each: the selector typo; a pod that is `Running` but unready; a `targetPort` that names a port the container never declared; and a Service in the wrong namespace.
5. For the `targetPort` case specifically, note where the failure appears — the slice is *populated*, the connection is refused, and no Kubernetes object is unhappy. Say which of the four causes `describe svc` cannot detect.

**Observe**

```sh
kubectl describe svc web              # Endpoints: <none> is the whole tell
kubectl -n kube-system logs -l component=kube-controller-manager --tail=100 | grep -i endpoint
```

**Expect** — the deleted slice is recreated in under a second with a new random suffix, by the endpointslice controller, because nothing about that object is authored — it is derived state, and deleting derived state is a no-op with extra steps. The selector typo shows up as `Endpoints: <none>` on a Service whose pods are all healthy, and the fix is a comparison of two label maps that `describe` gives you on adjacent screens. The `targetPort` case is the one that defeats the triage list, and finding out which of your four causes your own list misses is worth more than the list itself.

**Write down** — your triage order, the four causes with the command that identifies each, and the time you took on step 3. [Module 1.4 asks for the diagnosis from `describe` alone](../../phases/01-operate-shallow.md#m1-4).

**Teardown** — restore the Service's selector and `targetPort`, and confirm the slice repopulates. **The topology stays.**
