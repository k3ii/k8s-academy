<a id="a-netpol-that-blocks-the-metadata-ip"></a>
# A pod that can reach the internet but not `169.254.169.254`

**Artifact** — a namespace whose default-deny-plus-allow NetworkPolicy lets a pod resolve DNS and reach a normal address, while a `curl` to the link-local metadata IP `169.254.169.254` hangs and times out. The metadata endpoint is the classic pivot: a pod that reaches it on many platforms can read the node's cloud credentials, so a hardening baseline blocks it — and "blocks it" is a claim you test with one `curl` that must fail while another succeeds.

**Rests on** — [the P7 lesson that a policy is inert without a CNI that enforces it](../../phases/07-networking.md#m7-4): a NetworkPolicy is inert unless the CNI enforces egress, which your cluster's CNI must, or this exercise silently "passes" by doing nothing. Confirm enforcement — a policy that drops a packet you can point at — before trusting the result here.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [egress NetworkPolicy semantics](https://kubernetes.io/docs/concepts/services-networking/network-policies/): an egress rule is an *allow* list, and the presence of any egress rule flips the pod to default-deny-egress for everything not listed. The question to answer: *to block one IP while allowing the rest, do you write a deny rule or an allow rule* — and what does that tell you about how NetworkPolicy expresses "everything except"?

**Do** — a namespace, a pod, and a policy that allows egress to everything except the metadata block:

```sh
kubectl create ns meta
kubectl -n meta run probe --image=nixery.dev/shell/curl --restart=Never --command -- sleep 3600
kubectl -n meta wait --for=condition=Ready pod/probe
# baseline: metadata IP is reachable (returns quickly, even if 404/401)
kubectl -n meta exec probe -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/ ; echo "rc=$?"

kubectl -n meta apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: block-metadata, namespace: meta}
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except: ["169.254.169.254/32"]
  - ports:                      # keep DNS working
    - {protocol: UDP, port: 53}
    - {protocol: TCP, port: 53}
YAML
```

**Observe** — after the policy, the metadata `curl` no longer returns a code; it times out at `-m 3` with `rc` non-zero, while `kubectl -n meta exec probe -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' https://kubernetes.io` still returns `200`. The block is expressed as an `except` inside an allow-all `ipBlock` — which is the answer to the reading question: NetworkPolicy has no deny rule, so "everything except X" is an allow of `0.0.0.0/0` with `X` carved out. If the metadata `curl` still returns a code, either the CNI is not enforcing egress (the P7 caveat) or the DNS rule accidentally re-permitted it — check that `169.254.169.254` is genuinely in the `except`, not merely absent from an allow.

**Expect** — metadata unreachable, general egress and DNS intact. Note the honesty limit: this blocks the *pod network* path to the IP; a pod with `hostNetwork: true` shares the node's stack and this policy does not apply to it — which is one more reason [exercise 6](06-restricted-rejects-a-pod-you-can-name.md)'s `restricted` PSA (no `hostNetwork`) and this policy are two halves of one control.

**Write down** — the two `curl` results (blocked IP vs. allowed host), and the one sentence on why NetworkPolicy expresses a block as an allow-with-except.

**Teardown** — namespace and policy go; **the topology stays**:

```sh
kubectl delete ns meta
```
