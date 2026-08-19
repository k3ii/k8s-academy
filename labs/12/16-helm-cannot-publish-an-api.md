<a id="helm-cannot-publish-an-api"></a>
# `kubectl get webapp` works under a Composition and fails under Helm — the four consequences of publishing an API versus templating a manifest

**Artifact** — a four-consequence table comparing Helm and a Crossplane Composition on mechanism, not preference: under a Composition, `kubectl get webapp` *works* — there is a live API object, a controller, a status, and one RBAC verb behind self-service; under Helm, `kubectl get webapp` simply fails, because a chart is client-side templating that produces a manifest and then forgets, and self-service needs the **union of every permission the chart applies**. The last consequence is the sharp one: Helm structurally cannot depend on state that does not exist yet, because it renders once.

**Rests on** — [the Crossplane Composition](15-crossplane-the-two-lines-that-size-your-pod.md), the "publishes an API" side of the contrast; [the drift beat](02-drift-detection-off-by-default.md), because "renders once versus reconciles" is the same axis seen at the delivery layer; and [P1](../../phases/01-operate-shallow.md), which owns chart *authoring* — this exercise is about Helm as an abstraction layer, not templating.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module's second question](../../phases/12-gitops-platform.md#m12-5), which frames the four consequences. This is a mechanism comparison you produce as a document, resting on the live Composition from [the previous exercise](15-crossplane-the-two-lines-that-size-your-pod.md).

> **Question to answer (Helm vs Composition, mechanism-level):** a chart is client-side templating that produces a manifest; a Composition publishes an API. State the four consequences — (1) drift: does a live controller correct a hand-edit, or does nothing? (2) does a live API object exist — does `kubectl get webapp` return something? (3) who can self-service — one RBAC verb, or the union of every permission the chart applies? (4) what each can express — the Composition can depend on state produced during reconciliation; Helm cannot, because it renders once, so it structurally cannot depend on state that does not exist yet.

**Do** — demonstrate each consequence side by side against the same intent (an app + config):

```sh
# the Composition side: a live API object exists
kubectl get webapp shop -n team-a          # returns an object, with a status
kubectl get webapp shop -n team-a -o jsonpath='{.status}'    # reconciliation reports back
# the Helm side: no such API object — the chart rendered and left
helm install shop2 ./webapp-chart -n team-a
kubectl get webapp shop2 -n team-a         # Error: the server doesn't have a resource type "webapp"
kubectl get deploy -n team-a               # the children exist; the abstraction does not
# self-service permission: Composition needs one verb; Helm needs everything the chart touches
kubectl create role webapp-user --verb=create --resource=webapps -n team-a   # one verb
```

**Verify from outside** — the table is checkable line by line: `kubectl get webapp` returning an object versus an error is the second consequence made concrete; the one-verb Role versus the chart's permission union is the third. A reader runs each command and gets the outcome the table claims, or the table is wrong.

**Expect** — the same developer intent served two ways, distinguished by whether an *API* was published or a *manifest* was rendered. The Composition has a name you can `get`, a controller that corrects drift, and a one-verb self-service surface; Helm has none of these, and cannot depend on state produced later because it runs once.

**Write down** — the four-consequence table (drift / live API object / who self-services / what each can express), each row backed by one of the commands above.

**Footprint note** — no new long-lived pods beyond [the Crossplane install already costed](15-crossplane-the-two-lines-that-size-your-pod.md); Helm is [0 in-cluster pods](../../research/platform-engineering-footprints.md). [`platform`](../../strands/lab-topologies.md#platform) is unmoved.

**Teardown** — `helm uninstall shop2`; keep the `webapp` Composition and its instance for [the capstone](18-the-platform-and-its-critique.md). **The topology stays.**
