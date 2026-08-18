<a id="kustomize-base-and-overlays"></a>
# Two overlays over one base, with no templating language

**Claim** — you can produce two environment-specific manifests from one base without a single placeholder in the YAML, and say what kustomize does that a text templater structurally cannot.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Steps 1–4 need no cluster at all — `kustomize build` is a pure function of files.

**Do**

1. Lay out a base and two overlays:

   ```
   app/
     base/            kustomization.yaml, deployment.yaml, service.yaml, configmap.yaml
     overlays/dev/    kustomization.yaml
     overlays/prod/   kustomization.yaml
   ```

   The base must be **deployable as-is**. That constraint is the whole design: a base with placeholders in it is not a base.

2. `dev` differs by replica count and image tag; `prod` differs by those plus a resource block and an extra label on everything. Express each difference with the narrowest tool that does it:

   ```yaml
   # overlays/prod/kustomization.yaml
   resources: [../../base]
   namePrefix: prod-
   commonLabels: {env: prod}
   replicas: [{name: web, count: 4}]
   images: [{name: nginx, newTag: '1.27'}]
   patches:
     - path: resources.yaml
       target: {kind: Deployment, name: web}
   ```

3. Diff the two outputs before applying anything: `diff <(kubectl kustomize overlays/dev) <(kubectl kustomize overlays/prod)`. Every line of that diff should be a difference you asked for. Lines you did not ask for are the lesson.
4. Add a `configMapGenerator` and rebuild. The generated name has a hash suffix. Now change one value in the source file and rebuild: the name changes *and the Deployment's reference changes with it*. Say what that buys that a hand-written ConfigMap does not.
5. Apply both to two namespaces with `kubectl apply -k`, confirm they coexist, and check that the generator's hash suffix survived the round trip.
6. Break it usefully: patch a field on a resource the target selector does not match. kustomize says nothing at all, and that silence is the thing to remember about it.

**Expect** — the diff is exactly your three or four intended differences plus the `namePrefix` and label propagation, and the label propagated into the Service's `selector` as well as its `metadata` — which is correct and is also the sharpest edge in the tool, because a `commonLabels` change is a selector change and selectors are immutable on a Deployment. The generator hash is the mechanism kustomize has instead of a restart annotation: a ConfigMap change becomes a *new object with a new name*, so the pod template changes, so a rollout happens. Helm has no equivalent and [that gap is why charts grow checksum annotations](19-author-a-helm-chart.md).

**Write down** — one paragraph on what kustomize does that a text templater cannot, grounded in step 4, and the unrequested lines from step 3's diff.

**Teardown** — `kubectl delete -k overlays/dev -k overlays/prod` and delete the two namespaces. Keep the files; commit them. **The topology stays.**
