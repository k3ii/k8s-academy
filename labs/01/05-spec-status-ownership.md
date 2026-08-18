<a id="spec-status-ownership"></a>
# Who writes each half of an object

**Claim** — for any of five objects you can say which half is `spec` and which is `status`, and **name the component that writes each half**, without looking it up. The pattern holds so uniformly that the exceptions are the interesting part.

**Rests on** — [module 1.2's reading](../../phases/01-operate-shallow.md#m1-2), the *Spec and Status* and *Typical status properties / Conditions* sections. Read them first: this exercise is a check on the convention, not a way to discover it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Create a namespace `objectmodel` and put one of each in it — a Pod, a Deployment, a Service, a ConfigMap. The Node you already have.
2. For each, print the two halves separately:

   ```sh
   kubectl -n objectmodel get deploy/web -o jsonpath='{.spec}'   | jq
   kubectl -n objectmodel get deploy/web -o jsonpath='{.status}' | jq
   ```

3. Fill in a five-row table: **object · who writes `spec` · who writes `status`**. Be specific — "a controller" is not an answer; name it (`kube-controller-manager`'s deployment controller, the kubelet, the endpoints controller, the scheduler).
4. Two of the five break the pattern. Find them by asking the API rather than by guessing:

   ```sh
   kubectl api-resources -o wide | grep -E '^(configmaps|nodes|pods|services|deployments) '
   kubectl explain configmap.status
   ```

5. Look at what a `status` actually contains for a Deployment and a Pod. Both carry a `conditions` list. Compare the two lists' shape — `type`, `status`, `reason`, `message`, `lastTransitionTime` — against what the conventions said a condition must have.
6. Ask about subresources directly, because they are the mechanism that makes the ownership split enforceable rather than merely conventional:

   ```sh
   kubectl get --raw /apis/apps/v1 | jq '.resources[] | select(.name|test("deployments"))'
   ```

   Three entries come back for one kind. Name them, and say which one a controller would PATCH.

**Expect** — ConfigMap has no `status` at all, which is the first hint that the split is about *reconciliation*, not about tidiness: nothing reconciles a ConfigMap, so nothing has anything to report. The Pod is the awkward one — `spec.nodeName` is written by the *scheduler*, not by you, even though it lives in the spec. That single field is [P5](../../phases/05-scheduler.md)'s whole output, and noticing now that scheduling is a spec write rather than a status write saves an argument later.

**Write down** — the five-row table, and the two exceptions with one sentence each. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for this table.

**Teardown** — leave the `objectmodel` namespace; [the next exercise](06-resourceversion-moves.md) edits these same objects. **The topology stays.**
