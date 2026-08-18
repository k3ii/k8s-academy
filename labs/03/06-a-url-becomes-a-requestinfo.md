<a id="a-url-becomes-a-requestinfo"></a>
# Four URLs, predicted before they are parsed

**Claim** — given `requestinfo.go` alone you can predict `{verb, apiGroup, apiVersion, resource, subresource, namespace, name}` for any URL the apiserver serves, including the two that do not decompose the way the path suggests.

**Rests on** — [the running apiserver](05-hand-start-an-apiserver.md), and [module 3.1's first filter question](../../phases/03-api-machinery.md#m3-1).

**Topology** — **none.** `forge` and the apiserver from [the previous exercise](05-hand-start-an-apiserver.md), still running.

**Do**

1. Read `staging/src/k8s.io/apiserver/pkg/endpoints/filters/requestinfo.go` and, in `staging/src/k8s.io/apiserver/pkg/endpoints/request/requestinfo.go`, the `NewRequestInfo` method. Two questions to answer from it before you run anything:
   - Which path prefixes make a request **non-resource** rather than resource-scoped, and what is `RequestInfo.Path` set to then?
   - Where in the parse is the HTTP method turned into a `Verb`, and which two verbs are *not* HTTP methods?

2. **Predict, in writing, all seven fields** for each of these, before issuing them:

   ```
   GET  /api/v1/namespaces/default/pods
   GET  /api/v1/namespaces/default/pods/probe/log
   GET  /apis/apps/v1/deployments
   GET  /api/v1/namespaces/default/pods?watch=true
   GET  /healthz
   GET  /api/v1/namespaces/kube-system
   ```

   The fifth is the trap and the sixth is the better trap: `namespaces` is a resource that lives at the cluster scope, so `RequestInfo.Namespace` for the sixth is not the obvious answer twice over.

3. Issue each one and let the apiserver tell you what it decided. The audit log is the field-by-field answer; turn it on by restarting the apiserver with a policy that logs metadata for everything:

   ```sh
   cat > ~/apiserver/audit-policy.yaml <<'YAML'
   apiVersion: audit.k8s.io/v1
   kind: Policy
   rules:
     - level: Metadata
   YAML
   ```

   then add to the flag set from [the previous exercise](05-hand-start-an-apiserver.md):

   ```
   --audit-policy-file=$HOME/apiserver/audit-policy.yaml
   --audit-log-path=/tmp/audit.log
   ```

**Observe**

```sh
for p in /api/v1/namespaces/default/pods \
         /api/v1/namespaces/default/pods/probe/log \
         /apis/apps/v1/deployments \
         /healthz \
         /api/v1/namespaces/kube-system ; do
  kubectl get --raw "$p" >/dev/null 2>&1
done
kubectl get --raw '/api/v1/namespaces/default/pods?watch=true' &  sleep 2; kill %1

jq -r '[.verb, .objectRef.apiGroup, .objectRef.apiVersion, .objectRef.resource,
        .objectRef.subresource, .objectRef.namespace, .objectRef.name,
        .requestURI] | @tsv' /tmp/audit.log
```

**Expect** — your predictions are right for four of six. The two that are not:

- **`?watch=true` produces `verb: watch`, not `verb: get`.** The query parameter, not the method, decides. `list` and `watch` are the two verbs the HTTP method cannot supply, and this is where they are manufactured.
- **`/healthz` has no `objectRef` at all** — it is non-resource, and the field that carries its identity is the path. RBAC rules for it are `nonResourceURLs`, a separate stanza, which is why a ClusterRole granting `get` on everything still cannot grant `/healthz`.

`/api/v1/namespaces/kube-system` shows `resource: namespaces`, `name: kube-system`, and `namespace: kube-system` — the namespace field is populated even though this is a cluster-scoped read, because the parser sets it from the path segment. If you predicted an empty namespace, read the method again; the reason is one branch and it is worth being wrong about once.

**Write down** — the six-row prediction table with your answer and the audit log's answer side by side, the `file:function` you predicted from, and the one sentence explaining where `watch` comes from. This table is the first stage of [the capstone trace](45-the-capstone-trace.md) and it is the only stage that is pure parsing.

**Teardown** — delete `/tmp/audit.log` and remove the two audit flags if you do not want them for the rest of the module (keep them; [the authorization exercise](07-rejected-at-authorization-not-admission.md) reads the same log). **The apiserver and etcd stay up. No topology is up.**
