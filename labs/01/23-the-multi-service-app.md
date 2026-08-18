<a id="the-multi-service-app"></a>
# The capstone chart: three services, one helm install, reachable in a browser

**Artifact** — a frontend, a backend and a datastore deployed by one `helm install`, exposed through MetalLB, and open in a browser on the Mac. **This is [the capstone's first half](../../phases/01-operate-shallow.md#capstone) and [a gate condition](../../phases/01-operate-shallow.md#gate).**

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with MetalLB and ingress-nginx from [the exposure exercise](14-four-ways-to-expose.md) still installed.

**Build**

Grow `build/01-chart/` from [the chart exercise](19-author-a-helm-chart.md) — do not start a new chart. What it must gain:

1. **Three workloads that actually talk to each other.** The frontend must reach the backend by Service name and the backend must reach the datastore by Service name, so a DNS failure or a selector typo is visible as a broken page rather than as a healthy-looking cluster. Anything real enough to fail: a static frontend calling a small API calling Redis or Postgres is plenty.
2. **A ServiceAccount per workload**, each with `automountServiceAccountToken: false` unless the workload needs the API — and none of these do. Say in a comment why the default is the wrong default.
3. **Probes on all three**, with the datastore's readiness probe actually testing the datastore rather than testing that a port is open.
4. **Requests and limits on all three**, chosen against the [worker's remaining headroom](../../strands/lab-topologies.md#pair) rather than by copying a blog. Sum them before applying and check the arithmetic against what MetalLB, ingress-nginx and the CNI are already using.
5. **The datastore as the subchart dependency**, so requirement 3 of [the chart exercise](19-author-a-helm-chart.md) is satisfied by something load-bearing rather than by a demo.
6. **One Ingress**, host-based, routing to the frontend only. The backend and datastore must have no route in from outside, and you should verify that rather than assume it.

**Verify**

```sh
helm install app build/01-chart --wait --timeout 5m
kubectl get pods,svc,ingress
kubectl get svc -n ingress-nginx        # the VIP
```

Then open it on the Mac with [the browser forward](../../strands/lab-topologies.md#access), pointed at that VIP.

Then verify the negative: from a pod outside the release's namespace, try to reach the datastore's Service. Then try to reach it through the Ingress VIP with a crafted `Host` header.

**Gate** — one command installs it; `--wait` returns without timing out; the page loads in a real browser on the Mac and shows data that came through all three tiers; the datastore is unreachable from outside; `helm uninstall` removes everything (check for leftovers with `kubectl get all -l app.kubernetes.io/instance=app`).

**Expect** — `--wait` is the honest test and it is the one that fails first, usually because the backend's readiness probe passes before the datastore is accepting connections and the frontend renders an error page while every pod is `Ready`. Startup ordering is not something Kubernetes provides, and discovering that here — with three pods and a browser — is much cheaper than discovering it later. The fix is a readiness probe that tests the dependency, not an init container that waits.

**Write down** — the resource arithmetic from requirement 4 (requested versus the node's allocatable), a screenshot or the page's rendered output, and one sentence on the startup-ordering failure and how you fixed it.

**Footprint note** — three application pods plus a datastore on top of MetalLB, ingress-nginx and Flannel is the phase's peak, and it lands on `pair`'s 2048MB worker. If the datastore is Postgres rather than Redis, check `kubectl top nodes` before adding replicas — the smallest change that buys room is scaling `deploy/web` and the leftovers from earlier exercises to zero, which you should have done at each teardown anyway.

**Teardown** — leave the release installed and the cluster up. [The incident note](24-the-incident-note.md) is written next and ends the phase's cluster.
