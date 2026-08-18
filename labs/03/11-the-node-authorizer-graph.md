<a id="the-node-authorizer-graph"></a>
# A kubelet may read exactly the secrets its own pods use

**Claim** — with `Node` in the authorization chain, a credential in group `system:nodes` named `system:node:<name>` can read a Secret **only** if some pod scheduled to `<name>` references it, and the moment you delete that pod the same read is refused. The permission is not a rule; it is a path in a graph.

**Rests on** — [the two-identity token file](05-hand-start-an-apiserver.md), and [the `O=system:nodes` row](01-hand-wire-the-control-plane.md) of your hop table — this is what that group was actually for. [Module 3.1's last reading question](../../phases/03-api-machinery.md#m3-1) is the one being answered.

**Topology** — **none.** `forge` and [the running apiserver](05-hand-start-an-apiserver.md). No kubelet exists and none is needed: the authorizer reasons about `Node` and `Pod` *objects*, not about processes.

**Setup**

Add a third identity to `tokens.csv` and restart with the Node authorizer in front of RBAC:

```sh
printf 's3cr3t-kubelet,system:node:nodeA,1003,"system:nodes"\n' >> ~/apiserver/tokens.csv
kubectl config set-credentials kubeletA --token=s3cr3t-kubelet
kubectl config set-context kubeletA --cluster=forge --user=kubeletA
```

Restart the apiserver with `--authorization-mode=Node,RBAC` in place of `--authorization-mode=RBAC`.

**Do**

1. As `admin`, build the graph's raw material — two Nodes, two Secrets, one Pod:

   ```sh
   kubectl --context=admin create -f - <<'YAML'
   apiVersion: v1
   kind: Node
   metadata: {name: nodeA}
   ---
   apiVersion: v1
   kind: Node
   metadata: {name: nodeB}
   ---
   apiVersion: v1
   kind: Secret
   metadata: {name: mine, namespace: default}
   stringData: {k: v}
   ---
   apiVersion: v1
   kind: Secret
   metadata: {name: theirs, namespace: default}
   stringData: {k: v}
   YAML
   ```

2. Create a Pod **already bound to `nodeA`** — there is no scheduler here, so set `spec.nodeName` yourself — that mounts `mine` and not `theirs`:

   ```sh
   kubectl --context=admin create -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata: {name: onA, namespace: default}
   spec:
     nodeName: nodeA
     containers:
       - name: c
         image: busybox
         volumeMounts: [{name: s, mountPath: /s}]
     volumes:
       - name: s
         secret: {secretName: mine}
   YAML
   ```

3. Ask the three questions, as the kubelet identity:

   ```sh
   kubectl --context=kubeletA get secret mine   -n default
   kubectl --context=kubeletA get secret theirs -n default
   kubectl --context=kubeletA get node nodeB
   ```

4. Delete the pod and immediately ask the first question again.

5. Read `plugin/pkg/auth/authorizer/node/graph.go` and `node_authorizer.go`, and answer: **which object types are vertices, which relationships are edges, and what triggers an edge being added or removed?** Then find the check that limits how far the traversal will walk — it exists, it has a constant, and the reason it exists is a denial-of-service argument you should be able to state.

**Observe**

```sh
jq -r 'select(.user.username=="system:node:nodeA")
       | [.verb,.objectRef.resource,.objectRef.name,.responseStatus.code,
          .annotations["authorization.k8s.io/decision"],
          .annotations["authorization.k8s.io/reason"]] | @tsv' /tmp/audit.log
```

**Expect** — `mine` is readable, `theirs` is `403`, and `nodeB` is `403`. After the pod is deleted, `mine` becomes `403` too — **the permission was never granted to the identity, it was derived from a relationship that no longer exists.** The audit reason names the Node authorizer, not an RBAC rule, which is how you tell which authorizer in the chain answered.

The timing is the part worth watching: the graph is maintained by informers, so the revocation after the delete is *eventually* consistent — a retry within a second or two may still succeed. That is not a bug and it is worth writing down as one of the few places in the apiserver where an authorization answer is a function of a cache rather than of the request.

If every read succeeds including `theirs`, `Node` is not actually in your `--authorization-mode` — RBAC answered first with an allow, and an allow from any authorizer in the chain ends it. Chain order is a real property and this is the cheapest way to be wrong about it once.

**Write down** — the four-row result table, the vertex and edge types from `graph.go`, and the one-sentence answer to *"why may a kubelet read only its own node's secrets?"* — which [the checklist wants as a falsifiable claim](../../phases/03-api-machinery.md#checklist) with the source citation attached.

**Teardown** — `kubectl --context=admin delete pod onA --force --grace-period=0` (nothing is running it, so a graceful delete will hang), then delete both Secrets and both Nodes. Leave the third token in `tokens.csv`. **The apiserver and etcd stay up. No topology is up.**
