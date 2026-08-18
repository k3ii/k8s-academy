<a id="csi-driver-in-cluster"></a>
# Deploy the driver with its sidecars and provision a volume with it

**Artifact** — a pod running on a PVC dynamically provisioned by **your** driver, with the Controller service as a Deployment and the Node service as a DaemonSet. [Stage 2](../../strands/build-mechanics.md#two-stages).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). Bring it back up if [stage 1](12-csi-driver-sanity.md) ran after a teardown; otherwise it is still there from [the finalizer deadlock](11-finalizer-deadlock.md).

**Do**

1. Ship it: a static binary in a [`scratch` image](../../strands/build-mechanics.md#base-image), built on `forge`, pushed to [`forge`'s registry](../../strands/build-mechanics.md#registry) and pulled by the nodes.
2. Deploy the **Controller** service as a Deployment beside the `csi-provisioner` sidecar; deploy the **Node** service as a DaemonSet beside `node-driver-registrar`.
3. Give each half [its own ServiceAccount and a hand-written ClusterRole](../../strands/build-mechanics.md#identity). The two need genuinely different permissions — this is the artifact where separate identities are least arbitrary, so do not share one.
4. Give each [a memory request taken from `kubectl top pod`](../../strands/build-mechanics.md#sizing).
5. The DaemonSet needs `hostPath` access to `/var/lib/kubelet/plugins` and **`mountPropagation: Bidirectional`**. Deploy it *without* the propagation setting first and find out what breaks, then add it.
6. Create a StorageClass naming your provisioner, a PVC against it, and a pod. Watch `CreateVolume` arrive in your own logs.

**Observe**

```sh
kubectl logs -l app=toy-csi-controller -c toy-csi -f
kubectl logs -l app=toy-csi-node -c toy-csi -f
kubectl get csidrivers,csinodes -o wide
kubectl get volumeattachment -o wide
```

**Expect** — the sidecars are Kubernetes controllers translating Kubernetes objects into the RPCs you implemented in [stage 1](12-csi-driver-sanity.md); your binary never watches the API. That separation is the architectural idea of the whole interface. A `scratch` image has no shell, so `kubectl exec` fails and the way in is `kubectl debug --target=`.

**Write down** — what broke in step 5 without `mountPropagation: Bidirectional`, and why, in terms of mount namespaces. [Checklist item](../../phases/08-storage.md#checklist), and the best answer to it is the one you got the hard way.

**Teardown** — leave the driver deployed. [8.C3](16-chaos-detach-failure.md) needs it, and [the capstone](../../phases/08-storage.md#capstone) needs one of its two traces to run through your own `CreateVolume`.
