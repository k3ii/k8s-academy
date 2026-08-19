<a id="a-canary-gated-on-a-metric"></a>
# A rollout that promotes only if a metric holds and rolls itself back if it does not — the P1 rollout seen from the other end, ten months on

**Artifact** — a Flagger `Canary` that shifts traffic to a new version in weighted steps, promotes it only while a Prometheus SLO query stays inside threshold, and **rolls back automatically** on a breach — no human, no `kubectl rollout undo`; plus a two-line contrast naming what this can express that [P1's `maxSurge`/`maxUnavailable`](../../phases/01-operate-shallow.md) structurally cannot. It is the same operation — replace pods gradually — but one is blind to whether the new pods are *healthy by your definition* and one is not.

**Rests on** — [P1's blunt rollout](../../phases/01-operate-shallow.md), the same operation seen ten months earlier from the naive end; [P9's mesh](../../phases/09-service-mesh.md#m9-2), which Flagger drives to split traffic — cut P9 and this degrades or is cut with it; and [P6's Prometheus](../../phases/06-kubelet-node.md), reused as the metric source.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued — but this exercise installs the heavy half of Group A: Istio (the [P9](../../phases/09-service-mesh.md) pattern) and Prometheus (the [P6](../../phases/06-kubelet-node.md) one), together [~1.15GB](../../research/platform-engineering-footprints.md). This is the pair that [the group teardown](10-the-teardown-that-proves-git.md) exists to reclaim before Group B.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-2) and the source question below. The mesh mechanics are [P9's](../../phases/09-service-mesh.md) and are not restated; this exercise is about the *gate*, not the traffic split.

> **Question to answer from observation and source:** which metric query gates the promotion, and where does Flagger read it? Then contrast the blast radius with [P1's `maxSurge`/`maxUnavailable`](../../phases/01-operate-shallow.md): both "replace pods gradually," but one can express *only* "how many pods at once" and the other can express "advance only while this SLO holds." State the exact difference in what each can say.

**Build** — deploy `podinfo` + loadtester under a `Canary` gated on a request-success-rate SLO, trigger a canary, then ship a version that violates the SLO:

```sh
kubectl apply -f podinfo-canary.yaml     # Canary: stepWeight, threshold, metric = request-success-rate
kubectl -n test set image deploy/podinfo podinfod=<good-new-tag>
kubectl -n test describe canary/podinfo   # watch weight step: 10, 20, 30... as the SLO holds
# now break the SLO and watch the rollback happen with no human:
kubectl -n test set image deploy/podinfo podinfod=<bad-tag-that-500s>
kubectl -n test get canary/podinfo -w      # Progressing -> Failed, weight returns to 0
```

**Verify from outside** — the rollback is observable without trusting Flagger's own status: the Service's endpoints return to the primary, and `kubectl rollout history` shows no manual `undo` was issued — the decision was the controller's, driven by the metric. "Flagger rolled it back" fails; the metric query that gated it, cited to where Flagger reads it, plus the endpoint shift, passes.

**Expect** — traffic stepping up while the SLO holds, and on the bad version the weight returning to zero on its own within the analysis window. The failure of a metric-gated system is the metric — which is exactly what [the next drill](06-12c2-the-metric-dies-mid-canary.md) attacks.

**Write down** — the canary's metric query and its promotion/rollback thresholds, and the two-line contrast with the P1 rollout naming what Flagger can express that `maxSurge` cannot.

**Footprint note** — Flagger itself is [4 pods idle / 6 mid-canary, ~224Mi](../../research/platform-engineering-footprints.md); the weight sits in Istio + Prometheus at [~1.15GB](../../research/platform-engineering-footprints.md), which is why Group A does not co-reside with Group B.

**Teardown** — the `Canary` and `podinfo` go; Istio and Prometheus **stay** for [12.C2](06-12c2-the-metric-dies-mid-canary.md), then are torn down at [the group boundary](10-the-teardown-that-proves-git.md). **The topology stays.**
