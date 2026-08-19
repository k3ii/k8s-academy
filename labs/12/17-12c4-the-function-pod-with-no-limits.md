<a id="12c4-the-function-pod-with-no-limits"></a>
# 12.C4 — remove the `DeploymentRuntimeConfig` and let a `resources: {}` function pod run unbounded until something reclaims it

**Claim** — delete the `DeploymentRuntimeConfig` override and Crossplane's function pod returns to its default: `resources: {}` — BestEffort, no request, no limit — the exact hazard class that [ruled out Argo CD from this curriculum](../../research/platform-engineering-footprints.md), now on a pod you cannot avoid because functions are mandatory. Drive work through it and watch it grow unbounded until the node's memory pressure reclaims it, first among BestEffort pods. The platform you are building has the pod-sizing problem you spent [P8](../../phases/08-storage.md) learning to see — this drill is that thesis, executed.

**Rests on** — [the Crossplane exercise](15-crossplane-the-two-lines-that-size-your-pod.md), whose `DeploymentRuntimeConfig` override this removes; and [the build-track sizing rule](../../strands/build-mechanics.md#sizing), which says a memory request comes from measurement and a limit is a written-down decision — the discipline this drill shows the cost of skipping.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued — and this is [the single node](../../strands/lab-topologies.md#platform) where an unbounded pod is genuinely dangerous, which is the point.

**Read** — [the drill's chaos-table row](../../phases/12-gitops-platform.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand: omit the override and watch the default `resources: {}` bite.

**Do** — remove the override, confirm the pod is BestEffort again, and drive it:

```sh
kubectl delete deploymentruntimeconfig sized       # remove the sizing
kubectl delete pod -n crossplane-system -l pkg.crossplane.io/function   # let it respawn on the default
kubectl get pod -n crossplane-system -l pkg.crossplane.io/function -o \
  jsonpath='{.items[0].spec.containers[0].resources}{"\n"}'   # {} again — BestEffort
kubectl get pod -n crossplane-system -l pkg.crossplane.io/function -o \
  jsonpath='{.items[0].status.qosClass}{"\n"}'   # BestEffort
# drive compositions through it and watch RSS with no ceiling:
kubectl top pod -n crossplane-system -l pkg.crossplane.io/function --containers
```

**Observe** — the function pod's QoS class back to `BestEffort`, its RSS climbing with no limit to stop it, and — under node memory pressure — this pod first in line for the OOM killer precisely *because* it is BestEffort. The default that Crossplane ships is the failure; the `DeploymentRuntimeConfig` you removed was the only thing standing between a mandatory pod and unbounded growth.

**Expect** — a BestEffort pod that grows until the node reclaims it, on a node with no spare capacity to absorb it. If nothing reclaimed it, you did not drive enough work through it — the hazard is real even when it has not yet fired.

**Write down** — the function pod's QoS class with and without the override, and one sentence naming why a mandatory pod shipping `resources: {}` is a platform building a hazard into itself — the phase's thesis, in your own words, from your own cluster.

**Teardown** — **reapply the `DeploymentRuntimeConfig`** so [the capstone](18-the-platform-and-its-critique.md) runs on a sized function pod; confirm the QoS class returns to `Burstable`. **The topology stays.**
