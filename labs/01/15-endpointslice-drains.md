<a id="endpointslice-drains"></a>
# Watch a readiness probe reach all the way to an endpoint list

**Claim** — you flip a single readiness endpoint. Within seconds, that pod's address leaves the EndpointSlice of the Service. Nothing changes in any configuration. You can also name every hop between the probe and the endpoint list.

**Rests on** — [the readiness switch](09-probes-three-kinds.md). This exercise reuses that switch, and does not rebuild it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Scale `deploy/web` to 4 behind a ClusterIP Service. Start two watches, side by side:

   ```sh
   kubectl get pods -o wide -w
   kubectl get endpointslices -l kubernetes.io/service-name=web -o yaml -w
   ```

2. Fail readiness on exactly one pod. Then time one gap: the time between the probe failure, which you see in `describe`, and the departure of the address from the slice.
3. Read the slice while the pod is unready. The address does not vanish. It moves. Find where it moved to:

   ```sh
   kubectl get endpointslices -l kubernetes.io/service-name=web \
     -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}{"\t"}{.conditions}{"\n"}{end}'
   ```

   You find three condition booleans, and not one. Say what each boolean is for, and say which one `kube-proxy` reads.

4. Restore readiness, and watch the address return. Then scale to 8, and count the slices. There is a size limit, and crossing it is the entire reason why EndpointSlice replaced Endpoints.
5. Compare the slice against the legacy object: `kubectl get endpoints web -o yaml`. It holds the same information, in one object, with no cap.
6. Now delete a pod, and do not fail it. Watch the ordering. Does the address leave the slice before the container dies, or after? Use a `preStop` sleep of 20 seconds, so that the window is wide enough to see.

**Expect** — the address is removed within a few seconds of the `failureThreshold` of the probe being met. The **endpointslice controller** drives the removal, by watching pod status. Nothing that you configured on the Service drives it. The chain of hops runs as follows: the probe fails, then the kubelet writes `Ready=False` into the status of the pod, then the controller re-lists the pods that match the selector, then the slice is updated, then `kube-proxy` on every node reprograms. Step 6 shows that the removal starts *before* the container stops, and that the gap is not zero. That race between endpoint removal and connection draining is the reason why `preStop` hooks exist. It is also why a rolling update can drop requests even with perfect probes.

**Write down** — one paragraph that traces readiness to endpoint. Name each hop and its actor. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for exactly this paragraph.

**Teardown** — scale back to 3, and restore readiness. **The topology stays.**
