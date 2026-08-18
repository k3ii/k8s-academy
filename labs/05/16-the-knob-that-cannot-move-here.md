<a id="the-knob-that-cannot-move-here"></a>
# `percentageOfNodesToScore` is provably inert on any cluster you can build here

**Claim** — the scheduler's headline scalability knob does nothing at all below a floor of node count that no lab topology reaches; you can prove that from `findNodesThatFitPod` and its helper before touching the cluster, and then set the knob to its most extreme value and watch placement not change. The finding is the arithmetic, not the demo.

**Rests on** — [the annotated cycle](12-one-pod-through-schedule-one.md), which is where "how many nodes get filtered" sits in the sequence. This is objective 5's falsifiable half; [the next exercise](17-a-hundred-nodes-that-do-not-exist.md) is where the knob is actually made to move.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. **Derive it first.** Find the function that decides how many nodes to bother with:

   ```sh
   grep -n 'func (sched \*Scheduler) numFeasibleNodesToFind\|percentageOfNodesToScore\|minFeasibleNodes' pkg/scheduler/schedule_one.go
   sed -n '/func (sched \*Scheduler) numFeasibleNodesToFind/,/^}/p' pkg/scheduler/schedule_one.go
   ```

   Write down three things: the early-return condition, the constant that floors the result, and the adaptive expression used when the percentage is left at its default. Then substitute your own node count into all three by hand and record the answer.

2. **Find the second floor.** The percentage itself has a minimum, applied after the adaptive calculation:

   ```sh
   grep -rn 'minFeasibleNodesPercentageToFind\|minFeasibleNodesToFind' pkg/scheduler/
   ```

3. **Now try to move it anyway.** `percentageOfNodesToScore` is a `KubeSchedulerConfiguration` field with no command-line equivalent, so this is also where you first configure the real scheduler by file. On `.130`:

   ```sh
   ssh zain@10.10.10.130
   sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /root/kube-scheduler.yaml.bak
   sudo tee /etc/kubernetes/sched-config.yaml >/dev/null <<'EOF'
   apiVersion: kubescheduler.config.k8s.io/v1
   kind: KubeSchedulerConfiguration
   clientConnection:
     kubeconfig: /etc/kubernetes/scheduler.conf
   leaderElection:
     leaderElect: true
   percentageOfNodesToScore: 1
   EOF
   ```

   Then edit the static pod manifest: add `- --config=/etc/kubernetes/sched-config.yaml`, **remove** the flags whose settings you have just moved into that file, and add the file to the container's volume mounts alongside the one already there for `scheduler.conf`.

   Before you save, write down the list of flags you removed with the config field each one became. That mapping is the exercise's second artifact and it is the thing you will need again at [exercise 31](31-a-profile-not-a-binary.md).

4. **Confirm it took**, which is the step people skip and then debug for an hour:

   ```sh
   kubectl -n kube-system get pod -l component=kube-scheduler -o yaml | grep -A6 'command:'
   kubectl -n kube-system logs -l component=kube-scheduler --tail=20
   ```

5. **Look for a difference.** Schedule twenty pods and record placement; then set `percentageOfNodesToScore: 100`, wait for the restart, delete and re-create them, and record placement again.

**Observe** — the two placement distributions, and whether the scheduler logged anything at all about the knob.

**Expect** — identical distributions, and the reason is the early return you derived in step 1: below the floor, the function returns the total node count regardless of the percentage. **The knob is not merely ineffective at two nodes; it is unreachable.** A cluster would need node counts in the hundreds before the value has any effect, and the adaptive default means it stays gentle for a long way past that.

Expect step 3 to be more interesting than step 5, and that is the honest shape of this exercise: the configuration surgery you do here is a prerequisite for [the plugin's profile](31-a-profile-not-a-binary.md), and the measurement is a negative result you predicted in advance.

**Write down** — the three components of the formula with `file:line`, your substitution for two nodes, the flag-to-config mapping table, and one sentence stating what cluster size the knob would first bite at.

**Footprint note — this is the phase's one planned lab that does not fit, flagged rather than softened.** [The module](../../phases/05-scheduler.md#m5-3) wants this knob measured on a full topology. It cannot be: [`workhorse` is three nodes](../../strands/lab-topologies.md#workhorse), the floor is two orders of magnitude above that, and no arrangement of [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling) reaches it — a hundred VMs is not a rounding error away, it is a different building.

**The smallest change is not a bigger cluster, it is fake nodes**, and upstream already ships them: the scheduler's own performance harness constructs node objects in an integration environment, with no kubelet and no VM behind any of them. That is [exercise 17](17-a-hundred-nodes-that-do-not-exist.md), it costs one `forge` and no topology, and it is the only place in this phase where the knob's number changes anything. Two alternatives were rejected: `kwok` (new tooling for one measurement, and nothing else in the curriculum uses it), and simply asserting the upstream benchmark numbers (which is reading a table, not running a lab).

**Teardown** — leave the `--config` plumbing in place; [exercise 31](31-a-profile-not-a-binary.md) extends this same file, and `/root/kube-scheduler.yaml.bak` is the way back to a flags-only scheduler if the profile work goes wrong. Set `percentageOfNodesToScore` back to `0` (the adaptive default) so nothing downstream is measured against a hand-set value. `kubectl -n sched-lab delete deployment --all`. **The topology stays.**
