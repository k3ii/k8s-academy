<a id="stomp-the-status"></a>
# Write a lie into status and time the correction

**Claim** — a controller will overwrite a hand-edited `status` within seconds, and you can name which controller did it and what two values it compared to decide.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the `objectmodel` namespace still up.

**Do**

1. Scale `deploy/web` to 3 and wait for it to settle.
2. Predict, in writing: if you set `status.replicas` to `99`, how long until it is corrected, and by what?
3. Edit the status through the subresource — not `kubectl edit`, which will silently drop the field:

   ```sh
   kubectl -n objectmodel get deploy/web --subresource=status -o json \
     | jq '.status.replicas=99 | .status.readyReplicas=99' \
     | kubectl replace --subresource=status -f -
   ```

4. Immediately: `kubectl -n objectmodel get deploy/web -o jsonpath='{.status.replicas}'`, repeatedly. Time the correction.
5. Do it again, but with the deployment controller stopped, so the *absence* is as visible as the presence:

   ```sh
   sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /root/
   ```

   Repeat step 3. Now the lie persists. Put the manifest back and watch the correction land the moment the controller returns. This is [the same directory trick](04-static-pod-blip.md), used as an on/off switch for a controller.
6. Try the same edit against a **Pod's** `status.phase`, and against a **Node's** `status.conditions`. One is corrected by the kubelet on its next sync; the other has a much less pleasant failure mode if you get it wrong, which is why you are doing it on a lab.

**Observe**

```sh
kubectl -n objectmodel get deploy/web -o yaml | grep -A6 'observedGeneration'
kubectl -n objectmodel get events --sort-by=.lastTimestamp | tail
```

**Expect** — correction in single-digit seconds while the controller runs, and never while it does not. `metadata.generation` did **not** change when you wrote status — only spec writes bump it — and `status.observedGeneration` is how the controller decides whether the status it is looking at describes the spec it is looking at. That pair of fields is the level-triggered loop in two integers: the controller does not remember what it did, it compares what it wants with what it sees, every time. Step 5 makes the comparison visible by removing the comparer.

**Write down** — which controller corrected each of the three objects, and the two values it compared. [The checklist](../../phases/01-operate-shallow.md#checklist) asks why deleting a Pod under a Deployment achieves nothing; this is the same answer, arrived at from the other side.

**Teardown** — `kubectl delete ns objectmodel`, and confirm `/etc/kubernetes/manifests/kube-controller-manager.yaml` is back in place before you leave. **The topology stays.**
