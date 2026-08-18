<a id="oom-score-adj-from-the-formula"></a>
# Compute the number the kernel will use, then read it out of /proc

**Claim** — the kubelet translates QoS class into a single integer per container, and for Burstable pods that integer is a function of the pod's memory request and the node's capacity — so two Burstable pods on the same node get **different** scores, and you can predict both to the digit before looking.

**Rests on** — [the five classifications](06-three-pods-three-classes.md). The class is the input to this formula; without it the numbers are unreadable.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The pods must run on the worker `.131` — the formula divides by *that node's* capacity, and using the control plane would change the answer.

**Read** — `pkg/kubelet/qos/policy.go`. It is tiny. Extract three things with `file:line`: the constant for Guaranteed, the constant for BestEffort, and the expression for Burstable including its clamps. Then answer [module 6.2's second question](../../phases/06-kubelet-node.md#m6-2) — why those values make the kernel choose BestEffort first — from the [`oom_score`/`oom_score_adj` arithmetic you met in P0](../../phases/00-linux-primitives.md), not from the comment.

Also find out which process the kubelet does **not** apply this to, and what it uses instead for the sandbox. `grep -rn 'oom' ~/src/kubernetes/pkg/kubelet/kuberuntime/ | grep -i score` is the entry.

**Do**

1. Get the node's memory capacity — the denominator:

   ```sh
   kubectl get node pair-worker -o jsonpath='{.status.capacity.memory}{"\n"}'
   ```

2. **Compute four numbers on paper**: one Guaranteed, one BestEffort, and two Burstable pods whose memory requests differ by a factor of four. Then create exactly those:

   ```sh
   kubectl create ns oom-score
   for spec in "g 128Mi 128Mi" "b1 128Mi 512Mi" "b2 512Mi 1Gi"; do
     set -- $spec
     kubectl -n oom-score apply -f - <<EOF2
   apiVersion: v1
   kind: Pod
   metadata: {name: $1}
   spec:
     nodeName: pair-worker
     containers:
     - name: c
       image: registry.k8s.io/pause:3.10
       resources: {requests: {memory: $2}, limits: {memory: $3}}
   EOF2
   done
   kubectl -n oom-score run be --image=registry.k8s.io/pause:3.10 --restart=Never --overrides='{"spec":{"nodeName":"pair-worker"}}'
   ```

3. Read the truth off the node:

   ```sh
   ssh zain@10.10.10.131 'for p in $(sudo crictl ps -q); do
       pid=$(sudo crictl inspect $p | jq -r .info.pid)
       name=$(sudo crictl inspect $p | jq -r .status.metadata.name)
       printf "%-12s pid=%-7s oom_score_adj=%-6s oom_score=%s\n" "$name" "$pid" \
         "$(cat /proc/$pid/oom_score_adj)" "$(cat /proc/$pid/oom_score)"
     done'
   ```

**Observe** — also read the sandbox processes' values, not only the application containers':

```sh
ssh zain@10.10.10.131 'for s in $(sudo crictl pods -q); do
    pid=$(sudo crictl inspectp $s | jq -r .info.pid)
    printf "sandbox pid=%-7s adj=%s\n" "$pid" "$(cat /proc/$pid/oom_score_adj)"
  done'
```

**Expect** — your four predictions to match, with the two Burstable pods landing on visibly different values in the same direction as their requests: a larger request buys a *lower* score and therefore more protection, which is the whole design and the reason "just set requests" is real advice rather than paperwork.

Expect the sandboxes to be protected far more strongly than the workloads they hold. That asymmetry is deliberate — killing a sandbox destroys the pod's network namespace and the containers inside it become unreachable orphans, so the kernel is steered away from the one process whose death is unrecoverable.

Expect `oom_score` (the effective badness, which includes current usage) to differ from `oom_score_adj` (the constant offset). Only the second one is what `policy.go` sets; conflating them is the commonest mistake in OOM post-mortems, and [drill 6.C3](09-6c3-who-killed-the-pod.md) reads both out of a real kill.

**Write down** — the four predictions, the four observed values, the `policy.go:line` for each of the three cases, and the sandbox's value with one sentence on why it is not on the same scale. This is [the phase's 6.2 write-down](../../phases/06-kubelet-node.md#checklist).

**Footprint note** — the *requests* here total 1.25Gi on a 2048MB worker, which is deliberate: `pause` pods consume almost nothing, so this is the phase's cheapest demonstration that the scheduler's arithmetic and the node's actual usage are unrelated numbers. If a pod stays `Pending`, you have just re-derived [P5's `Insufficient memory`](../../phases/05-scheduler.md#m5-3) — lower `b2`'s request rather than growing the node.

**Teardown** — `kubectl delete ns oom-score`. **The topology stays** — [the Chaos Mesh install](08-chaos-mesh-at-582mi.md) is next, and it needs the worker's memory picture unchanged.
