<a id="which-flowschema-caught-the-request"></a>
# Naming the FlowSchema and priority level for a request you sent

**Claim** — for any request you send, you can name in advance which `FlowSchema` matches it, which `PriorityLevelConfiguration` that routes to, and which distinguisher bucket it lands in — and the apiserver will tell you the first two in response headers so you can be scored.

**Rests on** — [the RequestInfo exercise](06-a-url-becomes-a-requestinfo.md). APF matches on the same parsed request, which is why the ordering in the phase puts that one first.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Read what is installed before changing anything:

   ```sh
   kubectl get flowschemas -o custom-columns=NAME:.metadata.name,PRI:.spec.matchingPrecedence,PL:.spec.priorityLevelConfiguration.name,DIST:.spec.distinguisherMethod.type
   kubectl get prioritylevelconfigurations -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,NCS:.spec.limited.nominalConcurrencyShares,QUEUES:.spec.limited.limitedResponseType
   ```

   Sort the FlowSchemas by `matchingPrecedence` and note that lower wins. Then note which one is last and what it catches.

2. Predict, in writing, the FlowSchema for each of these before sending any of them:

   | Request | Sent as | Your prediction |
   |---|---|---|
   | `kubectl get nodes` | your admin kubeconfig | |
   | `kubectl get --raw /healthz` | your admin kubeconfig | |
   | `kubectl auth can-i --list` | a plain ServiceAccount | |
   | `kubectl get pods -A` | a plain ServiceAccount | |
   | a kubelet's node status update | `system:nodes` | |

3. Score yourself against the apiserver:

   ```sh
   kubectl get nodes -v=8 2>&1 | grep -i 'X-Kubernetes-PF'
   ```

   Two headers come back — the FlowSchema's UID and the priority level's UID. Map UIDs to names:

   ```sh
   kubectl get flowschemas -o json | jq -r '.items[] | "\(.metadata.uid) \(.metadata.name)"'
   ```

   For the ServiceAccount rows, get a token and use `--token`, or `kubectl --as=system:serviceaccount:default:probe` with impersonation — and note in your write-up which identity APF actually matched on when you impersonated, because it is not necessarily the one you expected.

4. Write a FlowSchema of your own that catches exactly one thing — your own username reading ConfigMaps — at a precedence that beats the catch-all, routing to `global-default`. Confirm with the headers that it took effect, then find its precedence relative to the built-ins and say why you chose that number.

5. Find the matching code: `staging/src/k8s.io/apiserver/pkg/util/flowcontrol/apf_filter.go`, and from there the function that picks the FlowSchema and the one that computes the flow distinguisher. Answer: what happens when **two** FlowSchemas have the same `matchingPrecedence`, and is that resolved deterministically?

**Observe**

```sh
kubectl get --raw /metrics | grep -E 'apiserver_flowcontrol_(current_inqueue_requests|current_executing_requests|dispatched_requests_total)' | sort
```

**Expect** — most of your predictions land except one, and the usual miss is the exempt level: some traffic is not queued at all, and finding which is the useful half of the exercise. `/healthz` and the `system:masters` group are the two to look at closely, and the reason they are exempt is a bootstrapping argument, not a fairness one.

The distinguisher is the part that decides whether one badly-behaved client can hurt its peers: by user, by namespace, or absent entirely. A priority level whose FlowSchema has **no** distinguisher puts every matching request in one queue, which is precisely the configuration [the drill](39-3c3-starve-an-apf-priority-level.md) exploits.

**Write down** — the prediction table with scores, your own FlowSchema and the precedence argument, the exempt-level finding, and the same-precedence answer from step 5.

**Teardown** — delete your FlowSchema. Leave the built-ins alone; they are re-created by the apiserver if deleted, but the mandatory ones are re-created *differently* from the suggested ones, and this is not the exercise to discover that in. **The topology stays** — [the drill](39-3c3-starve-an-apf-priority-level.md) is next and needs the built-in configuration intact.
