<a id="author-a-helm-chart"></a>
# A chart with a subchart, a helper and a real conditional

**Artifact** — a chart that lints clean, renders correctly under three different value sets, and pulls in one subchart dependency. **This is [the capstone's input](../../phases/01-operate-shallow.md#capstone)** — [the multi-service app](23-the-multi-service-app.md) grows this chart rather than starting a new one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Everything up to step 6 renders locally and needs no cluster.

**Build**

**This is not one of [the eleven build-track artifacts](../../strands/build-mechanics.md#artifact-table)** — those are Go modules and nothing in `build-mechanics` applies here. It lives in `build/01-chart/` because it is committed code and [the checklist](../../phases/01-operate-shallow.md#checklist) requires the chart to be committed.

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

Four requirements, each of which is the reason for one template:

1. **A real conditional** — `ingress.enabled` must make the difference between the Ingress object existing and not existing, not between two variants of it. Test it renders to *nothing* when false.
2. **A helper that is used more than once** — `_helpers.tpl` defines the name and label logic in one place, and every template calls it. If a template hard-codes a name, that is the bug this requirement exists to prevent.
3. **A subchart dependency** — declare it in `Chart.yaml`, `helm dependency update`, and set one of its values from the parent's `values.yaml`. A `bitnami/*` chart or a second chart of your own; what matters is that the parent overrides a child value and you can see it in the rendered output.
4. **A checksum annotation** — `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}` on the pod template, so a ConfigMap change causes a rollout. Prove it by upgrading with a changed value and watching the pods restart. This is [what kustomize gets for free](18-kustomize-base-and-overlays.md) from generator hashes.

**Verify**

```sh
helm lint build/01-chart
helm template t build/01-chart | kubectl apply --dry-run=server -f -
helm template t build/01-chart --set ingress.enabled=false | grep -c 'kind: Ingress'   # 0
helm template t build/01-chart --set subchart.replicaCount=3 | grep -A2 'replicas:'
```

**Gate** — `helm lint` clean; `--dry-run=server` accepted by the API server, which catches the schema errors `lint` does not; the Ingress genuinely absent when disabled; the parent's override visibly reaching the subchart's rendered output. Then `helm install` it for real and confirm `NOTES.txt` prints a URL that works.

**Expect** — the two failures that come first are a helper that produces a name longer than 63 characters (the label value limit, and `trunc 63 | trimSuffix "-"` is in every generated chart for that reason) and `--dry-run=server` rejecting something `lint` passed, because `lint` checks templates and the API server checks objects.

**Write down** — the rendered diff between `ingress.enabled` true and false, and one sentence on why the checksum annotation is necessary at all — which is a statement about what Helm does *not* watch.

**Teardown** — keep the release installed; [the release-state exercise](20-helm-upgrade-and-release-state.md) reads it. **The topology stays.**
