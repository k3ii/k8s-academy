<a id="stomp-the-status"></a>
# Write a lie into status and time the correction

**Claim** — a controller overwrites a hand-edited `status` within seconds. You can name the controller that did it, and you can name the two values that it compared to decide.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the `objectmodel` namespace still up.

**Do**

1. Scale `deploy/web` to 3, and wait for it to settle.
2. Predict two things in writing. If you set `status.replicas` to `99`, how long until something corrects it? What corrects it?
3. Edit the status through the subresource. Do not use `kubectl edit`, because it silently drops the field:

   ```sh
   kubectl -n objectmodel get deploy/web --subresource=status -o json \
     | jq '.status.replicas=99 | .status.readyReplicas=99' \
     | kubectl replace --subresource=status -f -
   ```

4. Immediately run `kubectl -n objectmodel get deploy/web -o jsonpath='{.status.replicas}'`, and repeat the command. Time the correction.
5. Do it again, but stop the deployment controller first. The *absence* of the controller is then as visible as its presence:

   ```sh
   sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /root/
   ```

   Repeat step 3. The lie now persists. Put the manifest back, and watch the correction land the moment the controller returns. This is [the same directory trick](04-static-pod-blip.md), used as an on/off switch for a controller.
6. Try the same edit against the `status.phase` of a **Pod**, and against the `status.conditions` of a **Node**. The kubelet corrects one of them on its next sync. The other one has a much less pleasant failure mode if you get it wrong, and that is why you do this on a lab.

**Observe**

```sh
kubectl -n objectmodel get deploy/web -o yaml | grep -A6 'observedGeneration'
kubectl -n objectmodel get events --sort-by=.lastTimestamp | tail
```

**Expect** — the correction takes single-digit seconds while the controller runs. It never happens while the controller is stopped. Note also what did not change. `metadata.generation` did **not** move when you wrote status, because only spec writes bump it. The controller uses `status.observedGeneration` to decide one thing: whether the status that it looks at describes the spec that it looks at. That pair of fields is the level-triggered loop, in two integers. The controller does not remember what it did. It compares what it wants with what it sees, every time. Step 5 makes the comparison visible, because it removes the comparer.

**Write down** — which controller corrected each of the three objects, and the two values that it compared. [The checklist](../../phases/01-operate-shallow.md#checklist) asks why deleting a Pod under a Deployment achieves nothing. This is the same answer, reached from the other side.

**Teardown** — run `kubectl delete ns objectmodel`. Confirm that `/etc/kubernetes/manifests/kube-controller-manager.yaml` is back in place before you leave. **The topology stays.**
