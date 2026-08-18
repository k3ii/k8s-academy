<a id="stage-2-and-the-role-you-write-yourself"></a>
# Stage 2: the same binary, and a ClusterRole discovered one 403 at a time

**Artifact** — [stage 2](../../strands/build-mechanics.md#two-stages) of build artifact 1: the operator as an image in the registry, running as a Deployment in `academy-build`, under a ServiceAccount whose ClusterRole you wrote **by starting from empty and adding exactly the rule each failure demanded**. The finished role is the artifact; the sequence of 403s is the exercise.

**Rests on** — [the stage-1 operator](15-the-hand-wired-loop.md), unchanged. Not one line of reconcile logic is edited here, which is the point of the two-stage split: what changes is everything *around* the code.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The image is built and pushed on [`forge`](../../strands/lab-topologies.md#build-guest).

**Build** — the mechanics are the strand's and are not restated: [the registry](../../strands/build-mechanics.md#registry), [the `scratch` base image](../../strands/build-mechanics.md#base-image), [the identity convention](../../strands/build-mechanics.md#identity), and [the sizing rule](../../strands/build-mechanics.md#sizing) including the limit decision you must write down rather than default. What this exercise adds is the authorisation.

```
build/04-operator-clientgo/deploy/
  namespace.yaml         academy-build already exists from P3; reuse it
  serviceaccount.yaml
  clusterrole.yaml       <- starts empty. This is the exercise.
  clusterrolebinding.yaml
  deployment.yaml        one replica, memory request set, limit argued
```

**Do**

1. Push the image, then deploy with a ClusterRole containing **no rules at all**:

   ```yaml
   rules: []
   ```

2. Read the first failure, and only the first:

   ```sh
   kubectl -n academy-build logs deploy/academy-operator --tail=20
   ```

3. Add exactly the one rule that failure names — the group, the resource and the single verb, not a wildcard and not the whole verb set. Re-deploy. Repeat until the operator is quiet and `alpha` reconciles again.

4. Keep a running table as you go:

   | # | Message | Rule added | Which part of the operator needed it |
   |---|---|---|---|
   | 1 | | | |

**Gate** — unchanged: [`envtest`](16-envtest-is-a-real-apiserver.md) gates the code, and the code did not change. Stage 2 is gated by the cluster doing the same thing the `go run` did, which you check by re-running [the reconcile drill](17-4c1-kill-it-mid-reconcile.md) against the pod: `kubectl -n academy-build delete pod -l app=academy-operator` is the in-cluster form of SIGKILL, and it must converge identically.

**Verify from outside** — the operator's own identity, from the cluster's point of view rather than from your code:

```sh
kubectl -n academy-build get deploy academy-operator -o jsonpath='{.spec.template.spec.serviceAccountName}'
kubectl auth can-i --list --as=system:serviceaccount:academy-build:academy-operator | sort
kubectl auth can-i update ensembles/status --as=system:serviceaccount:academy-build:academy-operator -n academy-lab
```

**Expect** — five or six rounds, and the order they arrive in is the informative part. `list` and `watch` on `ensembles` come first, from the informer, before any reconcile happens at all. `get` on `ensembles` does *not* appear, because the lister reads the cache and never asks the server — a genuinely surprising absence, and the reason a role built by guessing is usually both too wide and missing something.

Three rules people leave out until the 403 tells them:

- **`update` on `ensembles`** — not for the spec, which the operator never writes, but for the **finalizer**, which lives in `metadata` and is therefore a write to the main resource.
- **`update` on `ensembles/status`** — a separate resource string for a separate subresource, which is exactly the split [the gate asserts](16-envtest-is-a-real-apiserver.md).
- **`create` and `delete` on `configmaps` in two namespaces**, which is why this is a ClusterRole and not a Role. The registry namespace is chosen by the object's *spec*, so the operator cannot be scoped to a namespace list fixed at deploy time — a small, real illustration of how an API design decision becomes an authorisation decision. Say in the write-up what a narrower design would have looked like.

**Write down** — the numbered 403 table, the finished `rules:` block, and the memory limit decision with its argument.

**Footprint note** — one more small Deployment on [`pair`](../../strands/lab-topologies.md#pair), sized [by the strand's rule](../../strands/build-mechanics.md#sizing). Stop the `go run` copy on `forge` before starting the in-cluster one: two operators reconciling the same objects is [drill 4.C3](30-4c3-two-replicas-no-leader-election.md), and meeting it here by accident wastes the drill.

**Teardown** — scale the Deployment to zero and run the `go run` copy again for the next module; leaving both up is the accident above. Keep the image and the manifests — [the diff](33-the-diff.md) compares this directory against what `kubebuilder` generates. **The topology stays.**
