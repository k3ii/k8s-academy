<a id="b04"></a>
# B4 — Three Helm installs, then one Kustomize overlay on top

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / Helm and Kustomize

> **This build is a dependency, not a lesson.** It installs metrics-server, a Gateway controller and MetalLB, and until it has run, **W10**, **N7** and **N13** have nothing to drill against. That is why [the plan](../../plan.md#calendar) puts it on the first weeknight of week 2 rather than in weight order.

**Do**

1. **metrics-server**, from its own chart repo. On a kubeadm cluster the kubelet serves a self-signed certificate that metrics-server will not trust, so the install fails closed and the Deployment sits `0/1` with a healthy-looking log. Pass `--kubelet-insecure-tls` and know *why* you are passing it — this is the single most common "`kubectl top` is broken" cause, and **TS10** drills it from the other end.
2. **Gateway API CRDs, then a controller.** The CRDs are **not** part of the controller's chart: install the standard channel first, confirm `kubectl get crd | grep gateway.networking.k8s.io`, and only then `helm install` the controller. A controller installed against absent CRDs produces a crash loop that reads like a controller bug.
3. **MetalLB**, in L2 mode, with an `IPAddressPool` and an `L2Advertisement`. Use `10.10.10.200-10.10.10.209`, inside the range [`lab-topologies`](../../../strands/lab-topologies.md#addresses) reserves for MetalLB. **That reservation is prose only** — nothing in `tofu` enforces it — so confirm the range is idle before you claim it.
4. **One Kustomize overlay.** Take the simplest of the three releases, `kustomize build` a two-file overlay that patches one field, and apply it. The point is to have driven both tools in one sitting and be able to say which problem each solves: Helm templates *before* the API server sees anything, Kustomize patches *structured YAML*.

**Observe**

```sh
helm list -A
kubectl get crd | grep gateway.networking.k8s.io
kubectl -n metallb-system get ipaddresspool,l2advertisement
kubectl top nodes
kubectl kustomize overlays/dev | head -40
```

**Done when** — `kubectl top nodes` returns numbers, a `Service` of type `LoadBalancer` gets an address out of the pool rather than sitting `<pending>`, a `Gateway` reports `PROGRAMMED=True`, and the overlay's patched field is live in the cluster.

**Done in one sitting.** A Build is not worked three times. If it overruns, finish the metrics-server and MetalLB legs — they are what unlock three Pinned drills — and carry the Gateway controller into the next night.

**Teardown** — none. All three installs are **permanent fixtures** of `pair` for the rest of the sprint, and every topology switch in [the plan](../../plan.md#topology) destroys them. Reinstalling after a switch is part of the switch, not a new build.

**See also** — [the baseline](../../baseline.md#versions) for what was already on this cluster before any of this, and **B5**, which installs a CRD and its operator by hand so that step 2's chart stops being magic.
