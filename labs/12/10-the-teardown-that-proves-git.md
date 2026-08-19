<a id="the-teardown-that-proves-git"></a>
# The group boundary is a test: tear the delivery stack down, and if the cluster does not come back from git, Group A never made git the source of truth

**Claim** — [Group A](01-gitops-the-reconcile-loop-you-already-wrote.md) and Group B do not fit the node honestly at once ([Istio + Prometheus alone are ~1.15GB](../../research/platform-engineering-footprints.md)), so the delivery stack is torn down before Group B — and the teardown is itself the strongest GitOps test in the phase. Delete the workloads, then reconcile from the repo: if everything Flux managed returns, git was the source of truth; if anything does not come back, it was living in the cluster and Group A only *looked* declarative. The claim to test is your own Group A, retroactively.

**Rests on** — every Group A exercise, but especially [the delivery path](01-gitops-the-reconcile-loop-you-already-wrote.md) and [the golden path](07-a-golden-path-with-no-portal.md), which are the things that must reconstitute from git; and [the footprint arithmetic](README.md) that makes the teardown mandatory rather than tidy.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued — **the node stays up**; what is torn down is the *stack on it*, not the cluster. This is a group boundary, not a topology teardown.

**Read** — [the phase's teardown note](../../phases/12-gitops-platform.md#teardown): the delivery stack comes down before the platform-API stack goes up, because both co-resident is unmeasured and unwise. The teardown doubles as a proof, which is why it is an exercise and not a cleanup line.

**Do** — remove the heavy delivery components and the apps, then reconcile from git and watch what returns:

```sh
# tear down the heavy, Group-A-only pieces:
kubectl delete ns istio-system monitoring        # Istio + Prometheus, ~1.15GB reclaimed
flux uninstall --keep-namespace=false            # or: delete the Flux-managed apps, keep Flux
kubectl top node                                 # confirm you are back near the empty baseline
# now the test: reinstall Flux, point it at the same repo, reconcile, and watch:
flux install
flux create source git demo --url=<repo-url> --branch=main --interval=1m
flux reconcile kustomization demo --with-source
kubectl get all -A       # everything Group A managed should return — from git alone
```

**Observe** — the app, the golden-path CRD instances, and the config returning from a single reconcile against the repo, with no `kubectl apply` reconstructing them by hand. Anything you had to recreate manually was never really in git — that is the finding, and it is more valuable than a clean teardown.

**Expect** — a cluster rebuilt from its repository, and RAM back near [the empty-node baseline you recorded in exercise 1](01-gitops-the-reconcile-loop-you-already-wrote.md) — the headroom Group B needs. If the rebuild is incomplete, fix what was not committed *before* proceeding; Group B assumes a clean node.

**Write down** — one line on what did and did not return from git, and the reclaimed-RAM figure that clears the way for Group B. A gap here is a Group A defect, recorded honestly.

**Footprint note** — this exercise's entire purpose is footprint: it reclaims [the ~1.15GB](../../research/platform-engineering-footprints.md) that Group B needs, on [the single `platform` node](../../strands/lab-topologies.md#platform). The [two-group split](README.md) is the fog-patch resolution made operational.

**Teardown** — this *is* the teardown — of Group A's stack, not the topology. Flux may stay (Group B does not need it, but it is cheap) or go. **The topology stays**, now hosting Group B.
