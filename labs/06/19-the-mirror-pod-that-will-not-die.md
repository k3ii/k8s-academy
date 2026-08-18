<a id="the-mirror-pod-that-will-not-die"></a>
# Delete a pod through the API and watch it come back with no controller anywhere

**Claim** — the kubelet accepts pods from three sources, and one of them does not involve the API server at all: a file on disk produces a running container plus a read-only *mirror* in the API, so deleting the API object cannot remove the container and the object returns.

**Rests on** — [the sub-manager inventory](01-the-sub-managers-named.md), where the three sources were named from the design document. This is where the file source becomes a file.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The worker `.131` gets the static pod; the control plane already has four, which is the comparison.

**Read** — `pkg/kubelet/config/file.go` and the source-merging in the same package (item 16): which directory is watched, how often it is re-read, and how the three sources are merged into one stream of pod updates. Then answer [module 6.5's question](../../phases/06-kubelet-node.md#m6-5): what makes a mirror pod different from a pod the API server owns?

**Do**

1. Find the watched directory rather than assuming it:

   ```sh
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" | jq '.kubeletconfig.staticPodPath'
   ```

2. Drop a static pod into it:

   ```sh
   ssh zain@10.10.10.131 'sudo tee /etc/kubernetes/manifests/hello-static.yaml >/dev/null <<EOF2
   apiVersion: v1
   kind: Pod
   metadata:
     name: hello-static
     namespace: default
   spec:
     containers:
     - name: c
       image: registry.k8s.io/pause:3.10
       resources: {requests: {memory: 16Mi}, limits: {memory: 32Mi}}
   EOF2'
   ```

3. Watch it appear, and look at what appeared:

   ```sh
   kubectl get pod hello-static-pair-worker -o yaml | grep -A6 -e ownerReferences -e 'kubernetes.io/config'
   kubectl get pod hello-static-pair-worker -o jsonpath='{.spec.nodeName}{"\t"}{.metadata.annotations}{"\n"}'
   ```

4. Try to kill it three ways, in order, recording what happens each time:

   ```sh
   kubectl delete pod hello-static-pair-worker
   sleep 15; kubectl get pod hello-static-pair-worker
   kubectl patch pod hello-static-pair-worker --type=merge -p '{"spec":{"containers":[{"name":"c","image":"busybox:1.36"}]}}'
   ssh zain@10.10.10.131 'sudo crictl ps | grep -e hello -e NAME'
   ```

5. Kill it the only way that works: `ssh zain@10.10.10.131 'sudo rm /etc/kubernetes/manifests/hello-static.yaml'`.

6. Compare with the control plane's own static pods:

   ```sh
   ssh zain@10.10.10.130 'ls /etc/kubernetes/manifests/'
   kubectl -n kube-system get pods -o custom-columns=NAME:.metadata.name,OWNER:'.metadata.ownerReferences[*].kind' | head -20
   ```

**Expect** — the mirror to carry an owner reference to the **Node**, a `kubernetes.io/config.source: file` annotation and a mirror-pod hash annotation. Expect the `DELETE` to succeed — the API server has no reason to refuse it — and the pod to reappear within seconds with a **new UID**. Nothing recreated it; the kubelet simply re-published a mirror for a container that never stopped, which is why `crictl ps` shows the same container ID across the whole episode.

Expect the patch to be accepted by the API server and to change nothing at all on the node. **The mirror is a report, not a spec**, and this is the one place in Kubernetes where writing to `spec` is genuinely inert.

Expect the control plane's four static pods to have exactly the same shape — which is the real payoff: `kube-apiserver` is a static pod, so the mechanism you just poked is what makes it possible to start a control plane with no control plane running. [P3's hand-wiring](../../phases/03-api-machinery.md#m3-1) and this file are the same bootstrap problem, solved.

**Write down** — the three deletion attempts with their outcomes, the mirror's annotations and owner reference, and one sentence on why `kubeadm` uses this source for the control plane rather than a DaemonSet.

**Footprint note** — one `pause` pod at 32Mi on the worker. Negligible, but **remove the manifest file in step 5**: a forgotten static pod survives every `kubectl delete`, outlives the namespace, and confuses the next exercise's node accounting because nothing in the API can remove it.

**Teardown** — the `rm` in step 5 is the teardown; confirm with `kubectl get pods | grep hello-static` returning nothing. **The topology stays.**
