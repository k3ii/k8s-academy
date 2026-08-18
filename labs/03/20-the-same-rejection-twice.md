<a id="the-same-rejection-twice"></a>
# Identical semantics, two failure surfaces

**Claim** — the CEL policy and the webhook reject exactly the same pods with exactly the same rule, and differ in four measurable ways: the latency added to an admitted request, what happens when the enforcer is unavailable, when a mistake in the rule is caught, and what the cluster does if you delete the enforcer while it is enforcing.

**Rests on** — [the policy](16-a-policy-with-no-webhook.md) and [the webhook](18-the-webhook-the-apiserver-dials.md), which were built with the identical rule for this comparison. This is [module 3.2's contrast](../../phases/03-api-machinery.md#m3-2), run here because it needs both halves to exist.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the SAN drill](19-change-one-san.md), with the `go run` webhook up.

**Setup**

Re-apply the policy and binding from [the policy exercise](16-a-policy-with-no-webhook.md) onto `pair`, and scope the binding to a second namespace so the two enforcers never both act on the same pod:

```sh
kubectl create namespace policy-only
kubectl label namespace policy-only academy=no
```

Bind the policy with a `namespaceSelector` matching `academy=no`; the webhook already matches `academy=yes`. Two namespaces, one rule, two mechanisms.

**Do**

1. Confirm both reject and both admit:

   ```sh
   for ns in tenant policy-only; do
     kubectl -n $ns run nolimit --image=busybox --restart=Never
   done
   ```

2. **Latency.** Time twenty *admitted* creates in each namespace — the interesting number is the cost paid by requests that pass, not by requests that fail:

   ```sh
   for ns in tenant policy-only; do
     echo -n "$ns "
     /usr/bin/time -f %e bash -c "for i in \$(seq 20); do
       kubectl -n $ns run ok\$i --image=busybox --restart=Never \
         --overrides='{\"spec\":{\"containers\":[{\"name\":\"ok\$i\",\"image\":\"busybox\",\"resources\":{\"limits\":{\"memory\":\"32Mi\"}}}]}}' >/dev/null
     done"
   done
   ```

3. **Availability.** Kill the `go run` process on `forge` and try both namespaces again. Then restart it.

4. **When a mistake is caught.** Introduce the same bug into both: a rule referencing a field that does not exist. In the policy, that is an edited `expression`; in the webhook, an edited `admit.go`.

5. **Deleting the enforcer.** Delete the `ValidatingAdmissionPolicyBinding`, then re-create it. Delete the `ValidatingWebhookConfiguration`, then re-create it. Time both round trips.

**Observe**

```sh
kubectl get --raw /metrics | grep -E 'apiserver_admission_webhook_admission_duration_seconds_sum|apiserver_validating_admission_policy'
kubectl get validatingadmissionpolicy require-memory-limit -o jsonpath='{.status.typeChecking}{"\n"}' | jq .
kubectl -n tenant run afterkill --image=busybox --restart=Never 2>&1 | tail -2
```

**Expect** — four differences, and the fourth is the one nobody predicts:

- **Latency**: the webhook adds a network round trip per matching request, and it is measurable in the twenty-create loop even on a quiet lab bridge. The policy's cost is a CEL evaluation and does not leave the process.
- **Availability**: with `failurePolicy: Fail`, killing the webhook stops *all* creates in `tenant`; `policy-only` is unaffected because there is nothing to be unavailable. **The webhook coupled the cluster's write availability to a process on another machine.**
- **When the mistake is caught**: the policy's bad expression is rejected at `apply` time with `status.typeChecking` populated; the webhook's bad code is caught by the *next unlucky user*. Same bug, one caught at authoring time and one caught in production.
- **Deleting the enforcer**: both deletes take effect quickly, and re-creating the webhook configuration takes effect quickly too — but the apiserver caches the webhook's TLS client and service resolution, so a change that alters *how it is reached* is not always as immediate as a change to what it matches. Note whatever you measure rather than assuming either way.

The latency number will be dominated by `kubectl`'s own startup unless you are careful; if the two namespaces come out within noise of each other, drive the loop with `kubectl create --raw` or a single `apply -f` of twenty documents and say so in the write-up.

**Write down** — the four-row comparison with your measured numbers, and the one sentence [module 3.2 asks for](../../phases/03-api-machinery.md#m3-2): when CEL-in-process beats a webhook. Then the harder second sentence: **when it does not** — there is a class of rule a policy cannot express, and naming it is what stops this from being an argument that webhooks are obsolete.

**Teardown** — delete all pods in both namespaces, delete the `policy-only` namespace, the binding and the policy. **Keep the webhook configuration and the `go run` process.** **The topology stays.**
