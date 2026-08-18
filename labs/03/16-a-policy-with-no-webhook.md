<a id="a-policy-with-no-webhook"></a>
# A rejection with no network hop in it

**Artifact** — a `ValidatingAdmissionPolicy` and its binding that refuse a specific field value, on the [hand-started apiserver](05-hand-start-an-apiserver.md), with the CEL expression that does it and the message the user sees. This is the object [the comparison exercise](20-the-same-rejection-twice.md) puts beside a webhook doing the identical job.

**Rests on** — [the plugin metrics](13-toggle-a-built-in-plugin.md) — a policy shows up in a different place from a plugin and a different place again from a webhook, and locating each is half of what makes the comparison meaningful. [Module 3.2's last reading pair](../../phases/03-api-machinery.md#m3-2) is the reading behind it.

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md).

**Do**

1. Write the policy. The rule: **no container may run without a memory limit**, and the message must name the container.

   ```sh
   kubectl --context=admin apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicy
   metadata: {name: require-memory-limit}
   spec:
     failurePolicy: Fail
     matchConstraints:
       resourceRules:
         - apiGroups: [""]
           apiVersions: ["v1"]
           operations: ["CREATE", "UPDATE"]
           resources: ["pods"]
     validations:
       - expression: >-
           object.spec.containers.all(c,
             has(c.resources) && has(c.resources.limits) && has(c.resources.limits.memory))
         message: "every container needs resources.limits.memory"
         reason: Invalid
   YAML
   ```

2. Bind it — a policy with no binding does nothing at all, which is the first thing to be wrong about:

   ```sh
   kubectl --context=admin apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicyBinding
   metadata: {name: require-memory-limit}
   spec:
     policyName: require-memory-limit
     validationActions: [Deny]
     matchResources:
       namespaceSelector: {}
   YAML
   ```

3. Test both directions:

   ```sh
   kubectl --context=admin run nolimit --image=busybox --restart=Never
   kubectl --context=admin run withlimit --image=busybox --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"withlimit","image":"busybox","resources":{"limits":{"memory":"32Mi"}}}]}}'
   ```

4. Change `validationActions` to `[Warn, Audit]` and re-run the first command. Then set it back to `[Deny]`.

5. Break the expression on purpose — reference a field that does not exist — and try to `apply` the policy.

**Observe**

```sh
kubectl --context=admin get validatingadmissionpolicy require-memory-limit -o jsonpath='{.status}{"\n"}' | jq .
kubectl --context=admin get --raw /metrics | grep -E 'validating_admission_policy|admission_webhook' | head
jq -r 'select(.annotations["validation.policy.admission.k8s.io/validation_failure"]) | .annotations' /tmp/audit.log | tail -3
```

**Expect** — the first pod is refused with *your* message, prefixed by the policy name. The second is admitted. `validationActions: [Warn, Audit]` turns the same evaluation into a `Warning:` line on the client and an annotation in the audit log while the object is still created — **the same policy, three different consequences, chosen at bind time rather than at write time.** No webhook can do that, because a webhook's answer *is* the consequence.

Step 5 fails at `apply`, not at evaluation: the expression is type-checked against the matched resource's schema when the policy is written, and `.status.typeChecking` on the object holds the warnings. That is the mechanical difference the [comparison exercise](20-the-same-rejection-twice.md) is built on — a broken CEL policy is caught when you write it, a broken webhook is caught when someone else's write fails.

The metrics grep is deliberately wide: expect series for policy evaluation and **none at all** for webhooks, because no webhook exists yet. Note the zero; it is the baseline.

**Write down** — the CEL expression, the exact refusal message, the three `validationActions` behaviours, and what `.status.typeChecking` said when you broke it. Keep the two manifests — [the comparison](20-the-same-rejection-twice.md) reapplies them on a real cluster.

**Teardown** — delete the pods, the binding and the policy, in that order (deleting the policy first leaves a binding pointing at nothing, which is legal and silently does nothing — worth doing once to see). **The apiserver and etcd stay up for one more exercise.** [The CA exercise](17-a-ca-and-a-serving-cert-by-hand.md) is where they stop. **No topology is up.**
