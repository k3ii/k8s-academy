<a id="b05"></a>
# B5 — A CRD, its operator, and a CR you watch reconcile

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / CRDs and operators

> **The exam does not ask you to write an operator. It asks you to install one and tell whether it is working.** That is a narrower skill and a different one: reading a CRD to find out what fields a CR may carry, finding the controller that watches it, and distinguishing "my CR is wrong" from "the controller is not running" from "the controller is running and rejecting it".

**Do**

1. Install a CRD on its own, with no controller behind it. Create a CR. **It is accepted and nothing happens** — the API server stores any object whose schema validates, and storage is not reconciliation. Sit with that for a moment; it is the single most common confusion in this area.
2. Read the CRD rather than its documentation: `kubectl explain` works on custom resources exactly as it does on built-ins, and it is the only tool you are allowed in the exam that answers "what fields does this thing take".
3. Install the controller. Watch the same CR you already created get picked up and acted on. Nothing changed about the CR.
4. Break it in the two ways that matter. **Scale the controller to zero** — CRs are still accepted, still stored, and nothing reconciles, with no error anywhere. Then **make a CR invalid** against the schema and watch the API server reject it at admission, which is loud and immediate. Learn both signatures; they are opposite.
5. Note scope. A CRD is cluster-scoped but its resources may be `Namespaced` or `Cluster`, and `kubectl get <kind>` without `-A` will quietly show you nothing for a namespaced kind in another namespace.

**Observe**

```sh
kubectl get crd
kubectl explain <kind>.spec --recursive | head -40
kubectl api-resources --api-group=<group>
kubectl get <kind> -A
kubectl -n <ns> logs deploy/<controller> --tail=50
kubectl describe <kind> <name> | sed -n '/Status/,$p'
```

**Done when** — you can take an unfamiliar CRD and, without documentation, state its group, version, scope, kind, the fields its spec accepts, and which Deployment is supposed to be watching it.

**Done in one sitting.** If it overruns, the two-signature exercise in step 4 is the part to protect; the install is the cheap half.

**Teardown** — remove the CRD and confirm its CRs went with it. **Deleting a CRD deletes every object of that kind, cluster-wide, without a confirmation**, which is worth doing once deliberately so you never do it by accident.

**See also** — **B4** installs three charts that are each a CRD and a controller, so this build is what stops that one being magic.
