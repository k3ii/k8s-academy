<a id="the-waypoint-removed-and-the-silence"></a>
# Delete the waypoint and watch the policy stop applying: the object stays, the 403 does not, nothing reports it

**Claim** — deleting the waypoint makes the `AuthorizationPolicy`'s L7 rule **stop being enforced while the object remains `Applied` in the API with no warning, no event and no status condition that says so**. L4 identity enforcement keeps working throughout, because `ztunnel` never depended on the waypoint — which is the split ambient makes and the sidecar hid.

**Rests on** — [the waypoint](22-the-waypoint-l7-policy-needs.md) and the policy it enforces, both left running by the previous exercise.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — an L4 control, so that "still working" is a measurement and not a hope.** A second client in the same namespace with a **different** ServiceAccount is denied by identity alone, which is a rule `ztunnel` can evaluate:

```sh
kubectl -n mesh create serviceaccount stranger
kubectl -n mesh run stranger --image=curlimages/curl --overrides='{"spec":{"serviceAccountName":"stranger"}}' --restart=Never -- sleep 3600
kubectl -n mesh wait --for=condition=Ready pod/stranger --timeout=60s
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'sleep    GET  %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'sleep    POST %{http_code}\n' -X POST http://httpbin:8000/post
kubectl -n mesh exec stranger -- curl -s -m 5 -o /dev/null -w 'stranger GET  %{http_code}\n' http://httpbin:8000/get
```

**Do — remove the waypoint. Nothing else changes:**

```sh
istioctl waypoint delete -n mesh waypoint
kubectl -n mesh get gateway,pods
kubectl -n mesh get authorizationpolicy get-only -o yaml | sed -n '/^status:/,$p'
kubectl -n mesh describe authorizationpolicy get-only | tail -20
kubectl -n mesh get events --sort-by=.lastTimestamp | tail -10
```

**Observe — the same three probes, and where the two planes now stand:**

```sh
sleep 10
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'sleep    GET  %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'sleep    POST %{http_code}\n' -X POST http://httpbin:8000/post
kubectl -n mesh exec stranger -- curl -s -m 5 -o /dev/null -w 'stranger GET  %{http_code}\n' http://httpbin:8000/get
istioctl ztunnel-config policy -n mesh 2>/dev/null | head -20
kubectl -n istio-system exec ds/ztunnel -- curl -s localhost:15020/metrics | grep -E 'connections_(opened|closed)_total' | head -3
```

**Expect** — the **POST to succeed** where it was a 403 a minute ago, with the policy object still present, still accepted, and still saying nothing about the rule it can no longer enforce. Expect `kubectl describe` and the event stream to be **empty of anything relevant** — no controller writes "this rule is now unenforceable" onto the object, because from the API's point of view nothing about it changed. Search for it anyway; the searching is the exercise, and finding nothing is the result to write down.

Expect the L4 control to be **unaffected in both directions**: `stranger` denied before and after, `sleep` allowed before and after. Expect that to be the precise statement of the split — the policy's `from.source.principals` clause is evaluated by `ztunnel` from the HBONE connection's peer identity, and the `to.operation.methods` clause needs something that parses HTTP. Removing the waypoint removed the second evaluator and left the first alone.

Expect `ztunnel` to still be moving connections and to be the reason `stranger` is refused, and expect the refusal to arrive as a **connection-level failure rather than a 403** — there is no HTTP layer in the path to produce a status code. Note the two different shapes of "denied" you have now seen in one namespace; a client that reports a reset and a client that reports 403 were stopped by different processes on different evidence.

**This is the phase's most operationally important result and belongs in the notes as a warning, not a curiosity**: in ambient, an L7 policy's enforcement depends on a **separate object's existence**, and deleting that object is a normal-looking cleanup action with no feedback. A sidecar mesh cannot get into this state — the enforcer is inside the pod, so a policy is either enforced or the pod is gone. Ambient trades that coupling for a much better cost curve, and this exercise is the bill.

**Write down** — in `journal/p9-ambient.md`: the six probe results as a before/after table, the empty status and event output, and one sentence naming what you would monitor to catch this in a real cluster — the honest answer involves the waypoint's own existence, not the policy's.

**Teardown — remove everything this exercise and the last one created:**

```sh
kubectl -n mesh delete authorizationpolicy get-only
kubectl -n mesh delete pod stranger
kubectl -n mesh delete serviceaccount stranger
kubectl -n mesh get gateway,authorizationpolicy,pods
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'POST %{http_code}\n' -X POST http://httpbin:8000/post
```

A 200 on the POST with no policy left is the expected end state — **no half-removed policy, no orphaned waypoint, no scratch ServiceAccount**. The Gateway API CRDs stay; they cost nothing and removing them is not free. **Ambient stays. The topology stays** — [the capstone](25-one-request-both-halves.md) is what releases it, and it switches back to sidecar mode first.
