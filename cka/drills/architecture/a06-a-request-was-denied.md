<a id="a06"></a>
# A6 — A request was denied: say who, what, and which binding is missing

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / RBAC

> **A 403 from the API server is unusually generous: it names the user, the verb, the resource and usually the namespace.** Read it. Most of the time the message is the whole answer and people reach for `get rolebindings` without having read the sentence in front of them.

> **There is no reverse index.** Nothing answers "which binding would grant this?" — RBAC is purely additive and evaluated forwards, so you work from the subject and search. Knowing that stops you hunting for a command that does not exist.

**Do**

1. Produce a 403 on purpose and **read it word for word**. `User "x" cannot <verb> resource "<r>" in API group "<g>" in the namespace "<ns>"`. Four of the five things you need are in that sentence.
2. Confirm who you actually are, which is often the surprise. `kubectl auth whoami`. A kubeconfig pointing at the wrong context or a token you did not expect accounts for a large share of real 403s.
3. Establish the full picture for that subject in one command: `auth can-i --list --as=<subject>`. This is far faster than reading bindings and it is the command to reach for first.
4. **Then search for the gap.** There is no reverse lookup, so list RoleBindings and ClusterRoleBindings and filter by subject. Decide which of the three fixes applies: the binding is missing; the binding exists but names the wrong subject string; or the binding is right and the Role it points at lacks the verb, the resource, or the right `apiGroups`.
5. Check the API group specifically. A rule with `apiGroups: [""]` does not cover `apps`, and a Deployment is in `apps`. This is the most common "the Role looks right" cause.

**Observe**

```sh
kubectl auth whoami
kubectl auth can-i --list --as=<subject> -n <ns>
kubectl get rolebindings,clusterrolebindings -A -o json \
  | jq -r '.items[] | select(.subjects[]?.name=="<subject>") | "\(.kind) \(.metadata.namespace)/\(.metadata.name) -> \(.roleRef.name)"'
kubectl describe clusterrole <name>
```

**Done when** — you name the subject, the verb, the resource, the API group and the specific missing or wrong object, and your fix is the narrowest one that works rather than a bind to `cluster-admin`.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Produce each of the three causes and read its signature. | 10 min |
| **2** | A cluster with six bindings, one of them nearly right. | 8 min |
| **3** | Cold, clock visible. One 403, no context. | 5 min |

**Teardown** — remove anything you bound, including cluster-scoped objects.

**See also** — **A1** for the proof technique, **A3** for the scope rule that explains a surprising number of these.
