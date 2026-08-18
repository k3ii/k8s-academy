<a id="a-hard-error-at-reserve"></a>
# Failing after the decision costs more than failing before it

**Claim** — a plugin that returns an error at `Reserve` fails the pod *after* filtering and scoring have both succeeded, so the cycle's work is wasted, every plugin that already reserved must be un-reserved, and the pod goes back to the queue with an attempt spent; a `Filter` rejection at the same rate costs a fraction of that. The asymmetry is declared in `interface.go` and it is measurable in the metrics.

**Rests on** — [your plugin](28-the-out-of-tree-plugin.md), which is the only way to fail on demand at a chosen extension point, and [the extension-point table](02-eleven-points-and-what-an-error-does.md), where you wrote down what an error at each point does. This is where that column is tested.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, plugin running as [stage 1](28-the-out-of-tree-plugin.md).

**Setup** — add two more arguments to the plugin, both defaulting off: `failReserveOnNode` (a node name), and reuse `rejectEverything` from [the build spec](28-the-out-of-tree-plugin.md). Implement `ReservePlugin` — both `Reserve` and `Unreserve` — and log a line in each, including the pod and node.

**Do**

1. **Predict from `interface.go` before running anything.** For a pod that fails at `Reserve` on the only node that fits, write down: how many nodes were filtered, how many were scored, which plugins' `Unreserve` runs, whether the pod is bound, which queue it lands in, and what the event says.

2. **Baseline.** Record the metrics that count work, then schedule ten pods normally:

   ```sh
   kubectl get --raw /metrics | grep -E 'scheduler_framework_extension_point_duration_seconds_count|scheduler_schedule_attempts_total' > /tmp/rsv-before.txt
   ```

3. **Fail at `Filter`.** Restart the plugin with `rejectEverything: true`, submit ten pods to your profile, and record the same metrics after 30 seconds.

4. **Fail at `Reserve`.** Restart with `rejectEverything: false` and `failReserveOnNode` set to the only node with capacity. Submit ten pods to your profile. Record again.

   ```sh
   kubectl get --raw /metrics | grep -E 'scheduler_framework_extension_point_duration_seconds_count|scheduler_schedule_attempts_total' > /tmp/rsv-after.txt
   diff /tmp/rsv-before.txt /tmp/rsv-after.txt
   ```

5. **Read your own log** for the `Unreserve` lines and confirm which plugins ran them — not just yours. Cross-check against [the default set](04-what-actually-runs-by-default.md): which of the default plugins registers at `Reserve`, and did its `Unreserve` run?

6. Answer the module's question from `interface.go` rather than from the metrics: **why is a `Reserve` failure costlier than a `Filter` rejection?** Three costs, at least; one of them is not about CPU at all but about what the scheduler's cache believed for the duration.

**Observe** — the extension-point counters in both failure modes. The counter is labelled by extension point, so the two runs produce visibly different distributions of work for the same number of failed pods.

**Expect** — the `Filter` run to increment the early extension points and nothing after them. The `Reserve` run increments **everything up to and including `Reserve`**, plus the `Unreserve` counter, for every attempt — and since the pod is retried on the ordinary backoff schedule, this repeats. Ten pods failing at `Reserve` do measurably more scheduler work than ten pods failing at `Filter`, and the ratio is roughly the ratio of the extension points involved.

Expect `Unreserve` to run on **every** plugin that implements it, not only on the one that failed, and expect that to be the interesting half of the answer to step 6: an extension point after which failure requires cooperation from components that did nothing wrong is structurally more expensive than one where failure is a return value.

Expect the pod's event to be less helpful than a `Filter` rejection's. A refusal names a plugin and counts nodes; an error at `Reserve` is an error, and errors do not carry node counts. Note that: **the further down the cycle a failure happens, the worse the diagnostics get**, which is an operational fact worth more than the metric.

**Write down** — your step-1 prediction scored against the run, the two metric distributions, the list of `Unreserve` implementations that ran, and the three costs from step 6 with the `interface.go` line for each.

**Footprint note** — twenty short-lived pause pods across two runs, all of which fail. Nothing new compiles: the plugin is rebuilt with two extra arguments, which is a warm link on the guest you already sized. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete pods -l app=rsv --ignore-not-found`, `rm /tmp/rsv-*.txt`, and set both arguments back off. **Rebuild and re-push the image with the two new arguments included** — [module 5.6](34-placement-that-differs-measurably.md) runs the image, not your working tree, and an argument that exists only on `forge` is an argument you cannot use there. **The topology stays.**
