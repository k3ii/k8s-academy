<a id="kustomize-base-and-overlays"></a>
# Two overlays over one base, with no templating language

**Claim** — you can produce two environment-specific manifests from one base. The YAML contains no placeholder of any kind. You can also say what kustomize does that a text templater structurally cannot do.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Steps 1 to 4 need no cluster at all, because `kustomize build` is a pure function of files.

**Do**

1. Lay out a base and two overlays:

   ```
   app/
     base/            kustomization.yaml, deployment.yaml, service.yaml, configmap.yaml
     overlays/dev/    kustomization.yaml
     overlays/prod/   kustomization.yaml
   ```

   The base must be **deployable as it is**. That constraint is the whole design. A base with placeholders in it is not a base.

2. Make `dev` differ by replica count and image tag. Make `prod` differ by those two things, plus a resource block, plus an extra label on everything. Express each difference with the narrowest tool that can do it:

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

3. Diff the two outputs before you apply anything: `diff <(kubectl kustomize overlays/dev) <(kubectl kustomize overlays/prod)`. Every line of that diff should be a difference that you asked for. The lines that you did not ask for are the lesson.
4. Add a `configMapGenerator`, and rebuild. The generated name carries a hash suffix. Now change one value in the source file, and rebuild again. The name changes, *and the reference in the Deployment changes with it*. Say what that behaviour buys you, and what a hand-written ConfigMap does not give you.
5. Apply both overlays to two namespaces with `kubectl apply -k`. Confirm that they coexist. Then check that the hash suffix of the generator survived the round trip.
6. Break the setup in a useful way. Patch a field on a resource that the target selector does not match. kustomize says nothing at all. That silence is the thing to remember about the tool.

**Expect** — the diff holds exactly your three or four intended differences, plus the propagation of `namePrefix` and of the label. Note where the label went: it propagated into the `selector` of the Service, as well as into its `metadata`. That behaviour is correct, and it is also the sharpest edge in the tool. A `commonLabels` change is a selector change, and selectors are immutable on a Deployment. The generator hash is the mechanism that kustomize has instead of a restart annotation. A ConfigMap change becomes a *new object with a new name*, so the pod template changes, so a rollout happens. Helm has no equivalent, and [that gap is why charts grow checksum annotations](19-author-a-helm-chart.md).

**Write down** — one paragraph on what kustomize does that a text templater cannot do. Ground the paragraph in step 4. Then add the unrequested lines from the diff in step 3.

**Teardown** — run `kubectl delete -k overlays/dev -k overlays/prod`, and delete the two namespaces. Keep the files, and commit them. **The topology stays.**
