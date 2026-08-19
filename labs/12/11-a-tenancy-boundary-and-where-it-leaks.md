<a id="a-tenancy-boundary-and-where-it-leaks"></a>
# The namespace-per-team boundary, built from four objects — and the inventory of exactly where it leaks

**Artifact** — a namespace-per-team tenancy boundary assembled from RBAC + `ResourceQuota` + `LimitRange` + `NetworkPolicy`, and beside it an honest **leak inventory**: the places a namespace boundary does *not* hold — node-level noisy neighbours, cluster-scoped resources, shared CRDs, one CoreDNS for everyone. The deliverable is not the boundary (that is four objects you have seen) but the catalogue of what it cannot contain, which is what motivates [the vcluster exercise](12-the-same-pod-in-two-apiservers.md) that follows.

**Rests on** — [P4](../../phases/04-controllers.md) for the CRD-shaped thinking, and the earlier phases where each of these four objects was first met; this exercise composes them into a boundary and then finds its holes.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued — Group B's node, cleared by [the group teardown](10-the-teardown-that-proves-git.md).

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-4). The four objects' mechanics are earlier-phase material and are not restated; this exercise is about the *boundary they form and where it ends*.

**Build** — the four-object boundary for one team, then probe each place it leaks:

```sh
kubectl create ns team-a
kubectl -n team-a create quota q --hard=cpu=2,memory=4Gi,pods=10
kubectl -n team-a apply -f limitrange.yaml       # default + max per container
kubectl -n team-a apply -f rbac.yaml             # a Role scoped to team-a, bound to the team
kubectl -n team-a apply -f netpol-default-deny.yaml
# now the leaks — each is a boundary the namespace does NOT draw:
kubectl auth can-i list nodes --as=system:serviceaccount:team-a:default   # cluster-scoped: yes -> leak
kubectl get crd                                    # shared cluster-wide: team-a sees them all
kubectl -n team-a run hog --image=busybox -- sh -c 'while :; do :; done'  # node CPU: noisy neighbour
```

**Verify from outside** — the leak inventory is checkable, not asserted: each row is a command whose output shows the boundary failing to contain something. `can-i list nodes` returning `yes` proves cluster-scoped resources escape the namespace; a shared CoreDNS answering both tenants' queries proves DNS is not partitioned. A leak you cannot demonstrate does not belong on the inventory.

**Expect** — a boundary that holds for namespaced objects and quota, and leaks for everything cluster-scoped or node-level. That gap is the precise reason a stronger boundary — a virtual cluster with its own apiserver — exists, which is [the next exercise](12-the-same-pod-in-two-apiservers.md).

**Write down** — the four-object boundary and the leak inventory: for each leak, the command that demonstrates it and one word for the class (cluster-scoped / node-level / shared-CRD / shared-DNS).

**Footprint note** — the boundary objects cost nothing measurable; [`platform`](../../strands/lab-topologies.md#platform) is unmoved. The cost arrives with [vcluster](12-the-same-pod-in-two-apiservers.md).

**Teardown** — keep `team-a` (the [vcluster exercise](12-the-same-pod-in-two-apiservers.md) and [the capstone](18-the-platform-and-its-critique.md) reuse a tenant namespace) but delete the CPU hog and any probe pods. **The topology stays.**
