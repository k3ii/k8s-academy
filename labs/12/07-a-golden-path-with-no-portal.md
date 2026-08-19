<a id="a-golden-path-with-no-portal"></a>
# A developer opens a pull request and gets an app — a golden path built from a template repo, a CRD, and Flux, with no portal anywhere in it

**Artifact** — a working golden path with **no portal**: a template repo a developer copies, a [P4](../../phases/04-controllers.md) CRD they fill in one instance of, and Flux reconciling it into a running app — so "I want an app" becomes a pull request and the pull request becomes a deployment, with nothing a human has to click. The claim to test is that the whole self-service loop is three things you already have, not a product you install.

**Rests on** — [the Flux delivery path](01-gitops-the-reconcile-loop-you-already-wrote.md), which reconciles the CRD instance; and [P4's CRD-plus-controller](../../phases/04-controllers.md#m4-1), which is the "one kind the developer fills in."

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-3), the judgement module. This exercise builds the path; [reading Backstage](08-backstage-read-never-installed.md) is where the contrast that gives it meaning lives.

**Build** — a template repo, a CRD the developer instantiates, and Flux wiring the instance to a real app:

```sh
# the developer's whole interface: copy the template, edit one file, open a PR
# template repo holds: an <App> CR instance + a Kustomization that Flux already watches
cat > my-app.yaml <<'YAML'
apiVersion: platform.example.com/v1
kind: App
metadata: {name: checkout, namespace: team-a}
spec: {image: checkout:1.4.0, replicas: 2, port: 8080}
YAML
# a PR merging this is the entire developer action; the controller + Flux do the rest
kubectl get app checkout -n team-a
kubectl get deploy,svc -n team-a -l app=checkout   # emitted by the controller, not written by the developer
```

**Verify from outside** — hand the template repo to a fresh consumer (or your past self) and time them from clone to running app. If they had to touch a `Deployment`, a `Service`, or a `kubectl apply`, the golden path leaked its implementation and is not one. One edited file and one merged PR is the pass condition.

**Expect** — a developer who names an app and gets an app, having seen one CRD instance and no Kubernetes primitive. This is the platform-as-product claim made concrete, and it is [the capstone](18-the-platform-and-its-critique.md) in miniature — the capstone adds a database, ingress, and a tenant boundary to the same shape.

**Write down** — the golden path as it exists (template repo + CRD + Flux), and the one developer action that drives it. This is one input to [the failure-mode catalogue](09-12c5-the-leak-in-the-golden-path.md).

**Footprint note** — the controller is one small [P4](../../phases/04-controllers.md#m4-1)-style Deployment; no measurable addition to [`platform`](../../strands/lab-topologies.md#platform) beyond the app it emits.

**Teardown** — delete the `App` instance and let Flux prune what it emitted; the CRD and controller **stay** for [the leak drill](09-12c5-the-leak-in-the-golden-path.md) and [the capstone](18-the-platform-and-its-critique.md). **The topology stays.**
