<a id="the-platform-and-its-critique"></a>
# The capstone: a working platform a developer drives with one `create`, and the critique of it — which is the actual deliverable

**Artifact** — two things, and the second is the real one. First, a **working internal platform**: a developer commits a small manifest — "an app, a database, an ingress" — and your CRD + Crossplane Composition + Flux provisions it into a tenant namespace with `ResourceQuota` and `NetworkPolicy` enforced, storage from [the P8 CSI path](../../phases/08-storage.md#m8-4), and drift corrected automatically, the developer touching **no Kubernetes object directly**. Second, the **critique** — a written document naming what the abstraction hides, where it leaks, what a real developer would hate, and which of the eleven prior phases' skill it makes *unnecessary* versus merely *invisible*. The platform is the evidence; the critique is the deliverable, and it is the last thing the curriculum asks of you.

**Rests on** — the whole phase: [the delivery path](01-gitops-the-reconcile-loop-you-already-wrote.md), [the golden path](07-a-golden-path-with-no-portal.md), [the tenancy boundary](11-a-tenancy-boundary-and-where-it-leaks.md), [one vcluster tenant](12-the-same-pod-in-two-apiservers.md), [the Crossplane Composition and its sizing](15-crossplane-the-two-lines-that-size-your-pod.md); and the failure evidence from [the golden-path leak](09-12c5-the-leak-in-the-golden-path.md). It also rests on all eleven prior phases — the critique's final question is which of their skills your platform hides.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), a **lean co-resident set** only: Flux + KRO/Crossplane + one vcluster tenant, with **Istio, Prometheus and Flagger torn down** — the delivery-analysis stack is not needed to prove the platform works, and leaving it up would breach the node. Confirm you are running the lean set before you start.

**Read** — [the capstone framing](../../phases/12-gitops-platform.md#capstone) and [the gate's three conditions](../../phases/12-gitops-platform.md#gate). The citation discipline here is [the archaeology standard](../../strands/source-archaeology.md#drills) applied to the *tools'* own source: the drift-mode default, the Crossplane `mode` enum and empty runtime config, the vcluster syncer translation — each a `file:line` at a stated tag a hostile reader opens.

**Build** — the developer-side flow, end to end, from one committed manifest:

```sh
# the developer's entire interface — one small manifest, committed:
cat > checkout.yaml <<'YAML'
apiVersion: platform.example.com/v1
kind: WebApp
metadata: {name: checkout, namespace: team-a}
spec: {image: checkout:1.4.0, database: postgres, ingress: checkout.team-a.local}
YAML
git -C <repo> add checkout.yaml && git -C <repo> commit -m 'checkout' && git -C <repo> push
# from here the developer touches nothing else. Flux reconciles, the Composition provisions:
kubectl get webapp checkout -n team-a           # their one object, with a status
kubectl get deploy,svc,pvc,ingress -n team-a    # the children — the developer never wrote these
kubectl get resourcequota,networkpolicy -n team-a   # the boundary, enforced around them
```

**Verify from outside** — the gate is checkable against a hostile reader on three axes. **Works from the developer's side:** a fresh consumer provisions an app + database + ingress from one committed manifest and never runs `kubectl edit` on a Deployment — if they must, the abstraction failed. **Every mechanism claim cited:** the drift-mode default, the `mode` enum, the empty runtime config, the syncer translation, each `file:line@tag` a reader opens; "Crossplane composes it" fails, the citation passes. **The critique is honest:** it names a real leak (your [12.C5](09-12c5-the-leak-in-the-golden-path.md) evidence), a thing a developer would hate, and at least one prior-phase skill the platform makes *invisible* rather than *unnecessary*.

**Expect** — a platform that serves the developer who never needs to look, and a critique honest about the developer who *can't* look when it breaks. If the critique is "it's great," you built a platform and learned nothing — the critique is the phase, and its hardest line is the unnecessary-versus-invisible distinction, which is what separates a platform engineer from someone who writes CRDs.

**Write down** — the critique itself: what the abstraction hides correctly, where it leaks under load, what a real developer would hate, and the per-phase list of skills it makes unnecessary versus invisible. This is the deliverable the whole curriculum was built to reach.

**Footprint note** — the lean co-resident set (Flux + KRO/Crossplane + one vcluster + the app) sits well inside [the 6.0GB `platform` node](../../strands/lab-topologies.md#platform) with Istio/Prometheus/Flagger gone; this is why the capstone set is lean rather than everything Group A and B installed — [the arithmetic never allowed all of it at once](README.md).

**Teardown** — this is the end of the curriculum: delete the tenant, the platform components, and finally the topology — `just tofu labs destroy` on [`hopper`](../../strands/lab-topologies.md#teardown). **The topology goes, and the lab is finished.** [P0](../../phases/00-linux-primitives.md) built a container by hand and named `kubectl run nginx` as the target; [P11](../../phases/11-synthesis.md) traced that command to those exact syscalls; this phase hid all of it behind one `create`, and you have said, against your own work, what that costs the person who trusts it.
