<a id="a-policy-nobody-enforces"></a>
# Apply a deny-all policy, watch nothing happen, and find the sentence that says it will not

**Claim** — a `NetworkPolicy` that selects every pod in a namespace and permits no ingress can be accepted by the API server, be visible in `kubectl get`, be syntactically perfect, and **change nothing about which packets arrive**. Further: there is no field anywhere in the object or the cluster that reports this. Both halves are checkable in ten minutes and together they are the phase's third [falsifiable claim](../../phases/07-networking.md#checklist).

**Rests on** — [exercise 10](10-the-plugin-the-kubelet-calls.md), and this is the one place your own plugin's incompleteness is the *instrument*: the pods on `.131` are wired by a plugin you wrote, which certainly does not enforce policy, so the negative result on that node is guaranteed rather than hoped for.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with `svc`'s two `web` pods spread one per node from [exercise 20](20-7c1-a-partition-named-by-path.md).

**Read** — `network/network-policy.md`, and find the sentence that says Kubernetes ships no enforcer. Quote it exactly, with the heading it sits under. It is the single most load-bearing sentence in the document and it is easy to read past, because the rest of the document describes semantics in the confident voice of something that is implemented.

**Do — part 1, establish the baseline.** Prove connectivity works *now*, from two different sources, because a policy exercise that starts from an unmeasured baseline proves nothing either way:

```sh
kubectl -n svc get pods -o wide
kubectl -n svc run client --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- sleep 3600
kubectl -n svc exec client -- sh -c 'for ip in <web pod on .130> <web pod on .131>; do
  printf "%s " $ip; curl -s -m2 -o /dev/null -w "%{http_code}\n" http://$ip:8080/ || echo FAIL; done'
```

**Do — part 2, the deny-all.** The canonical four lines:

```sh
kubectl -n svc apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: default-deny-ingress, namespace: svc}
spec:
  podSelector: {}
  policyTypes: [Ingress]
YAML
kubectl -n svc get networkpolicy
kubectl -n svc describe networkpolicy default-deny-ingress
sleep 5
kubectl -n svc exec client -- sh -c 'for ip in <web pod on .130> <web pod on .131>; do
  printf "%s " $ip; curl -s -m2 -o /dev/null -w "%{http_code}\n" http://$ip:8080/ || echo FAIL; done'
```

**Do — part 3, look for the report that does not exist.** This is the part that makes the finding operationally serious rather than a curiosity:

```sh
kubectl -n svc get networkpolicy default-deny-ingress -o yaml | grep -c '^status:'
kubectl api-resources --api-group=networking.k8s.io -o wide | grep -i networkpolicies
kubectl -n svc get events --field-selector involvedObject.kind=NetworkPolicy
kubectl explain networkpolicy.status 2>&1 | tail -2
```

**Expect** — `200` from both pods, before and after. Expect `kubectl describe` to render the policy's rules in a friendly summary that reads exactly as it would on a cluster where the policy works. Expect **no `status` field, no condition, no event, and no `SubResources` entry** — the API has no vocabulary for *nobody is implementing this*.

**Expect the result to depend on the node, and check both**, because that is the whole reason the pods were spread. Whatever the cluster's stock CNI does on `.130` is a fact about that CNI, and if it *does* enforce, then you have a two-node cluster where the same policy is enforced on one node and not the other — which is a better version of this exercise than a uniform negative and should be written up as such. Record which happened.

**Expect the comparison with admission to be the sentence worth keeping.** A `ValidatingWebhookConfiguration` whose webhook is unreachable [fails loudly](../../phases/03-api-machinery.md#chaos) and can wedge a cluster; a `NetworkPolicy` with no enforcer fails **silently and permissively**. One of those designs tells you it is broken and one does not, and the difference is not accidental — a policy engine that failed closed on absence would mean any cluster without a CNI policy implementation could serve no traffic at all.

**Write down** — the quoted sentence from the design doc with its heading, the before/after `curl` results per node, the four empty checks from part 3, and the claim as one paragraph: *why NetworkPolicy needs a CNI to enforce it*, with the observation that the failure mode is permissive and unreported. Then note the debt: **the semantics in [exercise 24](24-the-semantics-are-in-the-comments.md) cannot be tested until [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) installs something that enforces them**, which is why the next exercise is a prediction and not a measurement.

**Footprint note** — one `agnhost` client pod, ~15 MiB.

**Teardown** — leave the policy and the client pod. [Exercise 24](24-the-semantics-are-in-the-comments.md) adds to the policy set on paper and [exercise 32](32-the-prediction-scored-at-the-datapath.md) scores the lot; deleting them now means writing them twice. **The topology stays.**
