<a id="break-the-endpoints"></a>
# Chaos drill 1.C2 — an empty endpoint list, diagnosed from describe alone

**Claim** — endpoints are reconciled from pod readiness. They are not configured. You can prove this by deleting one endpoint list and by breaking another. You can then diagnose the second case from `kubectl describe` output alone, in less than two minutes.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Do this drill [by hand](../../strands/chaos.md#principle).

**Do**

1. **Delete the EndpointSlice** for the `web` Service, and start a clock:

   ```sh
   kubectl delete endpointslice -l kubernetes.io/service-name=web
   kubectl get endpointslices -l kubernetes.io/service-name=web -w
   ```

   Predict the outcome first. Does the slice come back? Does it come back with the same name? What recreated it?

2. Now take the harder case. Change the selector of the Service to a label that no pod carries. One character is enough:

   ```sh
   kubectl patch svc web -p '{"spec":{"selector":{"app":"wbe"}}}'
   ```

3. **Diagnose the break as though you did not cause it.** The rules are strict. Use `kubectl describe` only. Do not use `get -o yaml`. Do not use an editor. Do not look at the patch that you just ran. Time yourself. The path runs like this: `describe svc`, then the line that gives it away, then `describe pod`, then a comparison.
4. Write the general triage order for "Service returns nothing" as a numbered list. Then test the list against **four** causes, and restore the state between each one. The four causes are: the selector typo; a pod that is `Running` but unready; a `targetPort` that names a port which the container never declared; and a Service in the wrong namespace.
5. Look closely at the `targetPort` case. Note where the failure appears. The slice is *populated*, the connection is refused, and no Kubernetes object is unhappy. Then say which of the four causes `describe svc` cannot detect.

**Observe**

```sh
kubectl describe svc web              # Endpoints: <none> is the whole tell
kubectl -n kube-system logs -l component=kube-controller-manager --tail=100 | grep -i endpoint
```

**Expect** — the endpointslice controller recreates the deleted slice in less than one second, with a new random suffix. Nothing about that object is authored. It is derived state, and deleting derived state is a no-op with extra steps. The selector typo shows up as `Endpoints: <none>` on a Service whose pods are all healthy. The fix is a comparison of two label maps, and `describe` gives you both on adjacent screens. The `targetPort` case is the one that defeats the triage list. Finding out which of the four causes your own list misses is worth more than the list itself.

**Write down** — your triage order, the four causes with the command that identifies each one, and the time that you took on step 3. [Module 1.4 asks for the diagnosis from `describe` alone](../../phases/01-operate-shallow.md#m1-4).

**Teardown** — restore the selector and the `targetPort` of the Service. Confirm that the slice repopulates. **The topology stays.**
