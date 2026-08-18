<a id="rejected-at-authorization-not-admission"></a>
# The same request, refused at two different stages

**Claim** — an authenticated identity with no RBAC binding is refused **before** any admission plugin runs, and you can prove admission never saw it. Bind the identity and the identical request reaches admission, where a different refusal is available.

**Rests on** — [the two identities](05-hand-start-an-apiserver.md) in `tokens.csv`, and [the cert-versus-identity distinction](04-mis-sign-a-client-cert.md), which is this claim one layer earlier and with a certificate instead of a token.

**Topology** — **none.** `forge`, the running apiserver, and the audit log from [the URL predictions](06-a-url-becomes-a-requestinfo.md).

**Do**

1. As `nobody`, try to create a pod:

   ```sh
   kubectl --context=nobody run p1 --image=busybox --restart=Never -- sleep 3600
   ```

2. Now make admission *loud*, so that "admission never ran" is an observation rather than an assumption. The `LimitRanger` plugin is on by default and does nothing without a LimitRange; give it one, as `admin`, in a namespace `nobody` will write to:

   ```sh
   kubectl --context=admin create namespace tenant
   kubectl --context=admin -n tenant create -f - <<'YAML'
   apiVersion: v1
   kind: LimitRange
   metadata: {name: caps}
   spec:
     limits:
       - type: Container
         max: {memory: 64Mi}
   YAML
   ```

3. Retry as `nobody`, now asking for more memory than the LimitRange permits — a request that would fail admission *if it ever got there*:

   ```sh
   kubectl --context=nobody -n tenant run p2 --image=busybox --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"p2","image":"busybox","resources":{"limits":{"memory":"512Mi"}}}]}}' \
     -- sleep 3600
   ```

4. Bind `nobody` and repeat the identical command:

   ```sh
   kubectl --context=admin -n tenant create rolebinding nobody-edit \
     --clusterrole=edit --user=nobody
   ```

**Observe**

```sh
kubectl --context=nobody -n tenant run p3 --image=busybox --restart=Never -v=8 2>&1 | grep -E 'HTTP/|Response Body' | tail -4
jq -r 'select(.user.username=="nobody") | [.verb,.objectRef.resource,.responseStatus.code,.annotations["authorization.k8s.io/decision"],.annotations["authorization.k8s.io/reason"]] | @tsv' /tmp/audit.log
grep -i 'forbidden\|denied' /tmp/apiserver.log | tail -20
```

**Expect** — before the binding, both attempts fail identically with `403 Forbidden` and a message naming the *user, verb and resource* — never the memory limit. The audit annotation reads `decision: forbid` with a reason naming the missing RBAC rule. **The LimitRange is not mentioned, because the plugin was never invoked**, and that absence is the evidence.

After the binding, the third pod is admitted and the *second* form fails with a message from `LimitRanger` naming the container and `maximum memory usage per Container`. Same HTTP status class, entirely different sentence, produced by a different stage. Two `403`s that mean *"not you"* and *"not that"*.

The usual confusion: `kubectl` prints both as *"error when creating"*, so reading only the client output makes these look like one failure with two wordings. The audit annotation is what separates them without ambiguity, and it is the reason the audit log stays on for this module.

**Write down** — the two refusal messages verbatim, the audit annotation for each, and **the file that produced each one** — one under `plugin/pkg/auth/authorizer/rbac/`, one under `plugin/pkg/admission/limitranger/`. Add both to [the running list of failures that look identical from the client](04-mis-sign-a-client-cert.md).

**Teardown** — `kubectl --context=admin delete namespace tenant` and delete any pods created in `default`. Note that the namespace will hang `Terminating` for the reason [the apiserver exercise](05-hand-start-an-apiserver.md) predicted; remove its finaliser by hand to actually clear it:

```sh
kubectl --context=admin get namespace tenant -o json \
  | jq '.spec.finalizers=[]' \
  | kubectl --context=admin replace --raw /api/v1/namespaces/tenant/finalize -f -
```

**The apiserver and etcd stay up. No topology is up.**
