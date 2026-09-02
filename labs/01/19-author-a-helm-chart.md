<a id="author-a-helm-chart"></a>
# A chart with a subchart, a helper and a real conditional

**Artifact** — a chart that lints clean, renders correctly under three different value sets, and pulls in one subchart dependency. **This chart is [the capstone's input](../../phases/01-operate-shallow.md#capstone)**. [The multi-service app](23-the-multi-service-app.md) grows this chart, and does not start a new one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Everything up to step 6 renders locally, and needs no cluster.

**Build**

**This chart is not one of [the eleven build-track artifacts](../../strands/build-mechanics.md#artifact-table).** Those artifacts are Go modules, and nothing in `build-mechanics` applies here. The chart lives in `build/01-chart/` for two reasons: it is committed code, and [the checklist](../../phases/01-operate-shallow.md#checklist) requires the chart to be committed.

```
build/01-chart/
  Chart.yaml          with a dependencies: entry
  values.yaml         with a comment on every key that is not self-explanatory
  templates/
    _helpers.tpl      fullname, labels, selectorLabels, serviceAccountName
    deployment.yaml
    service.yaml
    ingress.yaml      wholly inside an {{- if .Values.ingress.enabled }}
    serviceaccount.yaml
    NOTES.txt         must print the actual reachable URL, not a placeholder
  charts/             the fetched subchart
```

There are four requirements. Each requirement is the reason for one template.

1. **A real conditional.** `ingress.enabled` must decide whether the Ingress object exists. It must not decide between two variants of the object. Test that the template renders to *nothing* when the value is false.
2. **A helper that is used more than once.** `_helpers.tpl` defines the name logic and the label logic in one place, and every template calls it. A template that hard-codes a name is the bug which this requirement exists to prevent.
3. **A subchart dependency.** Declare it in `Chart.yaml`. Run `helm dependency update`. Then set one of the child's values from the `values.yaml` of the parent. Use a `bitnami/*` chart, or a second chart of your own. What matters is that the parent overrides a child value, and that you can see the override in the rendered output.
4. **A checksum annotation.** Put `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}` on the pod template, so that a ConfigMap change causes a rollout. Prove that it works: upgrade with a changed value, and watch the pods restart. This is [what kustomize gets for free](18-kustomize-base-and-overlays.md) from generator hashes.

**Verify**

```sh
helm lint build/01-chart
helm template t build/01-chart | kubectl apply --dry-run=server -f -
helm template t build/01-chart --set ingress.enabled=false | grep -c 'kind: Ingress'   # 0
helm template t build/01-chart --set subchart.replicaCount=3 | grep -A2 'replicas:'
```

**Gate** — four conditions must hold. `helm lint` is clean. `--dry-run=server` is accepted by the API server, which catches the schema errors that `lint` does not catch. The Ingress is genuinely absent when it is disabled. The override of the parent visibly reaches the rendered output of the subchart. Then run `helm install` for real, and confirm that `NOTES.txt` prints a URL that works.

**Expect** — two failures come first. The first is a helper that produces a name longer than 63 characters. That is the label value limit, and it is why `trunc 63 | trimSuffix "-"` is in every generated chart. The second is `--dry-run=server` rejecting something that `lint` passed. The reason is a division of labour: `lint` checks templates, and the API server checks objects.

**Write down** — the rendered diff between `ingress.enabled` set to true and set to false. Then write one sentence on why the checksum annotation is necessary at all. That sentence is a statement about what Helm does *not* watch.

**Teardown** — keep the release installed, because [the release-state exercise](20-helm-upgrade-and-release-state.md) reads it. **The topology stays.**
