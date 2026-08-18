<a id="the-node-that-cannot-read-its-neighbour"></a>
# A stolen kubelet credential reads its own node's secrets and is refused the neighbour's — the boundary the capstone's blast radius stops at

**Artifact** — a two-column table produced by measurement: with a credential in group `system:nodes` named `system:node:<nodeA>`, the list of Secrets it *can* read (exactly those mounted by pods scheduled to `nodeA`) and the list it is *refused* (a Secret mounted only on `nodeB`), each entry an actual apiserver response rather than a prediction, plus the `graph.go` edge that drew the line — cited `file:line` against the source, as the boundary that will hold in [the capstone](26-the-cve-incident.md) even when everything else does not.

**Rests on** — [exercise 1](01-one-verb-one-resource.md) for the difference between `get`-allowed and `get`-refused as read from a 403. This exercise is the attacker's reading of the Node authorizer: [P3 established which edge confines a kubelet](../../phases/03-api-machinery.md#m3-1); here you *stand on the wrong side of it* and measure the reach a node compromise actually buys, which is the number the capstone's postmortem has to state.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Two nodes is the minimum this exercise can be run on at all: the claim is about `nodeA` versus `nodeB`, and a single node cannot make it.

**Setup** — confirm the Node authorizer is in the chain (it is, on a kubeadm cluster), and put a secret-mounting pod on each node so that "its own" and "the neighbour's" are concrete:

```sh
kubectl -n kube-system get pod -l component=kube-apiserver -o yaml | grep authorization-mode   # expect Node,RBAC
CP=$(kubectl get node -l node-role.kubernetes.io/control-plane -o jsonpath='{.items[0].metadata.name}')
WK=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')

kubectl create namespace tenant
kubectl -n tenant create secret generic secret-on-worker --from-literal=k=w
kubectl -n tenant create secret generic secret-on-cp --from-literal=k=c
```

Mount each secret from a pod pinned to one node, so the Node authorizer's graph gains an edge from that node to that secret:

```sh
for pair in "worker $WK secret-on-worker" "cp $CP secret-on-cp"; do set -- $pair
kubectl -n tenant apply -f - <<YAML
apiVersion: v1
kind: Pod
metadata: {name: uses-$1, namespace: tenant}
spec:
  nodeName: $2
  tolerations: [{operator: Exists}]
  containers:
  - name: c
    image: registry.k8s.io/pause:3.9
    volumeMounts: [{name: s, mountPath: /s}]
  volumes: [{name: s, secret: {secretName: $3}}]
YAML
done
kubectl -n tenant get pod -o wide
```

**Read** — `plugin/pkg/auth/authorizer/node/graph.go`. [The reading question](../../phases/10-security.md#m10-1) is which edge encodes "a kubelet may read a Secret only if a pod on its node references it." Find where a `secret` vertex is connected to a `node` vertex through a `pod`:

```sh
ssh zain@10.10.10.125 'grep -n "AddPod\|secretVertexType\|func (g \*Graph)\|nodeVertexType\|hasPathFrom\|SetNodes" ~/src/kubernetes/plugin/pkg/auth/authorizer/node/graph.go | head'
```

**Do — become the node.** Impersonation reaches the same authorizer a stolen kubelet client-cert would; the group is what the Node authorizer keys on:

```sh
asA() { kubectl --as="system:node:$WK" --as-group=system:nodes "$@"; }
```

**Observe — what `nodeA`'s identity reaches:**

```sh
asA -n tenant get secret secret-on-worker -o jsonpath='{.data.k}'; echo    # its own node's — allowed
asA -n tenant get secret secret-on-cp                                       # the neighbour's — refused, read the 403
asA -n tenant get secrets                                                    # cannot list at all
kubectl -n tenant delete pod uses-worker
asA -n tenant get secret secret-on-worker                                    # now refused: the edge is gone with the pod
```

**Expect** — the worker identity reads `secret-on-worker` and is refused `secret-on-cp` with a 403 that says the node is not allowed to access that secret; it cannot `list` secrets at all (the Node authorizer grants no collection reads); and the moment the mounting pod is deleted, the *same* read of `secret-on-worker` becomes a 403 — the permission was the graph edge, and it vanished with the pod. This is the boundary intact: a compromised worker reaches only what its own pods mount.

**The consequence the capstone rests on, and it belongs in the notes as one sentence.** This boundary is real and it holds — *until the attacker is executing inside a pod that is itself `privileged: true` with `hostPID` and host mounts*, at which point the kubelet's own credentials on the node's disk are readable and the graph boundary is irrelevant because the attacker is no longer asking the apiserver politely. That pod is the `chaos-daemon` in [the capstone](26-the-cve-incident.md), and *why the graph boundary stops mattering* is the postmortem's central claim.

**Write down** — the `graph.go` line that adds the secret→node edge, the two-column allowed/refused table with real responses, and the one sentence above. The capstone cites this file:line as "the boundary that did hold, so that the reader sees exactly which boundary did not."

**Teardown** — the tenant namespace and its secrets go; **the topology stays**:

```sh
kubectl delete namespace tenant
```
