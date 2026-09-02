<a id="helm-upgrade-and-release-state"></a>
# Find the release on the cluster and read it

**Claim** — a Helm release is a Secret, and you can decode it by hand. `helm upgrade` diffs three inputs, and one of those inputs is *not* in that Secret. You can name all three inputs, and you can show each one changing the outcome.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the release from [the chart exercise](19-author-a-helm-chart.md).

**Do**

1. Find the release without asking Helm:

   ```sh
   kubectl get secrets --field-selector type=helm.sh/release.v1
   ```

   Note the structure of the name, and note the `version` label. Then upgrade once. Watch a *second* Secret appear. The first Secret is not edited.

2. Decode one Secret by hand. It is base64, twice, and then gzip:

   ```sh
   kubectl get secret sh.helm.release.v1.t.v1 -o jsonpath='{.data.release}' \
     | base64 -d | base64 -d | gunzip | jq 'keys'
   ```

   List the top-level keys. Two of them are the entire rollback mechanism. Say which two.

3. Run `helm upgrade` with a changed value, then run `helm rollback`. Watch the Secret count. A rollback creates a *new* revision, and it does not delete one. Say why that is the only safe choice.
4. **Demonstrate the three-way merge.** The demonstration needs a change from a direction that Helm did not make. With the release installed, edit the live Deployment by hand, and add an annotation that Helm has never heard of. Then run `helm upgrade` with an unrelated value change. Predict the result first: does your annotation survive?
5. Now take the case that catches everyone. Edit a field by hand that the chart *does* set: change `replicas` with `kubectl scale`. Then run `helm upgrade` with no changes at all, as `helm upgrade t build/01-chart`. Predict the result, then check it.
6. Delete the release Secret for an old revision. Then try `helm rollback` to that revision.

**Expect** — there is one Secret per revision, in the namespace of the release. Each Secret holds gzipped JSON, which contains the chart, the values and the rendered manifest. The merge has three inputs: **the old rendered manifest**, from that Secret; **the new rendered manifest**; and **live cluster state**. Only the first two inputs are in Helm's own storage, and that is why the third input is where the surprises live. Your hand-added annotation survives. It is in neither manifest, and Helm has no opinion about fields that it never set. Your `kubectl scale` does **not** survive. `replicas` *is* in both manifests, and old-equals-new means that Helm patches the value back to the chart's value. Do not read this as "Helm reconciles". It is a three-way merge of two documents against reality, computed once, on demand.

**Write down** — where Helm stores a release, and the three inputs that `helm upgrade` diffs. [The checklist asks for exactly this](../../phases/01-operate-shallow.md#checklist), and [the ecosystem section](../../phases/01-operate-shallow.md#ecosystem) says why it matters four phases from now.

**Teardown** — keep the release, because [the next exercise](21-helm-does-not-reconcile.md) breaks it deliberately. **The topology stays.**
