<a id="the-same-pod-in-two-apiservers"></a>
# One pod, pointed at twice: a tenant pod in a virtual apiserver and a real pod in a host namespace — and the syncer limit dropped from 4Gi to ~1Gi first

**Artifact** — the *same* pod shown in two apiservers at once: as a tenant pod inside a vcluster's virtual apiserver, and as a real pod in a host namespace on [the P5 host scheduler](../../phases/05-scheduler.md#m5-1) — with the host namespace named and the component that is real (the container) told apart from the component that is a shim (the tenant's apiserver view); plus the syncer's measured idle RSS from `kubectl top pod`, and its memory limit deliberately dropped from the chart's 4Gi to ~1Gi. The first step is a measurement, because the whole module rests on a number vcluster does not publish.

**Rests on** — [the namespace boundary and its leaks](11-a-tenancy-boundary-and-where-it-leaks.md), which vcluster is the stronger answer to; [P5's host scheduler](../../phases/05-scheduler.md#m5-1), which schedules the "real" half; and [P3's apiserver](../../phases/03-api-machinery.md), because a vcluster ships its own.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-4) and the source question below, plus [the maturity note](../../phases/12-gitops-platform.md#ecosystem): vcluster is **not a CNCF project**, and its chart's default image is the commercial build, so `repository: loft-sh/vcluster-oss` is an explicit lab choice, not a default absorbed silently.

> **Question to answer from the source and the cluster:** the vcluster syncer is a `kube-apiserver` + `kube-controller-manager` + kine/SQLite in **one Go process** — which half of a tenant pod is real (the container, on the host, scheduled by [the P5 host scheduler](../../phases/05-scheduler.md#m5-1)) and which is a shim (the tenant's apiserver view)? Point at the pod in both apiservers. And: what does the 4Gi→1Gi limit convert unbounded growth *into*, and why is that OOMKill the better failure?

**Build — measure first, then place the same pod on both sides:**

```sh
# 1. install one tenant, OSS image, limit dropped from the chart's 4Gi to ~1Gi:
vcluster create vcluster-a -n vcluster-a \
  --set 'controlPlane.statefulSet.image.repository=loft-sh/vcluster-oss' \
  --set 'controlPlane.statefulSet.resources.limits.memory=1Gi'
# 2. THE FIRST REAL STEP — the number the module rests on:
kubectl top pod -n vcluster-a       # the syncer's idle RSS, not its 256Mi request
# 3. create a pod INSIDE the tenant:
vcluster connect vcluster-a -- kubectl run app --image=nginx --restart=Never
# 4. the same pod, twice:
vcluster connect vcluster-a -- kubectl get pod app -o wide   # tenant view: the virtual apiserver
kubectl get pod -n vcluster-a -o wide | grep app             # host view: a real pod, real node
```

**Verify from outside** — the "same pod" claim is two `get` outputs sharing a container ID and a node: the tenant apiserver names it `app`, the host apiserver names it with a syncer-mangled name in the `vcluster-a` namespace, and both point at one container on one node. "vcluster gives each tenant a cluster" fails the gate; the single host pod backing the tenant's view passes. If a single tenant idles above ~600Mi on the `top pod` reading, drop to one tenant plus a written walkthrough of the second — [the arithmetic says so](../../research/platform-engineering-footprints.md).

**Expect** — one container, two apiserver views; the container real and host-scheduled, the tenant's control plane a shim in a single Go process. The 4Gi→1Gi limit converts an unbounded-growth risk into a clean OOMKill on one tenant — a better, cheaper failure than a node slowly starved.

**Write down** — the same tenant pod shown in both apiservers with the host namespace named; the `top pod` number the module rests on; and one line on what the limit drop converts unbounded growth into.

**Footprint note** — vcluster is [~640Mi and a PVC for two tenants, but the chart's default 4Gi limit is a 16× tell](../../research/platform-engineering-footprints.md) that 256Mi is not the working set — hence the measure-first, limit-drop discipline on [the single `platform` node](../../strands/lab-topologies.md#platform). Anything needing a *second real cluster* is [out of scope by #8](../../research/platform-engineering-footprints.md) — vcluster is deliberately the single-node answer to that, not a second node.

**Teardown** — [12.C3](13-12c3-the-syncer-dies-the-host-pods-live.md) breaks this same syncer next, so keep `vcluster-a` for now; delete the in-tenant `app` pod. **The topology stays.**
