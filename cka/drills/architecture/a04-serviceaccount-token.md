<a id="a04"></a>
# A4 — A ServiceAccount token: create it, mount it, read it, use it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / RBAC

> **ServiceAccounts stopped auto-generating Secrets years ago, and a lot of material has not caught up.** Creating a ServiceAccount today gives you a ServiceAccount and nothing else. Knowing the two remaining ways to get a token — and which one is right — is the drill.

**Do**

1. Create a ServiceAccount and look for its Secret. **There isn't one.** Confirm that rather than assuming it, because half the guidance you will find online says otherwise.
2. **The right way: `kubectl create token <sa>`.** A TokenRequest — time-bound, audience-bound, not stored anywhere. Decode it and read the claims: expiry, audience, and the bound object. Note that it expires, which is the entire point.
3. **The legacy way**, which still exists for the cases that need it: a `Secret` of type `kubernetes.io/service-account-token` with a `kubernetes.io/service-account.name` annotation. The controller fills in the token. It does not expire, which is why it is no longer the default.
4. **The automatic way, which is what pods actually use.** Run a pod with the ServiceAccount and look inside `/var/run/secrets/kubernetes.io/serviceaccount/` — token, `ca.crt`, `namespace`. It is a **projected** volume: the kubelet rotates the token in place, so a long-running pod never holds a stale one.
5. Use it. From inside the pod, call the API server with the token as a bearer and `ca.crt` as the CA. Then bind a Role to the ServiceAccount and watch the same call go from 403 to 200 with nothing else changing.
6. `automountServiceAccountToken: false` — set it on the pod and on the ServiceAccount, and know that the pod-level setting wins.

**Observe**

```sh
kubectl create token <sa> --duration=10m
kubectl get sa <sa> -o yaml
kubectl exec <pod> -- ls /var/run/secrets/kubernetes.io/serviceaccount/
kubectl exec <pod> -- sh -c 'curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  https://kubernetes.default/api/v1/namespaces/$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)/pods'
```

**Done when** — you got a 403 and then a 200 from inside the pod, changing only the RBAC, and you can name all three paths to a token.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. All three paths, with the docs open. | 10 min |
| **2** | Start from a pod that is already failing with 403 and fix it. | 8 min |
| **3** | Cold, no notes. `create token` and the in-pod curl from memory. | 5 min |

**Teardown** — delete the namespace.

**See also** — **A6** starts where step 5 does, with a 403 and no explanation.
