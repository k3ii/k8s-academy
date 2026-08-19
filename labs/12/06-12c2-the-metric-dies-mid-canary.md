<a id="12c2-the-metric-dies-mid-canary"></a>
# 12.C2 — kill Prometheus in the middle of a canary and watch what a metric-gated system decides with no data

**Claim** — start a canary, then delete Prometheus mid-analysis, and Flagger must decide promotion with no metric to read. It does not promote into the void: with no data it holds or fails the canary rather than advancing, because "the SLO is satisfied" and "the SLO cannot be evaluated" are not the same, and a system that treated them the same would promote every broken release the moment its monitoring broke. The failure mode of a metric-gated system is the metric, and this is what that looks like.

**Rests on** — [the canary](05-a-canary-gated-on-a-metric.md), which must be mid-analysis for this to bite; and [P6's Prometheus](../../phases/06-kubelet-node.md), the thing being killed.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued, Istio + Prometheus still up from [the canary exercise](05-a-canary-gated-on-a-metric.md).

**Read** — [the drill's chaos-table row](../../phases/12-gitops-platform.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand: `kubectl delete` the metric source at the exact moment a decision depends on it.

**Do** — trigger a canary and delete Prometheus while the analysis window is open:

```sh
kubectl -n test set image deploy/podinfo podinfod=<good-new-tag>
kubectl -n test get canary/podinfo -w &     # watch the weight steps
sleep 20
kubectl -n monitoring delete deploy prometheus      # pull the data out from under it mid-canary
kubectl -n test describe canary/podinfo | tail -30  # what does it decide with no metric?
```

**Observe** — Flagger stalling or failing the canary rather than promoting, its events naming the metric it could not read. The weight does not advance on missing data. Restore Prometheus and the analysis resumes or the canary is already marked failed — either way, the absence of the metric was treated as *not a pass*, which is the safe default and the lesson.

**Expect** — a system that fails closed on missing telemetry, not open. If your canary promoted the instant Prometheus died, that is a real and dangerous finding about the configuration — record it, because it means the gate was advisory, not binding.

**Write down** — Flagger's decision with no data — promote, hold, or roll back — named exactly, and one sentence on why "cannot evaluate the SLO" must not mean "the SLO passed."

**Teardown** — restore Prometheus if you deleted rather than scaled it; the `Canary` is cleaned up with [its parent exercise](05-a-canary-gated-on-a-metric.md). **The topology stays.**
