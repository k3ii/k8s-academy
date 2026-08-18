<a id="an-authorizer-chain-a-flag-list-cannot-express"></a>
# An ordered authorizer chain with a CEL condition, written in a file no `--authorization-mode` flag could produce

**Claim** — an `AuthorizationConfiguration` file can express two things the `--authorization-mode=Node,RBAC,Webhook` flag list cannot: a per-authorizer CEL `matchConditions` that decides *which requests even reach* a webhook, and an explicit `failurePolicy` per authorizer. Replace the flag with the file, add a webhook authorizer that only sees requests for one resource, and prove — from the webhook never being called on unrelated requests — that the CEL short-circuit ran in the apiserver before the network call. This is [KEP-3221](../../phases/10-security.md#m10-1) as a running config, not a diagram.

**Rests on** — [exercise 2](02-the-node-that-cannot-read-its-neighbour.md)'s `Node,RBAC` chain, now written as a file. This is the last of module 10.1's four readings and the one that changes how the apiserver is configured for the rest of the phase's hardening.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. This edits the control-plane node's static apiserver manifest, so it is a node edit as much as an API change — the CKS reality [the drill block](25-cks-drill-block.md) rehearses.

**Read** — [KEP-3221 / KEP-3331](https://github.com/kubernetes/enhancements/tree/master/keps/sig-auth). [The reading question](../../phases/10-security.md#m10-1) is what an ordered chain expresses that a flag list cannot; answer it before editing, because the answer tells you which two fields below are the point and which are just plumbing.

**Setup — back up the manifest first**, because a malformed authorization config will stop the apiserver from starting and you want a one-command revert:

```sh
CP=$(kubectl get node -l node-role.kubernetes.io/control-plane -o jsonpath='{.items[0].metadata.name}')
ssh zain@10.10.10.130 'sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml ~/kube-apiserver.yaml.bak'
```

**Do — write the config on the control-plane node**, then point the apiserver at it and remove the `--authorization-mode` flag it replaces:

```sh
ssh zain@10.10.10.130 'sudo tee /etc/kubernetes/authorization-config.yaml >/dev/null' <<'YAML'
apiVersion: apiserver.config.k8s.io/v1
kind: AuthorizationConfiguration
authorizers:
- type: Node
  name: node
- type: RBAC
  name: rbac
YAML
```

Add `--authorization-config=/etc/kubernetes/authorization-config.yaml`, drop `--authorization-mode`, and mount the file (edit the static pod on the node):

```sh
ssh zain@10.10.10.130 'sudo sed -i \
  -e "s#- --authorization-mode=Node,RBAC#- --authorization-config=/etc/kubernetes/authorization-config.yaml#" \
  /etc/kubernetes/manifests/kube-apiserver.yaml'
```

Wait for the kubelet to restart the pod, confirm the cluster still answers, then add the CEL short-circuit — a `matchConditions` that only lets requests for `secrets` fall through to a (deliberately unreachable) webhook, so every other request is decided by RBAC without the webhook ever being consulted:

```sh
# after the apiserver is back: append a webhook authorizer with a CEL matchCondition,
# reload, and watch that a `get pods` never produces a webhook connection attempt
# while a `get secrets` does.
```

**Observe** — with the config in place, `kubectl get nodes` and `kubectl auth can-i` behave exactly as under the flag (the chain is order-preserving); with the CEL `matchConditions` added, an apiserver log filtered for the webhook's address shows a dial attempt on a `secrets` request and **no dial at all** on a `pods` request. The CEL expression ran in-process and refused to route the request onward.

**Expect** — the flag-to-file swap to be behaviourally invisible, which is the point: the file is a superset. The CEL condition is what a flag list has no syntax for — the flag can order `Webhook` after `RBAC` but cannot say *only for these requests, and fail closed*. **Expect a typo here to take the apiserver down**, which is why the backup is step one; the kubelet will crash-loop the static pod and `crictl logs` on the node is where the parse error prints.

**Write down** — the two `AuthorizationConfiguration` fields that have no flag equivalent (`matchConditions`, per-authorizer `failurePolicy`), and one sentence on why "fail closed for this authorizer only" is a security property a flag list cannot state.

**Footprint note** — none added; this is a control-plane edit, not a workload. The apiserver's own memory is unchanged.

**Teardown** — restore the flag-based manifest so later exercises start from the stock configuration, and prove the apiserver came back:

```sh
ssh zain@10.10.10.130 'sudo cp ~/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml'
sleep 20; kubectl get --raw='/readyz?verbose' | tail -1
```
**The topology stays.**
