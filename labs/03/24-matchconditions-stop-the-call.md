<a id="matchconditions-stop-the-call"></a>
# Narrowing that happens before the network call, not after it

**Claim** — `rules` and `namespaceSelector` decide whether the apiserver *dials* your webhook; `matchConditions` decides whether it dials after evaluating CEL against the request — and a condition that excludes a request means your process never logs it. A webhook that filters internally cannot make this claim, and the difference is measurable in your own log.

**Rests on** — [the request log](18-the-webhook-the-apiserver-dials.md) built into both webhooks, and [the policy exercise](16-a-policy-with-no-webhook.md)'s CEL. [Module 3.2's blast-radius reading](../../phases/03-api-machinery.md#m3-2) is what this makes concrete.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [reinvocation](23-reinvocation-observed.md).

**Do**

1. Establish the baseline. Remove the `namespaceSelector` from the validating webhook so it matches every namespace, and count what arrives during one minute of ordinary cluster activity:

   ```sh
   kubectl -n academy-build logs deploy/academy-webhook --since=1m | wc -l
   kubectl -n kube-system rollout restart daemonset kube-proxy
   sleep 30
   kubectl -n academy-build logs deploy/academy-webhook --since=1m | grep -c 'namespace=kube-system'
   ```

2. Add a `matchConditions` that excludes requests from the cluster's own controllers, which is the exclusion nearly every production webhook eventually needs:

   ```yaml
   matchConditions:
     - name: exclude-system-identities
       expression: >-
         !(request.userInfo.username.startsWith('system:serviceaccount:kube-system:'))
     - name: exclude-node-identities
       expression: >-
         !('system:nodes' in request.userInfo.groups)
   ```

3. Repeat step 1's activity exactly and count again.

4. Break one on purpose — reference `request.userInfo.uid` in a way that can be null — and apply. Then create a pod.

5. Add a condition that is *expensive to be wrong about*: exclude the `academy-build` namespace itself. Then, with the webhook still `failurePolicy: Fail`, delete the webhook Deployment and try to recreate it.

**Observe**

```sh
kubectl -n academy-build logs deploy/academy-webhook --since=1m | wc -l
kubectl get --raw /metrics | grep -E 'apiserver_admission_match_condition' | head
kubectl get validatingwebhookconfiguration academy-memlimit -o jsonpath='{.webhooks[0].matchConditions}' | jq .
```

**Expect** — the count drops, and it drops **in your log**, not merely in the outcome. That is the whole claim: the requests did not arrive, were not decoded, cost no network round trip, and could not have been affected by your process being down.

Step 4 is the sharp one. A `matchCondition` that errors is governed by `failurePolicy` — with `Fail`, an expression that throws on some requests **blocks those requests**, and the block has nothing to do with your webhook's logic or availability. A CEL typo is now an outage vector, and this is the cheapest possible place to discover that. `apiserver_admission_match_condition_evaluation_errors_total` is where it shows up.

Step 5 is the recovery rehearsal: with `academy-build` excluded, deleting and recreating the webhook's own Deployment works even while the webhook is down. Without that exclusion, you would be relying on the `namespaceSelector`, and if neither exists you have built [the wedge the chaos drill is about](26-3c1-corrupt-a-cabundle.md). Doing it in this order means you meet the escape hatch before you need it, which is [what the phase file insists on](../../phases/03-api-machinery.md#chaos).

**Write down** — the two counts, the exact CEL expressions, the error metric name, and **the exclusion that makes your own webhook recoverable**. That last line is the one to be able to recite; [the drill](26-3c1-corrupt-a-cabundle.md) is two exercises away and it removes it on purpose.

**Teardown** — restore the `namespaceSelector` to `academy: "yes"` and keep the two working `matchConditions` and the `academy-build` exclusion. Delete any pods created. **The topology stays.**
