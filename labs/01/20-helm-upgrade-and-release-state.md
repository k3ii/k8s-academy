<a id="helm-upgrade-and-release-state"></a>
# Find the release on the cluster and read it

**Claim** — a Helm release is a Secret you can decode by hand, and `helm upgrade` diffs three inputs, one of which is *not* in that Secret. You can name all three and show each one changing the outcome.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the release from [the chart exercise](19-author-a-helm-chart.md).

**Do**

1. Find it without asking Helm:

   ```sh
   kubectl get secrets --field-selector type=helm.sh/release.v1
   ```

   Note the name's structure and the `version` label. Upgrade once and watch a *second* Secret appear rather than the first being edited.

2. Decode one by hand. It is base64, twice, then gzip:

   ```sh
   kubectl get secret sh.helm.release.v1.t.v1 -o jsonpath='{.data.release}' \
     | base64 -d | base64 -d | gunzip | jq 'keys'
   ```

   List the top-level keys. Two of them are the entire rollback mechanism; say which.

3. `helm upgrade` with a changed value, then `helm rollback`. Watch the Secret count. A rollback creates a *new* revision rather than deleting one — say why that is the only safe choice.
4. **Demonstrate the three-way merge**, which needs a change from a direction Helm did not make. With the release installed, edit the live Deployment by hand to add an annotation Helm has never heard of. Then `helm upgrade` with an unrelated value change. Predict first: does your annotation survive?
5. Now the case that catches everyone: edit a field by hand that the chart *does* set — change `replicas` with `kubectl scale` — then `helm upgrade` with no changes at all (`helm upgrade t build/01-chart`). Predict, then check.
6. Delete a release Secret for an old revision and try `helm rollback` to it.

**Expect** — one Secret per revision, in the release's namespace, gzipped JSON containing the chart, the values and the rendered manifest. The three inputs to the merge are **the old rendered manifest** (from that Secret), **the new rendered manifest**, and **live cluster state** — and only the first two are in Helm's own storage, which is why the third is where the surprises live. Your hand-added annotation survives, because it is not in either manifest and Helm has no opinion about fields it never set. Your `kubectl scale` does **not** survive, because `replicas` *is* in both manifests and old-equals-new means Helm patches it back to the chart's value. The distinction is not "Helm reconciles" — it is a three-way merge of two documents against reality, computed once, on demand.

**Write down** — where Helm stores a release and the three inputs `helm upgrade` diffs. [The checklist asks for exactly this](../../phases/01-operate-shallow.md#checklist), and [the ecosystem section](../../phases/01-operate-shallow.md#ecosystem) says why it matters four phases from now.

**Teardown** — keep the release; [the next exercise](21-helm-does-not-reconcile.md) breaks it deliberately. **The topology stays.**
