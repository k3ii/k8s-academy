<a id="endpointslice-drains"></a>
# Watch a readiness probe reach all the way to an endpoint list

**Claim** — flipping a single readiness endpoint removes that pod's address from the Service's EndpointSlice within seconds, with no configuration change anywhere, and you can name every hop between the two.

**Rests on** — [the readiness switch](09-probes-three-kinds.md), which this exercise reuses rather than rebuilds.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Scale `deploy/web` to 4 behind a ClusterIP Service, and start two watches side by side:

   ```sh
   kubectl get pods -o wide -w
   kubectl get endpointslices -l kubernetes.io/service-name=web -o yaml -w
   ```

2. Fail readiness on exactly one pod. Time the gap between the probe failing (visible in `describe`) and the address leaving the slice.
3. Read the slice while the pod is unready — the address does not vanish; it moves. Find where:

   ```sh
   kubectl get endpointslices -l kubernetes.io/service-name=web \
     -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}{"\t"}{.conditions}{"\n"}{end}'
   ```

   Three condition booleans, not one. Say what each is for and which one `kube-proxy` reads.

4. Restore readiness and watch it return. Then scale to 8 and count the slices — there is a size limit and crossing it is the entire reason EndpointSlice replaced Endpoints.
5. Compare against the legacy object: `kubectl get endpoints web -o yaml`. Same information, one object, no cap.
6. Now delete a pod (do not fail it) and watch the ordering: does the address leave the slice before or after the container dies? Do it with a `preStop` sleep of 20 seconds to make the window wide enough to see.

**Expect** — removal within a couple of seconds of the probe's `failureThreshold` being met, driven by the **endpointslice controller** watching pod status, not by anything you configured on the Service. The hop chain is: probe fails → kubelet writes `Ready=False` into the pod's status → controller re-lists pods matching the selector → slice updated → `kube-proxy` on every node reprograms. Step 6 shows the removal starts *before* the container stops, and the gap is not zero — the race between endpoint removal and connection draining is the reason `preStop` hooks exist, and it is why a rolling update can drop requests even with perfect probes.

**Write down** — one paragraph tracing readiness to endpoint, naming each hop and its actor. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for exactly this paragraph.

**Teardown** — scale back to 3, restore readiness. **The topology stays.**
