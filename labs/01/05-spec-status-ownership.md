<a id="spec-status-ownership"></a>
# Who writes each half of an object

**Claim** — take any of five objects. You can say which half is `spec` and which half is `status`. You can also **name the component that writes each half**, without looking it up. The pattern holds so uniformly that the exceptions are the interesting part.

**Rests on** — [module 1.2's reading](../../phases/01-operate-shallow.md#m1-2). Read two sections: *Spec and Status*, and *Typical status properties / Conditions*. Read them first. This exercise checks the convention. It is not a way to discover the convention.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Create a namespace `objectmodel`. Put one of each object in it: a Pod, a Deployment, a Service and a ConfigMap. You already have the Node.
2. For each object, print the two halves separately:

   ```sh
   kubectl -n objectmodel get deploy/web -o jsonpath='{.spec}'   | jq
   kubectl -n objectmodel get deploy/web -o jsonpath='{.status}' | jq
   ```

3. Fill in a table of five rows: **object · who writes `spec` · who writes `status`**. Be specific. "A controller" is not an answer. Name it: the deployment controller in `kube-controller-manager`, the kubelet, the endpoints controller, or the scheduler.
4. Two of the five objects break the pattern. Find them by asking the API, and not by guessing:

   ```sh
   kubectl api-resources -o wide | grep -E '^(configmaps|nodes|pods|services|deployments) '
   kubectl explain configmap.status
   ```

5. Look at what a `status` actually contains, for a Deployment and for a Pod. Both objects carry a `conditions` list. Compare the shape of the two lists — `type`, `status`, `reason`, `message` and `lastTransitionTime` — against what the conventions say a condition must have.
6. Ask about subresources directly. Subresources are the mechanism that makes the ownership split enforceable, rather than merely conventional:

   ```sh
   kubectl get --raw /apis/apps/v1 | jq '.resources[] | select(.name|test("deployments"))'
   ```

   Three entries come back for one kind. Name them, and say which one a controller would PATCH.

**Expect** — ConfigMap has no `status` at all. That is the first hint about the split: the split is about *reconciliation*, and not about tidiness. Nothing reconciles a ConfigMap, so nothing has anything to report. The Pod is the awkward object. The *scheduler* writes `spec.nodeName`, and you do not, even though the field lives in the spec. That single field is the whole output of [P5](../../phases/05-scheduler.md). Notice now that scheduling is a spec write, and not a status write. That saves you an argument later.

**Write down** — the table of five rows, and one sentence about each of the two exceptions. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for this table.

**Teardown** — leave the `objectmodel` namespace in place, because [the next exercise](06-resourceversion-moves.md) edits these same objects. **The topology stays.**
