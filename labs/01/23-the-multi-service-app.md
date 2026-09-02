<a id="the-multi-service-app"></a>
# The capstone chart: three services, one helm install, reachable in a browser

**Artifact** — a frontend, a backend and a datastore, deployed by one `helm install`, exposed through MetalLB, and open in a browser on the Mac. **This is [the capstone's first half](../../phases/01-operate-shallow.md#capstone) and [a gate condition](../../phases/01-operate-shallow.md#gate).**

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with MetalLB and ingress-nginx from [the exposure exercise](14-four-ways-to-expose.md) still installed.

**Build**

Grow `build/01-chart/` from [the chart exercise](19-author-a-helm-chart.md). Do not start a new chart. The chart must gain six things.

1. **Three workloads that actually talk to each other.** The frontend must reach the backend by Service name, and the backend must reach the datastore by Service name. A DNS failure or a selector typo is then visible as a broken page, and not as a healthy-looking cluster. Anything real enough to fail will do. A static frontend that calls a small API, which calls Redis or Postgres, is plenty.
2. **A ServiceAccount for each workload.** Set `automountServiceAccountToken: false` unless the workload needs the API, and none of these three workloads does. Write a comment that says why the default is the wrong default here.
3. **Probes on all three workloads.** The readiness probe of the datastore must test the datastore. It must not test that a port is open.
4. **Requests and limits on all three workloads.** Choose the values against the [worker's remaining headroom](../../strands/lab-topologies.md#pair), and do not copy them from a blog. Sum the values before you apply them. Then check the arithmetic against what MetalLB, ingress-nginx and the CNI already use.
5. **The datastore as the subchart dependency.** Requirement 3 of [the chart exercise](19-author-a-helm-chart.md) is then satisfied by something load-bearing, and not by a demo.
6. **One Ingress, host-based, that routes to the frontend only.** The backend and the datastore must have no route in from outside. Verify that, and do not assume it.

**Verify**

```sh
helm install app build/01-chart --wait --timeout 5m
kubectl get pods,svc,ingress
kubectl get svc -n ingress-nginx        # the VIP
```

Then open the application on the Mac with [the browser forward](../../strands/lab-topologies.md#access), pointed at that VIP.

Then verify the negative case. From a pod outside the namespace of the release, try to reach the Service of the datastore. Then try to reach it through the Ingress VIP, with a crafted `Host` header.

**Gate** — five conditions must hold. One command installs the application. `--wait` returns and does not time out. The page loads in a real browser on the Mac, and it shows data that came through all three tiers. The datastore is unreachable from outside. `helm uninstall` removes everything — check for leftovers with `kubectl get all -l app.kubernetes.io/instance=app`.

**Expect** — `--wait` is the honest test, and it is the test that fails first. The usual cause is an ordering problem. The readiness probe of the backend passes before the datastore accepts connections, so the frontend renders an error page while every pod is `Ready`. Kubernetes does not provide startup ordering. Discovering that here, with three pods and a browser, is much cheaper than discovering it later. The fix is a readiness probe that tests the dependency. The fix is not an init container that waits.

**Write down** — three things. The resource arithmetic from requirement 4, as requested values against the allocatable capacity of the node. A screenshot, or the rendered output of the page. One sentence on the startup-ordering failure, and on how you fixed it.

**Footprint note** — three application pods plus a datastore, on top of MetalLB, ingress-nginx and Flannel, is the peak of the phase. That peak lands on the 2048MB worker of `pair`. If the datastore is Postgres rather than Redis, check `kubectl top nodes` before you add replicas. The smallest change that buys room is to scale `deploy/web` and the leftovers from earlier exercises to zero. You should have done that at each teardown anyway.

**Teardown** — leave the release installed, and leave the cluster up. [The incident note](24-the-incident-note.md) is written next, and it ends the phase's cluster.
