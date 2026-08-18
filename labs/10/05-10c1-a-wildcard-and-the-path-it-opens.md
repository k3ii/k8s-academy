<a id="10c1-a-wildcard-and-the-path-it-opens"></a>
# 10.C1 — a `*` on rolebindings, and the self-promotion RBAC normally forbids

**Claim** — drill [10.C1](../../phases/10-security.md#chaos): a ServiceAccount whose Role grants `verbs: ["*"]` on `rolebindings` can bind *itself* to the built-in `admin` ClusterRole and thereby gain every verb on every resource in its namespace — a promotion the apiserver **refuses** the instant the wildcard is narrowed to the explicit verbs, because RBAC's escalation-prevention check keys on whether you hold `bind`, and `*` silently included it. The path opened and closed is the same object created twice, once accepted and once `403`.

**Rests on** — [exercise 1](01-one-verb-one-resource.md)'s literal-string matcher (the `*` that stood in for a verb list) and [exercise 4](04-an-authorizer-chain-a-flag-list-cannot-express.md)'s chain. This is the first of the phase's five [rehearsal drills](../../phases/10-security.md#chaos), each a mechanism [the capstone](26-the-cve-incident.md) will need without it being new.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — the escalation-prevention path in `plugin/pkg/auth/authorizer/rbac`. The check that a `create rolebindings` request cannot grant permissions the requester lacks lives in the RBAC admission side; find where `bind` is the verb that exempts it:

```sh
ssh zain@10.10.10.125 'grep -rn "escalat\|ConfirmNoEscalation\|\"bind\"\|BindVerb" ~/src/kubernetes/plugin/pkg/auth/authorizer/rbac/ ~/src/kubernetes/pkg/registry/rbac/ 2>/dev/null | head'
```

**Do — grant the wildcard, and take the path:**

```sh
kubectl create namespace esc
kubectl -n esc create serviceaccount climber
kubectl apply -f - <<'YAML'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {namespace: esc, name: rolebinding-star}
rules:
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["rolebindings"]
  verbs: ["*"]
YAML
kubectl -n esc create rolebinding climber-star --role=rolebinding-star --serviceaccount=esc:climber

# as the SA, bind yourself to admin — the promotion:
kubectl -n esc --as=system:serviceaccount:esc:climber create rolebinding pwned \
  --clusterrole=admin --serviceaccount=esc:climber
# prove the new reach:
kubectl -n esc --as=system:serviceaccount:esc:climber auth can-i get secrets
kubectl -n esc --as=system:serviceaccount:esc:climber auth can-i delete deployments
```

**Do — close it, and watch the same create refused:**

```sh
kubectl -n esc delete rolebinding pwned
kubectl -n esc patch role rolebinding-star --type=json \
  -p='[{"op":"replace","path":"/rules/0/verbs","value":["get","list","create","delete"]}]'
# now the wildcard is gone but every *explicit* verb the climber had is still present;
# the escalation is still refused, because "bind" was never in the explicit list:
kubectl -n esc --as=system:serviceaccount:esc:climber create rolebinding pwned2 \
  --clusterrole=admin --serviceaccount=esc:climber
```

**Observe** — the first `create rolebinding pwned` succeeds and `can-i get secrets` / `delete deployments` both flip to `yes`; after narrowing the verbs to `get,list,create,delete` — which still includes `create` on rolebindings — the second attempt is refused with a message about not being permitted to grant privileges the user does not hold. The requester still has `create`; what it lost was `bind`, and `bind` is the one verb the escalation check treats as consent to hand out a role you do not yourself own.

**Expect** — the promotion to work under `*` and fail under an explicit list that is *larger than what most people would write by hand* yet still omits `bind`. **The lesson is that `*` is not "all the verbs I would have listed" — it is a strictly larger set that includes the ones RBAC specifically gates.** The escalation was never a bug; it was the wildcard being taken at its word.

**Write down** — the escalation-check line, the two `can-i` answers before and after, and one sentence: which verb the wildcard included that no reasonable explicit list would have. That sentence is why [the capstone's](26-the-cve-incident.md) blast-radius reasoning treats an over-broad Role as equivalent to the permission it could grant itself.

**Teardown** — the whole namespace, which takes the Role, both bindings and the SA with it; **the topology stays**:

```sh
kubectl delete namespace esc
```
