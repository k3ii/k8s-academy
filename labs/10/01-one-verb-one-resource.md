<a id="one-verb-one-resource"></a>
# A Role that grants one verb on one resource, and the three requests it refuses

**Claim** — a `Role` whose only rule is `verbs: [get]`, `resources: [pods]` lets a ServiceAccount `get` a pod by name and refuses, with a 403 whose message names the missing verb, all three of: `list pods`, `get pods/log`, and `get secrets`. A `*` in any of the three rule fields would have permitted the corresponding request, so each wildcard you have ever written was a decision to widen, not a default — and [`rbac.go`'s](../../phases/10-security.md#m10-1) matcher is where that decision is read rather than asserted.

**Rests on** — nothing in this phase; it is the opener. The RBAC objects are the ones [the CKA drill](../08/20-cka-drill-block.md) treats as a speed task, read here for the first time as *attack surface* — the question is not "how do I grant access" but "what does this grant that I did not mean to."

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **provisioned here and held for the whole phase.** Every live-cluster exercise from here to [the capstone](26-the-cve-incident.md) uses it; the capstone is what destroys it.

**Setup** — bring the topology up [the standard way](../../strands/lab-topologies.md#provision), and clone `k/k` [blobless](../../strands/source-archaeology.md#clone) on [`forge`](../../strands/lab-topologies.md#build-guest) for the reading, if it is not already there from an earlier phase:

```sh
ssh hopper
cd factory && git pull
just tofu labs apply -var 'topology=pair'
just gate 130 && just gate 131
just play
```

```sh
ssh zain@10.10.10.125 'test -d ~/src/kubernetes || git clone --filter=blob:none https://github.com/kubernetes/kubernetes ~/src/kubernetes'
```

**Read** — `plugin/pkg/auth/authorizer/rbac/rbac.go`, the function that decides a single request against a single rule. [The reading question](../../phases/10-security.md#m10-1) asks which function matches a request and what a `*` widens; answer it from the source before you write a rule, so that the rule you write is a prediction of what that function will do:

```sh
ssh zain@10.10.10.125 'grep -n "func.*VisitRulesFor\|func RuleAllows\|func verbMatches\|func resourceMatches\|rbacv1helpers" ~/src/kubernetes/plugin/pkg/auth/authorizer/rbac/rbac.go'
```

**Do** — create the ServiceAccount and the deliberately narrow Role, then a pod for it to name:

```sh
kubectl create namespace probe
kubectl -n probe create serviceaccount reader
kubectl -n probe run target --image=registry.k8s.io/pause:3.9

kubectl apply -f - <<'YAML'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {namespace: probe, name: one-verb}
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get"]
YAML
kubectl -n probe create rolebinding reader-one-verb --role=one-verb --serviceaccount=probe:reader
```

**Observe** — ask the apiserver each question *as the ServiceAccount*, so the answer comes from the authorizer and not from your own admin token. `kubectl auth can-i` reads the same code path the request would:

```sh
alias asreader='kubectl -n probe --as=system:serviceaccount:probe:reader'
asreader auth can-i get pods
asreader auth can-i list pods
asreader auth can-i get pods --subresource=log
asreader auth can-i get secrets
asreader get pod target -o name          # the one that works
asreader get pods                        # list — refused, and read the message
asreader logs target                     # pods/log — refused
```

**Expect** — `yes` for the first, `no` for the next three, and the four `can-i` answers matched by the four real requests. Read the 403 body on `asreader get pods`: it names the group, resource and verb that had no matching rule, which is the same tuple `rbac.go`'s matcher compared and failed. **`list` is refused even though `get` is granted** — the verb strings are compared literally, `get` does not imply `list`, and a rule that meant "read pods" needed both. **`pods/log` is a separate resource string** (`pods/log`, not `pods`), which is why a `get pods` grant does not carry it — the single most common real-world RBAC surprise, and it is a string comparison, not a policy.

**Write down** — the matcher function name and the line, and beside it the one-sentence version of what each of the three rule fields (`apiGroups`, `resources`, `verbs`) does when it holds `*`. That is the sentence [10.C1](05-10c1-a-wildcard-and-the-path-it-opens.md) makes dangerous.

**Footprint note** — the phase opens at **6.5GB** ([`pair`](../../strands/lab-topologies.md#pair) 5.0GB + [`forge`](../../strands/lab-topologies.md#build-guest) 1.5GB) against the [~9.5GB ceiling](../../strands/lab-topologies.md#ceiling). [The index](README.md) tracks what the remaining 3.0GB is spent on: a policy engine, a runtime detector, and — at the capstone — the vulnerable component itself.

**Teardown** — the RBAC objects and the probe namespace go; **the topology stays** — it is the phase's cluster now:

```sh
kubectl delete namespace probe
```
